import json

from celery import group, shared_task
from django.utils import timezone

import scraper
from scraper.tasks import magazines

from .models import Article, Source


@shared_task
def get_articles_for_source(source_title: str):
    source: Source = Source.objects.get(name=source_title)
    sitemap = source.to_dict()
    starting_urls = [
        sitemap["base_url"] + path for path in sitemap["paths"]
    ]

    spider = scraper.Spider(starting_urls, sitemap)
    scraper.run(spider)
    data = [json.loads(article) for article in spider.articles]

    Article.objects.bulk_create([
        Article(
            headline=article_data["headline"],
            slug=article_data["slug"],
            source=Source.objects.get(link=article_data["source_link"]),
            summary=article_data["summary"],
            language=article_data["language"],
            link=article_data["link"],
            created_at=timezone.now(),
        ) for article_data in data
    ], ignore_conflicts=True)


@shared_task
def get_articles(language: str):
    task_group = group(
        get_articles_for_source.s(source_title=title) for title in magazines[language]["titles"]
    )
    promise = task_group.apply_async()
    if promise.ready():
        return promise.get()
