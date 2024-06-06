from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter(name="strip_html_tags")
def strip_html_tags(content: str) -> str:
    return strip_tags(content)
