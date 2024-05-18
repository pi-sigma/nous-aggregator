from django.db import models


class Language(models.TextChoices):
    en = "en", "English"
    en_us = "en-us", "English (AE)"


class PublicationType(models.TextChoices):
    newspaper = "newspaper/journal", "Newspaper or journal"
