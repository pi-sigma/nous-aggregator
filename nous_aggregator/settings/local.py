"""
Development settings for nous_aggregator project.

With these settings, the development server and pytest
can be run without Docker.
"""

from .basic import *


SECRET_KEY = "hush-hush"

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "postgres",
        "USER": "postgres",
        "PASSWORD": "postgres",
        "HOST": "localhost",
        "PORT": 5432,
    },
}
