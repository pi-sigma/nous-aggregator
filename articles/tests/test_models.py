import regex  # type: ignore

from ..models import Article, Source


#
# Test Source
#
def test_create_source(source_values):
    source = Source(**source_values)

    for attr_name in source_values:
        assert getattr(source, attr_name) == source_values.get(attr_name)


def test_source_to_dict(source_values):
    source = Source(**source_values)
    sitemap = source.to_dict()

    for attr_name in [
            "body_selectors", "headline_selectors", "javascript", "language", "paths"
    ]:
        assert getattr(source, attr_name) == sitemap.get(attr_name)

    assert source.link == sitemap["base_url"]
    assert regex.compile(source.regex) == sitemap["filter"]


def test_source_str_representation(source_values):
    source = Source(**source_values)

    assert str(source) == "Fake News"


#
# Test Article
#
def test_create_article(article_values_m):
    article = Article(**article_values_m)

    for attr_name in article_values_m:
        assert getattr(article, attr_name) == article_values_m.get(attr_name)


def test_article_representation(article_values_m):
    article = Article(**article_values_m)

    assert str(article) == (
        f"{article.source}: {article.headline}"
    )
