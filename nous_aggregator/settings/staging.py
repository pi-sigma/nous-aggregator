"""
The settings emulate the production environment

Defaults are chosen with security in mind: DEBUG is False by default, SECRET_KEY
has an empty default in order to make the app crash if it's not set and DEBUG is off etc.
"""

from .base import *

import socket

from decouple import config, Csv


SECRET_KEY = config("SECRET_KEY", default="")

DEBUG = config("DEBUG", default=False, cast=bool)

ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="", cast=Csv())

CSRF_TRUSTED_ORIGINS = config("CSRF_TRUSTED_ORIGINS", default="", cast=Csv())

SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", default=True, cast=bool)

CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", default=True, cast=bool)

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
    "default": {
        "ENGINE": config("DATABASE_ENGINE", default="django.db.backends.postgresql"),
        "NAME": config("DATABASE_NAME", default="postgres"),
        "USER": config("DATABASE_USER", default="postgres"),
        "PASSWORD": config("DATABASE_PASSWORD", default="postgres"),
        "HOST": config("DATABASE_HOST", default="localhost"),
        # "HOST": "host.docker.internal",
        # "HOST": "localhost",
        "PORT": config("DATABASE_PORT", default=5432, cast=int),
    },
}

# for django_debug_toolbar
hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + ["127.0.0.1", "10.0.2.2"]
