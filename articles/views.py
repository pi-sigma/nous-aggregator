import re

from django.shortcuts import render
from django.views.generic import ListView

from .models import Article, Source


def index(request):
    """Display latest articles for all sources."""
    context = {
        "sources": Source.objects.only("name", "link", "publication_type"),
    }
    return render(request, "articles/index.html", context)


class SearchResultsView(ListView):
    """Display sources + articles matching query."""

    model = Article
    fields = ["headline", "link", "body"]
    template_name = "articles/search_results.html"

    def get_context_data(self, **kwargs):
        """Filter sources by query."""
        query = self.request.GET.get("q")
        # precaution: empty strings are also excluded on the client-side
        if query in ("", " ", "  "):
            query = "Please don't attempt to hack my website, thanks!"
        regex = r"(?<![a-zA-Z])" + re.escape(query) + r"(?![a-rA-Rt-zT-Z])"
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "sources": Source.objects.only("name", "link", "publication_type")
                .filter(articles__headline__iregex=regex)
                .distinct(),
                "query": query,
            },
        )
        return context

    def get_queryset(self):
        """Filter articles by query."""
        query = self.request.GET.get("q")
        regex = r"(?<![a-zA-Z])" + re.escape(query) + r"(?![a-rA-Rt-zT-Z])"
        return Article.objects.filter(headline__iregex=regex)
