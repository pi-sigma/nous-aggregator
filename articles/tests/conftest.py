import pytest
from django.test import Client
from django.utils import timezone

from ..constants import Language, PublicationType
from ..models import Article, Source


#
# Test fixtures
#
@pytest.fixture
def source_values():
    return {
        "name": "Fake News",
        "slug": "fake-news",
        "link": "https://www.hocusbogus.com/",
        "publication_type": PublicationType.newspaper,
        "language": Language.en,
        "paths": ["world/"],
        "javascript": False,
        "regex": "[0-9]{4}/[0-9]{2}/[0-9]{2}",
        "headline_selectors": {"tag": "h1", "attrs": {}},
        "body_selectors": {"tag": "h2", "attrs": {}},
    }


@pytest.fixture
def source_instance(source_values):
    return Source.objects.create(**source_values)


@pytest.fixture
def source_values_2():
    return {
        "name": "Alternative Facts",
        "slug": "alternative-facts",
        "link": "https://www.nonsensical.org/",
        "publication_type": PublicationType.newspaper,
        "language": Language.en,
        "paths": ["world/"],
        "javascript": False,
        "regex": "[0-9]{4}/[0-9]{2}/[0-9]{2}",
        "headline_selectors": {"tag": "h1", "attrs": {}},
        "body_selectors": {"tag": "h2", "attrs": {}},
    }


@pytest.fixture
def source_instance_2(source_values_2):
    return Source.objects.create(**source_values_2)


@pytest.fixture
def article_values(source_instance):
    return {
        "headline": "A cow jumps over the moon",
        "slug": "a-cow-jumps-over-the-moon",
        "body": "Lorem dolor sit amet...",
        "link": "https://www.hocusbogus.com/2022/05/08/foobar",
        "source": source_instance,
        "created_at": timezone.localtime(),
    }


@pytest.fixture
def article_values_m(source_values):
    return {
        "headline": "A cow jumps over the moon",
        "slug": "a-cow-jumps-over-the-moon",
        "body": "Lorem dolor sit amet...",
        "link": "https://www.hocusbogus.com/2022/05/08/foobar",
        "source": Source(**source_values),
        "created_at": timezone.localtime(),
    }


@pytest.fixture
def article_instance(article_values):
    return Article.objects.create(**article_values)


@pytest.fixture
def article_values_2(source_instance):
    return {
        "headline": "The moon is made of cheese",
        "slug": "the-moon-is-made-of-cheese",
        "body": "Consectetur adipiscing elit, sed do eiusmod tempor incididunt...",
        "link": "https://www.nonsensical.org/2022/05/08/baz",
        "source": source_instance,
        "created_at": timezone.localtime(),
    }


@pytest.fixture
def article_instance_2(article_values_2):
    return Article.objects.create(**article_values_2)


@pytest.fixture
def client():
    return Client()
