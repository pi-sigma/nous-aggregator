from typing import List

from django.urls import path
from django.urls.resolvers import URLPattern

from . import views

urlpatterns: List[URLPattern] = [
    path("", views.index, name="index"),
    path("search", views.SearchResultsView.as_view(), name="search"),
]
