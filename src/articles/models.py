import regex
from django.db import models
from django.db.models.functions import Lower
from django.utils.translation import gettext_lazy as _

from .constants import Language, PublicationType


class Article(models.Model):
    """
    Metadata about articles from newspapers, journals, etc.

    Fields:
        headline (models.TextField): headline of the article
        slug (models.SlugField): slug of the article (generated from headline)
        summary (models.TextField): short paragraph summarizing the article
        created_at (models.DateTimeField): date the article was added to the
            database. Mostly corresponds to actual publication date, though
            this can vary. Actual dates are not used because their format
            varies a lot, hence they are difficult to parse.
        language (models.CharField): the language of the article
        url (models.URLField): link to the article

    Relations:
        source (ForeignKey): the source of the article

    Methods:
        __str__: string representation for the admin area
    """

    headline = models.CharField(
        max_length=512,
        help_text=_("The headline of the article"),
    )
    slug = models.SlugField(
        max_length=1024,
        help_text=_("The slug of the article for SEO-friendly urls"),
    )
    summary = models.TextField(
        blank=True,
        help_text=_("A summary of the article"),
    )
    created_at = models.DateTimeField()
    language = models.CharField(
        max_length=4,
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
        indexes = [models.Index(fields=["headline", "url"])]

    def __str__(self) -> str:
        return f"{self.source}: {self.headline}"


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
        paths (models.JSONField): a list of paths, each of which is appended to
            the base url to tell the scraper where to look for hyper-links
            ('https://example.com/path1/')
        regex (models.CharField): a regular expression for filtering links
        javascript_required (models.BooleanField): True if JavaScript must be rendered
            before data can be extracted from the webpage, False otherwise
        headline_selectors (models.JSONField): information about the CSS selectors
            needed to extract the headline of an article
        summary_selectors (models.JSONField): information about the CSS selectors
            needed to extract the summary of an article

    Methods:
        __str__: string representation of the model for the admin area
        to_dict: creates a dictionary with the information required by the
            scraper
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
        max_length=4,
        choices=Language.choices,
        blank=True,
        help_text=_("The language of the article"),
    )
    url = models.URLField(
        unique=True,
        max_length=512,
        help_text=_("The url of the source"),
    )
    #
    # data related to scraping
    #
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
    headline_search_params_find = models.JSONField(
        help_text=_(
            "Selectors for extracting the headline of articles"
        ),
    )
    headline_search_params_remove = models.JSONField(
        help_text=_(
            "Selectors for HTML elements that need to be removed from the headline"
        ),
    )
    summary_search_params_find = models.JSONField(
        default=str,
        help_text=_(
            "Selectors for extracting the summary of articles"
        ),
    )
    summary_search_params_remove = models.JSONField(
        default=list,
        help_text=_(
            "Selectors for HTML elements that need to be removed from the summary"
        ),
    )

    class Meta:
        ordering = [
            Lower("title"),
        ]

    def __str__(self) -> str:
        return f"{self.title}"

    def to_dict(self):
        sitemap = {
            "base_url": self.url,
            "paths": self.paths,
            "language": self.language,
            "javascript_required": self.javascript_required,
            "filter": regex.compile(self.regex),
            "search_params": {
                "headline": {
                    "find": self.headline_search_params_find,
                    "remove": self.headline_search_params_remove,
                },
                "summary": {
                    "find": self.summary_search_params_find,
                    "remove": self.summary_search_params_remove,
                },
            },
        }
        return sitemap
