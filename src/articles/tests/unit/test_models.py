import regex  # type: ignore

from articles.models import Article, Source


#
# Source
#
def test_create_source(source_values) -> None:
    source = Source(**source_values)

    for attr_name in source_values:
        assert getattr(source, attr_name) == source_values.get(attr_name)


def test_source_to_dict(source_values) -> None:
    source = Source(**source_values)
    sitemap = source.to_dict()

    for attr_name in [
        "javascript_required",
        "language",
        "paths",
    ]:
        assert getattr(source, attr_name) == sitemap.get(attr_name)

    assert source.url == sitemap["base_url"]
    assert regex.compile(source.regex) == sitemap["filter"]
    assert sitemap["search_params"]["headline"]["find"] == source.headline_search_params_find
    assert sitemap["search_params"]["headline"]["remove"] == source.headline_search_params_remove
    assert sitemap["search_params"]["summary"]["find"] == source.summary_search_params_find
    assert sitemap["search_params"]["summary"]["remove"] == source.summary_search_params_remove


def test_source_str_representation(source_values) -> None:
    source = Source(**source_values)

    assert str(source) == "Fake News"


#
# Article
#
def test_create_article(article_values_m) -> None:
    article = Article(**article_values_m)

    for attr_name in article_values_m:
        assert getattr(article, attr_name) == article_values_m.get(attr_name)


def test_article_representation(article_values_m) -> None:
    article = Article(**article_values_m)

    assert str(article) == (f"{article.source}: {article.headline}")
