import json
import logging
from datetime import datetime

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.utils.timezone import make_aware
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJob, DjangoJobExecution

from articles.models import Article, Source
from articles.scraper.spider import Spider

logger = logging.getLogger(__name__)

SCRAPING_INTERVAL = 1  # minutes


def scrape(sitemap: dict):
    Spider.crawl(sitemap)
    data = [json.loads(article) for article in Spider.articles]

    for article_data in data:
        article = Article(
            headline=article_data["headline"],
            slug=article_data["slug"],
            source=Source.objects.get(link=article_data["source_link"]),
            summary=article_data["summary"],
            language=article_data["language"],
            link=article_data["link"],
            created_at=make_aware(datetime.now()),
        )
        try:
            article.save()
        except IntegrityError as e:
            logger.info(
                "Article (%s) already exists in database (%s)",
                article_data["headline"],
                e,
            )


def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(
            timezone=settings.TIME_ZONE,
            executors={"default": ThreadPoolExecutor(1)},
        )
        scheduler.add_jobstore(DjangoJobStore(), "default")

        sources = Source.objects.all()
        for index, source in enumerate(sources):
            source_id = f"Scraping {index + 1}: {source.name}"
            try:
                DjangoJob.objects.get(pk=source_id)
            except DjangoJob.DoesNotExist:
                scheduler.add_job(
                    scrape,
                    args=[source.to_dict()],
                    trigger="interval",
                    minutes=SCRAPING_INTERVAL,
                    misfire_grace_time=600,
                    id=source_id,
                    max_instances=1,
                    replace_existing=True,
                )
                logger.info("Added daily job: %s.", source_id)

        # delete old job executions
        try:
            DjangoJob.objects.get(pk="Delete Old Job Executions")
        except DjangoJob.DoesNotExist:
            scheduler.add_job(
                delete_old_job_executions,
                # Monday midnight
                trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
                id="Delete Old Job Executions",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Added weekly job: delete old executions.")

        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Manual shutdown of scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully.\n")
