from datetime import datetime
from typing import Dict, Union

import pytest
from django.test import Client
from django.utils import timezone

from ..constants import Language, PublicationType
from ..models import Article, Source


@pytest.fixture
def source_values():
    return {
        "title": "Fake News",
        "slug": "fake-news",
        "url": "https://www.hocusbogus.com/",
        "publication_type": PublicationType.newspaper,
        "language": Language.en,
        "paths": ["world/"],
        "javascript_required": False,
        "regex": "[0-9]{4}/[0-9]{2}/[0-9]{2}",
        "headline_search_params_find": "h1",
        "headline_search_params_remove": [],
        "summary_search_params_find": "",
        "summary_search_params_remove": []
    }


@pytest.fixture
def source_instance(source_values):
    return Source.objects.create(**source_values)


@pytest.fixture
def source_values_2():
    return {
        "title": "Alternative Facts",
        "slug": "alternative-facts",
        "url": "https://www.nonsensical.org/",
        "publication_type": PublicationType.newspaper,
        "language": Language.en,
        "paths": ["world/"],
        "javascript_required": False,
        "regex": "[0-9]{4}/[0-9]{2}/[0-9]{2}",
        "headline_search_params_find": "h1",
        "headline_search_params_remove": [],
        "summary_search_params_find": "",
        "summary_search_params_remove": []
    }


@pytest.fixture
def source_instance_2(source_values_2):
    return Source.objects.create(**source_values_2)


@pytest.fixture
def article_values(source_instance) -> Dict[str, Union[datetime, str]]:
    return {
        "headline": "A cow jumps over the moon",
        "slug": "a-cow-jumps-over-the-moon",
        "summary": "Lorem dolor sit amet...",
        "url": "https://www.hocusbogus.com/2022/05/08/foobar",
        "source": source_instance,
        "created_at": timezone.localtime(),
    }


@pytest.fixture
def article_values_m(source_values) -> Dict[str, Union[Source, datetime, str]]:
    return {
        "headline": "A cow jumps over the moon",
        "slug": "a-cow-jumps-over-the-moon",
        "summary": "Lorem dolor sit amet...",
        "url": "https://www.hocusbogus.com/2022/05/08/foobar",
        "source": Source(**source_values),
        "created_at": timezone.localtime(),
    }


@pytest.fixture
def article_instance(article_values):
    return Article.objects.create(**article_values)


@pytest.fixture
def article_values_2(source_instance) -> Dict[str, Union[datetime, str]]:
    return {
        "headline": "The moon is made of cheese",
        "slug": "the-moon-is-made-of-cheese",
        "summary": "Consectetur adipiscing elit, sed do eiusmod tempor incididunt...",
        "url": "https://www.nonsensical.org/2022/05/08/baz",
        "source": source_instance,
        "created_at": timezone.localtime(),
    }


@pytest.fixture
def article_instance_2(article_values_2):
    return Article.objects.create(**article_values_2)


@pytest.fixture
def client() -> Client:
    return Client()
