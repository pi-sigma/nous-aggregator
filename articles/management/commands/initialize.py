"""Scheduler for initializing an empty database"""
import logging

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.blocking import BlockingScheduler
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from .sitemaps import sitemaps as maps
from articles.models import Language
from articles.models import PublicationType
from articles.models import Source


logger = logging.getLogger(__name__)


def initialize_db_languages() -> None:
    """Initialize database with languages."""
    try:
        Language.objects.get(pk=1)
    except Language.DoesNotExist:
        lang = Language(
            name="en",
        )
        try:
            lang.save()
        except IntegrityError:
            pass


def initialize_db_pubtypes() -> None:
    """Initialize database with publication types."""
    try:
        PublicationType.objects.get(pk=1)
    except PublicationType.DoesNotExist:
        pubtype = PublicationType(
            name="newspaper/journal",
        )
        try:
            pubtype.save()
        except IntegrityError:
            pass


def initialize_db_sources(sitemaps: dict) -> None:
    """Initialize database with sources in accordance with `sitemaps`."""
    try:
        Source.objects.get(pk=1)
    except Source.DoesNotExist:
        for sitemap in sitemaps:
            publication_type = PublicationType.objects.get(name=sitemap["publication_type"])
            language = Language.objects.get(name=sitemap["language"])
            source = Source(
                name=sitemap["name"],
                publication_type=publication_type,
                language=language,
                link=sitemap["base_url"],
                paths=sitemap["paths"],
                javascript=sitemap["javascript"],
                regex=sitemap["regex"],
                headline=sitemap["headline"],
                body=sitemap["body"],
            )
            try:
                source.save()
            except IntegrityError:
                pass


def terminate_scheduler(scheduler, should_exit=False):
    if should_exit:
        logger.info("Terminating scheduler...")
        scheduler.shutdown(wait=False)


class Command(BaseCommand):
    """Create jobs"""
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(
            executors={"default": ThreadPoolExecutor(1)}
        )

        scheduler.add_job(
            initialize_db_languages,
            id="Add languages",
            max_instances=1,
        )

        scheduler.add_job(
            initialize_db_pubtypes,
            id="Add publication types",
            max_instances=1,
        )

        scheduler.add_job(
            initialize_db_sources,
            args=[maps],
            id="Add sources",
            max_instances=1,
        )

        scheduler.add_job(
            terminate_scheduler, args=[scheduler, {"should_exit": True}]
        )

        logger.info("Initializing database...")
        scheduler.start()
