import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nous_aggregator.settings.local")

app = Celery("nous_aggregator")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
