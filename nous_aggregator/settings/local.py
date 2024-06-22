import socket
from typing import List

from .base import *

hostname: str
ips: List[str]

SECRET_KEY = "hush-hush"

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
    }
}

INSTALLED_APPS += [
    "debug_toolbar",
    "django_extensions",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]


LOG_DIR: Path = BASE_DIR / "logs"
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} [{module}] {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} [{module}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'django': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, "django.log"),
            'maxBytes': 100000,
            'backupCount': 2,
            'formatter': 'verbose',
        },
        'project': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(LOG_DIR, "nous_aggregator.log"),
            'maxBytes': 1024 * 1024 * 10,  # Max 10MB
            'backupCount': 3,
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['django'],
            'propagate': True,
            'level': 'INFO',
        },
        'articles': {
            'handlers': ['project'],
            'propagate': True,
            'level': 'INFO',
        },
        'scraper': {
            'handlers': ['project'],
            'propagate': True,
            'level': 'INFO',
        },
        'rss': {
            'handlers': ['project'],
            'propagate': True,
            'level': 'INFO',
        },
    },
}

# for django_debug_toolbar
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
