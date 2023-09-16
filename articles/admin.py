from django.contrib import admin

from .models import Article, Source

admin.site.register(Source)
admin.site.register(Article)
