"""
Scheduler for scraping

Jobs are stored in a Django job store. Old jobs should be deleted when
the sources are changed; otherwise the scheduler will use the old information.
"""
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
from django_apscheduler.models import DjangoJob
from django_apscheduler.models import DjangoJobExecution

from articles.models import Article
from articles.models import Language
from articles.models import Source
from articles.scraper.spider import Spider

logger = logging.getLogger(__name__)

INTERVAL = 480  # interval in minutes for scraping


def scrape(sitemap: dict):
    """Scrape newspapers/journals and store articles in database."""
    Spider.crawl(sitemap)
    data = [json.loads(article) for article in Spider.articles]

    for article_data in data:
        article = Article(
            headline=article_data["headline"],
            source=Source.objects.get(link=article_data["source_link"]),
            body=article_data["body"],
            language=Language.objects.get(name=article_data["language"]),
            link=article_data["link"],
            pubdate=make_aware(datetime.now()),
        )
        try:
            article.save()
        except IntegrityError as e:
            logger.error("Article (%s) already exists in database (%s)", article_data["headline"], e)


def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    """Create jobs."""
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(
            timezone=settings.TIME_ZONE, executors={"default": ThreadPoolExecutor(1)},
        )
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # jobs for scraping newspapers/journals
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
                    minutes=INTERVAL,
                    misfire_grace_time=360,
                    id=source_id,
                    max_instances=1,
                    replace_existing=True,
                )
                logger.info(f"Added daily job: {source_id}.")

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
