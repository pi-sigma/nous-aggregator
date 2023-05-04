from django.db import models


class Language(models.TextChoices):
    en = "en", "English"


class PublicationType(models.TextChoices):
    newspaper = "newspaper/journal", "Newspaper or journal"
