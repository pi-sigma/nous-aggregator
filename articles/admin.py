from django.contrib import admin

from .models import PublicationType, Source, Language, Article


admin.site.register(PublicationType)
admin.site.register(Source)
admin.site.register(Language)
admin.site.register(Article)
