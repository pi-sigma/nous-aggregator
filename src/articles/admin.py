from django.contrib import admin
from django.contrib.admin import ModelAdmin, StackedInline

from .models import Article, RSSFeed, Sitemap, Source

admin.site.register(Article)


class SitemapInline(StackedInline):
    model = Sitemap
    classes = ["collapse"]


class RSSInline(StackedInline):
    model = RSSFeed
    classes = ["collapse"]
    extra = 0


@admin.register(Source)
class SourceAdmin(ModelAdmin):
    inlines = (SitemapInline, RSSInline)
    fieldsets = (
        (
            "Basic info",
            {
                "fields": [
                    "title",
                    "slug",
                    "publication_type",
                    "language",
                    "url",
                ]
            }
        ),
    )
