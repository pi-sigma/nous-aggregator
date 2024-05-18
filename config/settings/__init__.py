"""
Settings are loaded depending on the DJANGO_ENV environment variable,
"""

from decouple import config

DJANGO_ENV = config('DJANGO_ENV', default="")

match DJANGO_ENV:
    case "":
        from .base import *
    case "BASE":
        from .base import *
    case "LOCAL":
        from .local import *
    case "PRODUCTION":
        from .production import *
