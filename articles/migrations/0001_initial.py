# Generated by Django 5.0.1 on 2024-02-26 20:25

import django.db.models.deletion
import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Source",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        help_text="The name of the source", max_length=128, unique=True
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        blank=True,
                        help_text="The slug of the source for SEO-friendly urls",
                        max_length=255,
                    ),
                ),
                (
                    "publication_type",
                    models.CharField(
                        choices=[("newspaper/journal", "Newspaper or journal")],
                        help_text="The type of publication of the source",
                        max_length=24,
                    ),
                ),
                (
                    "language",
                    models.CharField(
                        blank=True,
                        choices=[("en", "English")],
                        help_text="The language of the article",
                        max_length=4,
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        help_text="The url of the source", max_length=255, unique=True
                    ),
                ),
                (
                    "paths",
                    models.JSONField(
                        help_text="A list of resource paths where the scraper will look for articles"
                    ),
                ),
                (
                    "regex",
                    models.CharField(
                        blank=True,
                        help_text="Regular expression for filtering hyper-links found at the resource paths",
                        max_length=255,
                    ),
                ),
                (
                    "javascript_required",
                    models.BooleanField(
                        default=False,
                        help_text="Whether the parsing of articles by this source requires rendering of JavaScript",
                    ),
                ),
                (
                    "headline_selectors",
                    models.JSONField(
                        help_text="Information about the structure of the target page needed to extract the headline of articles published by this source"
                    ),
                ),
                (
                    "summary_selectors",
                    models.JSONField(
                        blank=True,
                        help_text="Information about the structure of the target page needed to extract the summary of articles published by this source",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": [django.db.models.functions.text.Lower("title")],
            },
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "headline",
                    models.CharField(
                        help_text="The headline of the article", max_length=200
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="The slug of the article for SEO-friendly urls",
                        max_length=255,
                    ),
                ),
                ("created_at", models.DateTimeField()),
                (
                    "language",
                    models.CharField(
                        choices=[("en", "English")],
                        help_text="The language of the article",
                        max_length=4,
                    ),
                ),
                (
                    "url",
                    models.URLField(
                        help_text="The link to the article", max_length=255, unique=True
                    ),
                ),
                (
                    "summary",
                    models.TextField(blank=True, help_text="A summary of the article"),
                ),
                (
                    "source",
                    models.ForeignKey(
                        help_text="The source where the article is published",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="articles",
                        to="articles.source",
                    ),
                ),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(
                        fields=["headline", "url"],
                        name="articles_ar_headlin_4f6c91_idx",
                    )
                ],
            },
        ),
    ]
