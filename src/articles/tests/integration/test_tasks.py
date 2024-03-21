import pytest
from django.conf import settings
from django.core.management import call_command

from articles.models import Article
from articles.tasks import get_articles_for_source
from scraper.tests import AsyncMockResponse, contents_aj, expected_aj

SOURCE_TITLE = "Al Jazeera"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "db.example.com",
        "NAME": "test_db",
        "ATOMIC_REQUESTS": True,
    }

    with django_db_blocker.unblock():
        call_command("loaddata", "fixtures/sources_test.json")


@pytest.mark.usefixtures("celery_session_app")
@pytest.mark.usefixtures("celery_session_worker")
@pytest.mark.django_db
def test_get_articles_for_source(contents_aj, expected_aj, mocker):
    # setup
    def return_value(*args, **kwargs):
        for key, value in contents_aj.items():
            if args[0] == value["link"]:
                return AsyncMockResponse(text=value["content"])

    mocker.patch("aiohttp.ClientSession.get", side_effect=return_value)

    # asserts
    promise = get_articles_for_source.delay(SOURCE_TITLE)
    promise.get()

    articles = Article.objects.all()

    assert len(articles) == 12

    for expected_data in expected_aj.values():
        article = next(
            (article for article in articles if article.headline == expected_data["headline"])
        )
        assert article.slug == expected_data["slug"]
        assert article.summary == expected_data["summary"]
        assert article.language == expected_data["language"]
        assert article.url == expected_data["url"]
        assert article.source.title == SOURCE_TITLE
