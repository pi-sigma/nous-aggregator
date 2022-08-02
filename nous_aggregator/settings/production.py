"""
Production settings for nous_aggregator project.

Identical to stage settings, except that values for environment
variables are pulled from Heroku via a Django plugin.
"""
import django_on_heroku
from . staging import *


django_on_heroku.settings(locals())
