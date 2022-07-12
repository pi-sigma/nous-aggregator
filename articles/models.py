import regex  # type: ignore
from django.db import models
from django.db.models.functions import Lower


class Article(models.Model):
    headline = models.CharField(max_length=500)
    source = models.ForeignKey(
        "Source", on_delete=models.CASCADE, related_name="articles"
    )
    body = models.TextField(null=True)
    language = models.ForeignKey(
        "Language", null=True, blank=True, on_delete=models.SET_NULL
    )
    link = models.URLField(unique=True)
    pubdate = models.DateTimeField()

    def __str__(self):
        return f"{self.source}: {self.headline}"

    class Meta:
        ordering = ("-pubdate",)
        indexes = [models.Index(fields=["headline", "link"])]


class Language(models.Model):
    name = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return f"{self.name}"


class PublicationType(models.Model):
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.name}"


class Source(models.Model):
    name = models.CharField(max_length=128, unique=True)
    link = models.URLField(max_length=128, unique=True)
    publication_type = models.ForeignKey(
        "PublicationType",
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    language = models.ForeignKey("Language", null=True, on_delete=models.SET_NULL)
    paths = models.JSONField()
    javascript = models.BooleanField(default=False)
    regex = models.CharField(max_length=512)
    headline = models.JSONField()
    body = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        sitemap = \
            {
                "base_url": self.link,
                "paths": self.paths,
                "language": self.language.name,
                "javascript": self.javascript,
                "filter": regex.compile(self.regex),
                "headline": self.headline,
                "body": self.body,
            }
        return sitemap

    class Meta:
        ordering = [Lower("name"), ]
        indexes = [models.Index(fields=["link"])]
