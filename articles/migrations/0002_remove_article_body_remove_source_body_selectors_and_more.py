# Generated by Django 4.2.5 on 2023-09-20 18:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="article",
            name="body",
        ),
        migrations.RemoveField(
            model_name="source",
            name="body_selectors",
        ),
        migrations.AddField(
            model_name="article",
            name="summary",
            field=models.TextField(
                blank=True,
                help_text="A summary of the article",
                null=True,
                verbose_name="summary",
            ),
        ),
        migrations.AddField(
            model_name="source",
            name="summary_selectors",
            field=models.JSONField(
                blank=True,
                help_text="Information about the structure of the target page needed to extract the summary of articles published by this source",
                null=True,
                verbose_name="summary selectors",
            ),
        ),
    ]
