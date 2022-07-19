import regex  # type: ignore
from django.db import models
from django.db.models.functions import Lower


class Article(models.Model):
    """
    Represents metadata about articles from newspapers, journals, etc.

    Attributes:
        headline (str): the headline of the article
        source (Source): the source of the article
        body (str): either the actual body of the article,
            or a short desriptive paragraph
        language (Language): the language of the article
        pubdate (datetime): the date at which the article was added to the
            database. Mostly corresponds to actual publication date, though
            it can vary. Actual dates are not used because their format
            varies a lot, hence they are difficult to parse.

    Methods:
        __str__: string representation for the admin area
    """
    headline = models.CharField(max_length=500)
    source = models.ForeignKey(
        "Source", on_delete=models.CASCADE, related_name="articles"
    )
    body = models.TextField(null=True, blank=True)
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
    """Represents metadata about the language of an article"""
    name = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return f"{self.name}"


class PublicationType(models.Model):
    """Represents metadata about the type of publication of an article"""
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return f"{self.name}"


class Source(models.Model):
    """
    Represents metadata about the source of an article

    Attributes:
        name (str): the name of the source
        link (str): the base url of the source ('https://www.example.com/')
        publication_type (PublicationType): the type of publication of the
            source (newspaper, journal, blog, etc,)
        language (Language): the language of the source (used by the scraper
            to compare against the language of a webpage)
        paths (list): a list of paths, each of which is appended to the base url to
            tell the scraper where to look for links ('https://example.com/path1/',
            'https://example.com/path2/')
        javascript (bool): True if JavaScript must be rendered before data can be
            extracted from the webpage, False otherwise
        regex (str): a regular expression for filtering links; the scraper will only
            follow links that pass the test
        headline (dict): contains information about the HTML/CSS needed to extract
            the headline of an article
        body (dict): contains information about the HTML/CSS needed to extract
            the body of an article (or a descriptive paragraph)

    Methods:
        __str__: string representation of the model for the admin area
        to_dict: creates a dictionary with the information required by the
            scraper
    """
    name = models.CharField(max_length=128, unique=True)
    link = models.URLField(max_length=128, unique=True)
    publication_type = models.ForeignKey(
        "PublicationType", null=True, blank=True, on_delete=models.SET_NULL
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
