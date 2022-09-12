"""
Stage settings for nous_aggregator project.

The settings are meant for running the app inside a Docker container.
They emulate the production environment with the use of environment variables.

Values for the env variables must be stored in a file .env-staging (see env-sample for
instructions). They are loaded via dotenv in the __init__.py file.

Defaults are chosen with security in mind: DEBUG is False by default, SECRET_KEY
has an empty default in order to make the app crash if it's not set and DEBUG is off etc.
"""
import os
from dotenv import load_dotenv
from .basic import *

load_dotenv(".env")

SECRET_KEY = os.getenv("SECRET_KEY", default="")

DEBUG = os.getenv("DEBUG", default="False") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", default="").split(',')

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", default="").split(',')

SESSION_COOKIE_SECURE = os.getenv("SESSION_COOKIE_SECURE", default="True") == "True"

CSRF_COOKIE_SECURE = os.getenv("CSRF_COOKIE_SECURE", default="True") == "True"

SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", default="True") == "True"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

DATABASES = {
    "default": {
        "ENGINE": os.getenv("DATABASE_ENGINE", default="django.db.backends.postgresql"),
        "NAME": os.getenv("DATABASE_NAME", default="postgres"),
        "USER": os.getenv("DATABASE_USER", default="postgres"),
        "PASSWORD": os.getenv("DATABASE_PASSWORD", default="postgres"),
        "HOST": os.getenv("DATABASE_HOST", default="postgres"),
        "PORT": int(os.getenv("DATABASE_PORT", default=5432)),
    },
}
