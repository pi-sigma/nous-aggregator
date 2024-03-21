"""
Settings are loaded depending on the value of the DJANGO_ENV environment variable,

On the production server, DJANGO_ENV should be left undefined
(hence the production settings are loaded by default).
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
