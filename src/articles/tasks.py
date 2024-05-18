import json
import logging
from typing import Optional

from celery import group, shared_task
from django.db.utils import DatabaseError
from django.utils import timezone

import rss
import scraper

from .models import Article, Source

logger = logging.getLogger("__name__")


def create_articles(article_data: list[dict], source: Source) -> None:
    """
    Try bulk create, revert to individual DB saves in case of error
    """
    try:
        Article.objects.bulk_create([
            Article(
                title=article["title"],
                slug=article["slug"],
                source=source,
                description=article["description"],
                language=article["language"],
                url=article["url"],
                created_at=article.get("pubdate") or timezone.now(),
            ) for article in article_data
        ], ignore_conflicts=True)
    except DatabaseError as exc:
        logger.error("Bulk create failed", exc_info=exc)
        for article in article_data:
            try:
                Article.objects.create(
                    title=article["title"],
                    slug=article["slug"],
                    source=source,
                    description=article["description"],
                    language=article["language"],
                    url=article["url"],
                    created_at=article.get("pubdate") or timezone.now(),
                )
            except DatabaseError as exc:
                logger.error("DB save failed for %s", article["url"], exc_info=exc)


@shared_task
def get_feed_articles_for_source(source_title: str, time_delta: int):
    source: Source = Source.objects.get(title=source_title)
    reader = rss.Reader(feeds=source.feeds, time_delta=time_delta)

    reader.get_feed()
    article_data = [item for item in reader.articles]

    create_articles(article_data, source)


@shared_task
def scrape_articles_from_source(source_title: str):
    source: Source = Source.objects.get(title=source_title)
    sitemap = source.sitemap.to_dict()
    starting_urls = [
        sitemap["base_url"] + path for path in sitemap["paths"]
    ]

    spider = scraper.Spider(starting_urls, sitemap)
    spider.run()
    article_data = [json.loads(article) for article in spider.articles]

    create_articles(article_data, source)


@shared_task
def get_articles(language: str, titles: list, time_delta: Optional[int] = None):
    """Retrieve articles from RSS feed or by scraping, depending on `time_delta`

    Args:
        language: the language of the articles
        titles: the titles of the article sources
        time_delta: max age (unit agnostic) of the target articles; if specified, articles
            are retrieved from feed, otherwise scraped
    """
    if time_delta:
        task_group = group(
            get_feed_articles_for_source.s(source_title=title, time_delta=time_delta)
            for title in titles
        )
    else:
        task_group = group(
            scrape_articles_from_source.s(source_title=title) for title in titles
        )

    promise = task_group.apply_async()
    if promise.ready():
        return promise.get()
