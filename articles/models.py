import regex

from django.db import models
from django.db.models.functions import Lower
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

from .constants import PublicationType, Language


class Article(models.Model):
    """
    Metadata about articles from newspapers, journals, etc.

    Fields:
        headline (models.TextField): headline of the article
        slug (models.SlugField): slug of the article (generated from headline)
        created_at (models.DateTimeField): date the article was added to the
            database. Mostly corresponds to actual publication date, though
            this can vary. Actual dates are not used because their format
            varies a lot, hence they are difficult to parse.
        language (models.CharField): the language of the article
        link (models.URLField): link to the article
        body (models.TextField): either the actual body of the article,
            or a short desriptive paragraph

    Relations:
        source (ForeignKey): the source of the article

    Methods:
        __str__: string representation for the admin area
    """

    headline = models.TextField(
        _("headline"),
        help_text=_("The headline of the article"),
    )
    slug = models.SlugField(
        _("Slug"),
        help_text=_("The slug of the article for SEO-friendly urls"),
    )
    created_at = models.DateTimeField()
    language = models.CharField(
        _("language"),
        max_length=4,
        choices=Language.choices,
        blank=True,
        help_text=_("The language of the article"),
    )
    link = models.URLField(
        _("link"),
        unique=True,
        help_text=_("The link to the article")
    )
    body = models.TextField(
        _("body"),
        null=True,
        blank=True,
        help_text=_("The body of the article"),
    )
    source = models.ForeignKey(
        "Source",
        on_delete=models.CASCADE,
        related_name="articles",
        help_text=_("The source where the article is published"),
    )

    class Meta:
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["headline", "link"])]

    def __str__(self):
        return f"{self.source}: {self.headline}"


class Source(models.Model):
    """
    Metadata about the source of articles

    Fields:
        name (models.CharField): name of the source
        slug (models.SlugField): slug of the source
        publication_type (models.CharField): the type of publication of the
            source (newspaper, journal, blog...)
        language (models.CharField): the language of the source
        link (models.URLField): the base url of the source
        paths (models.JSONField): a list of paths, each of which is appended to
            the base url to tell the scraper where to look for hyper-links
            ('https://example.com/path1/')
        regex (models.CharField): a regular expression for filtering links
        javascript (models.BooleanField): True if JavaScript must be rendered before
            data can be extracted from the webpage, False otherwise
        headline_selectors (models.JSONField): information about the CSS selectors
            needed to extract the headline of an article
        body_selectors (models.JSONField): information about the CSS selectors
            needed to extract the body of an article (or a descriptive paragraph)

    Methods:
        __str__: string representation of the model for the admin area
        to_dict: creates a dictionary with the information required by the
            scraper
    """

    name = models.CharField(
        _("name"),
        max_length=128,
        unique=True,
        blank=False,
        help_text=_("The name of the source"),
    )
    slug = models.SlugField(
        _("Slug"),
        blank=True,
        help_text=_("The slug of the source for SEO-friendly urls"),
    )
    publication_type = models.CharField(
        _("publication type"),
        max_length=24,
        choices=PublicationType.choices,
        blank=False,
        help_text=_("The type of publication of the source"),
    )
    language = models.CharField(
        _("language"),
        max_length=4,
        choices=Language.choices,
        blank=True,
        help_text=_("The language of the article"),
    )
    link = models.URLField(
        _("link"),
        unique=True,
        validators=[URLValidator],
        help_text=_("The link to the source")
    )
    #
    # info related to scraping
    #
    paths = models.JSONField(
        _("paths"),
        help_text=_(
            "A list of resource paths where the scraper will look for articles"
        ),
    )
    regex = models.CharField(
        _("regex"),
        max_length=512,
        blank=True,
        help_text=(
            "Regular expression for filtering hyper-links found at the resource paths"
        ),
    )
    javascript = models.BooleanField(
        _("render javascript"),
        default=False,
        help_text=_(
            "Whether the parsing of articles by this source requires rendering "
            "of JavaScript"
        )
    )
    headline_selectors = models.JSONField(
        _("headline selectors"),
        help_text=_(
            "Information about the structure of the target page needed to extract "
            "the headline of articles published by this source"
        )
    )
    body_selectors = models.JSONField(
        _("body selectors"),
        null=True,
        blank=True,
        help_text=_(
            "Information about the structure of the target page needed to extract "
            "the body of articles published by this source"
        )
    )

    class Meta:
        ordering = [Lower("name"), ]

    def __str__(self):
        return f"{self.name}"

    def to_dict(self):
        sitemap = \
            {
                "base_url": self.link,
                "paths": self.paths,
                "language": self.language,
                "javascript": self.javascript,
                "filter": regex.compile(self.regex),
                "headline_selectors": self.headline_selectors,
                "body_selectors": self.body_selectors,
            }
        return sitemap
