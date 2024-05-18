import regex
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from .constants import Language, PublicationType


class Article(models.Model):
    """
    Metadata about articles from newspapers, journals, etc.

    Fields:
        title (models.TextField): headline of the article
        slug (models.SlugField): slug of the article (generated from title)
        description (models.TextField): short paragraph summarizing the article
        created_at (models.DateTimeField): date the article was added to the
            database. Either the publication date (from RSS feed) or the time
            the article was created (if the article is scraped; the publication
            date is difficult to obtain in this case)
        language (models.CharField): the language of the article
        url (models.URLField): link to the article

    Relations:
        source (ForeignKey): the source of the article

    Methods:
        __str__: string representation for the admin area
    """

    title = models.CharField(
        max_length=512,
        help_text=_("The headline of the article"),
    )
    slug = models.SlugField(
        max_length=1024,
        help_text=_("The slug of the article for SEO-friendly urls"),
    )
    description = models.TextField(
        blank=True,
        help_text=_("A description/summary of the article"),
    )
    created_at = models.DateTimeField()
    language = models.CharField(
        max_length=16,
        choices=Language.choices,
        blank=False,
        help_text=_("The language of the article"),
    )
    url = models.URLField(
        max_length=512,
        unique=True,
        help_text=_("The link to the article"),
    )
    source = models.ForeignKey(
        to="Source",
        on_delete=models.CASCADE,
        related_name="articles",
        help_text=_("The source where the article is published"),
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["title", "url"])]

    def __str__(self) -> str:
        return f"{self.source}: {self.title}"


class Source(models.Model):
    """
    Metadata about the source of articles

    Fields:
        title (models.CharField): name/title of the source
        slug (models.SlugField): slug of the source
        publication_type (models.CharField): the type of publication of the
            source (newspaper, journal, blog...)
        language (models.CharField): the language of the source
        url (models.URLField): the base url of the source

    Relations:
        sitemap (models.OneToOneField): information about the HTML/CSS structure
            of the page required for scraping

    Methods:
        __str__: string representation of the model for the admin area
    """

    title = models.CharField(
        max_length=128,
        unique=True,
        blank=False,
        help_text=_("The name of the source"),
    )
    slug = models.SlugField(
        max_length=255,
        blank=True,
        help_text=_("The slug of the source for SEO-friendly urls"),
    )
    publication_type = models.CharField(
        max_length=24,
        choices=PublicationType.choices,
        blank=False,
        help_text=_("The type of publication of the source"),
    )
    language = models.CharField(
        max_length=16,
        choices=Language.choices,
        blank=True,
        help_text=_("The language of the article"),
    )
    url = models.URLField(
        unique=True,
        max_length=512,
        help_text=_("The url of the source"),
    )

    class Meta:
        ordering = [
            Lower("title"),
        ]

    def __str__(self) -> str:
        return f"{self.title}"


class Sitemap(models.Model):
    """Information for scraping source"""

    source = models.OneToOneField(
        to=Source,
        on_delete=models.CASCADE,
    )
    paths = models.JSONField(
        help_text=_(
            "List of resource paths where the scraper will look for articles"
        ),
    )
    regex = models.CharField(
        max_length=255,
        blank=True,
        help_text=(
            "Regular expression for filtering hyper-links found at the resource paths"
        ),
    )
    javascript_required = models.BooleanField(
        default=False,
        help_text=_(
            "Whether the parsing of articles by this source requires rendering "
            "of JavaScript"
        ),
    )
    title_search_params_find = models.JSONField(
        default=str,
        help_text=_(
            "Selectors for extracting the headline of articles"
        ),
    )
    title_search_params_remove = models.JSONField(
        null=True,
        blank=True,
        help_text=_(
            "Selectors for HTML elements that need to be removed from the headline"
        ),
    )
    description_search_params_find = models.JSONField(
        default=str,
        help_text=_(
            "Selectors for extracting the summary of articles"
        ),
    )
    description_search_params_remove = models.JSONField(
        null=True,
        blank=True,
        help_text=_(
            "Selectors for HTML elements that need to be removed from the summary"
        ),
    )

    def to_dict(self):
        return {
            "base_url": self.source.url,
            "paths": self.paths,
            "language": self.source.language,
            "javascript_required": self.javascript_required,
            "filter": regex.compile(self.regex),
            "search_params": {
                "title": {
                    "find": self.title_search_params_find,
                    "remove": self.title_search_params_remove,
                },
                "description": {
                    "find": self.description_search_params_find,
                    "remove": self.description_search_params_remove,
                },
            },
        }


class Feed(models.Model):
    source = models.ForeignKey(
        to=Source,
        on_delete=models.CASCADE,
        related_name="feeds",
    )
    url = models.URLField(
        unique=True,
        max_length=512,
        help_text=_("The url of the RSS feed"),
    )
