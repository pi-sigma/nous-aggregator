"""
Depending on the value of the DJANGO_ENV environment variable,
different settings are loaded.

On the production server, DJANGO_ENV should be left undefined
(hence the production settings are loaded by default).
"""
import os

DJANGO_ENV = os.getenv('DJANGO_ENV')

match DJANGO_ENV:
    case "CI":
        from . ci import *
    case "LOCAL":
        from . local import *
    case "STAGE":
        from . staging import *
    case _:
        from . production import *
