import re

from django.shortcuts import render
from django.views.generic import ListView

from .models import Article
from .models import Source


TIMESPAN = 7  # no. of days


def index(request):
    """Display latest articles for all sources."""
    context = {
        "sources": Source.objects.only("name", "link", "publication_type")
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
        regex = r"(?<![a-zA-Z])" + re.escape(query) + r"(?![a-rA-Rt-zT-Z])"
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        context.update(
            {
                "sources": Source.objects.only("name", "link", "publication_type").filter(
                    articles__headline__iregex=regex,
                ).distinct(),
                "query": query,
            },
        )
        return context

    def get_queryset(self):
        """Filter articles by query."""
        query = self.request.GET.get("q")
        regex = r"(?<![a-zA-Z])" + re.escape(query) + r"(?![a-rA-Rt-zT-Z])"
        return Article.objects.filter(headline__iregex=regex)
