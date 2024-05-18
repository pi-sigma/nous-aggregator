import regex  # type: ignore

from articles.models import Article, Sitemap, Source


#
# Source
#
def test_create_source(source_values) -> None:
    source = Source(**source_values)

    for attr_name in source_values:
        assert getattr(source, attr_name) == source_values.get(attr_name)


def test_source_str_representation(source_values) -> None:
    source = Source(**source_values)

    assert str(source) == "Fake News"


#
# Sitemap
#
def test_create_sitemap(sitemap_values) -> None:
    sitemap = Sitemap(**sitemap_values)

    for attr_name in sitemap_values:
        assert getattr(sitemap, attr_name) == sitemap_values.get(attr_name)


def test_sitemap_to_dict(sitemap_values) -> None:
    sitemap = Sitemap(**sitemap_values)
    sitemap_dict = sitemap.to_dict()

    for attr_name in [
        "javascript_required",
        "paths",
    ]:
        assert getattr(sitemap, attr_name) == sitemap_dict.get(attr_name)

    assert regex.compile(sitemap.regex) == sitemap_dict["filter"]
    assert sitemap_dict["search_params"]["title"]["find"] == sitemap.title_search_params_find
    assert sitemap_dict["search_params"]["title"]["remove"] == sitemap.title_search_params_remove
    assert sitemap_dict["search_params"]["description"]["find"] == sitemap.description_search_params_find
    assert (
        sitemap_dict["search_params"]["description"]["remove"] == sitemap.description_search_params_remove
    )


#
# Article
#
def test_create_article(article_values_m) -> None:
    article = Article(**article_values_m)

    for attr_name in article_values_m:
        assert getattr(article, attr_name) == article_values_m.get(attr_name)


def test_article_representation(article_values_m) -> None:
    article = Article(**article_values_m)

    assert str(article) == (f"{article.source}: {article.title}")
