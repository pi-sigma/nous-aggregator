import re

from django.shortcuts import render
from django.views.generic import ListView

from .models import Article, Source


def index(request):
    context = {
        "sources": Source.objects.only("name", "url", "publication_type"),
    }
    return render(request, "articles/index.html", context)


class SearchResultsView(ListView):
    model = Article
    fields = ["headline", "url", "body"]
    template_name = "articles/search_results.html"

    def get_context_data(self, **kwargs):
        """Pre-filter sources on the basis of article headlines and queries"""

        context = super().get_context_data(**kwargs)

        query = self.request.GET.get("q")
        if query and not query.isspace():
            regex = r"(?<![a-zA-Z])" + re.escape(query) + r"(?![a-rA-Rt-zT-Z])"
            context.update(
                {
                    "sources": Source.objects.only("name", "url", "publication_type")
                                             .filter(articles__headline__iregex=regex)
                                             .distinct(),
                    "query": query,
                },
            )
        return context

    def get_queryset(self):
        query = self.request.GET.get("q")
        regex = r"(?<![a-zA-Z])" + re.escape(query) + r"(?![a-rA-Rt-zT-Z])"
        return Article.objects.filter(headline__iregex=regex)
