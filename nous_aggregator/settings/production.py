"""
Production settings for nous_aggregator project.

Identical to stage settings, except:
    - values for environment variables are pulled
      from Heroku via a Django plugin.
    - sentry config is specific to production
"""

import django_on_heroku

from .staging import *


sentry_sdk.init(
    dsn="https://242fe72f1a234cecae5a3b1fad7bb4c0@o1410776.ingest.sentry.io/6748377",
    integrations=[
        DjangoIntegration(),
    ],

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production.
    traces_sample_rate=0.2,

    # If you wish to associate users to errors (assuming you are using
    # django.contrib.auth) you may enable sending PII data.
    send_default_pii=True,

    environment="production",
)

django_on_heroku.settings(locals())
