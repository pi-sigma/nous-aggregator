import json
import logging

from celery import group, shared_task
from django.db.utils import DatabaseError
from django.utils import timezone

import scraper
from config.scraper import tasks as scraper_tasks

from .models import Article, Source

logger = logging.getLogger("__name__")


@shared_task
def get_articles_for_source(source_title: str) -> None:
    source: Source = Source.objects.get(title=source_title)
    sitemap = source.to_dict()
    starting_urls = [
        sitemap["base_url"] + path for path in sitemap["paths"]
    ]

    spider = scraper.Spider(starting_urls, sitemap)
    spider.run()
    articles = [json.loads(article) for article in spider.articles]

    # try bulk create, revert to individual db saves in case of error
    try:
        Article.objects.bulk_create([
            Article(
                headline=article_data["headline"],
                slug=article_data["slug"],
                source=Source.objects.get(url=article_data["source_link"]),
                summary=article_data["summary"],
                language=article_data["language"],
                url=article_data["url"],
                created_at=timezone.now(),
            ) for article_data in articles
        ], ignore_conflicts=True)
    except DatabaseError as exc:
        logger.error("Bulk create failed", exc_info=exc)
        for article_data in articles:
            try:
                Article.objects.create(
                    headline=article_data["headline"],
                    slug=article_data["slug"],
                    source=Source.objects.get(url=article_data["source_link"]),
                    summary=article_data["summary"],
                    language=article_data["language"],
                    url=article_data["url"],
                    created_at=timezone.now(),
                )
            except DatabaseError as exc:
                logger.error("DB save failed for %s", article_data["url"], exc_info=exc)


@shared_task
def get_articles(language: str):
    task_group = group(
        get_articles_for_source.s(source_title=title) for title in scraper_tasks["magazines"][language]["titles"]
    )
    promise = task_group.apply_async()
    if promise.ready():
        return promise.get()
