import json
from pathlib import Path
from typing import Any, Dict

import pytest
from django.utils.text import slugify

from articles.constants import Language, PublicationType
from articles.models import Source
from scraper.spiders import Spider

from ..mocks import MockResponse
from ..utils import read_file

FILES_DIR: Path = Path(__file__).parent.parent.resolve() / "files" / "articles" / "aj"


#
# fixtures
#
@pytest.fixture
def source():
    return Source(
        title="Al Jazeera",
        slug=slugify("Al Jazeera"),
        publication_type=PublicationType.newspaper,
        language=Language.en,
        url="https://www.aljazeera.com/",
        paths=["news/"],
        regex="(?<!liveblog)/[0-9]{4}/[0-9]+/[0-9]+/(?!.*terms-and-conditions/|.*community-rules-guidelines/|.*eu-eea-regulatory|.*code-of-ethics|.*liveblog)",
        javascript_required=False,
        headline_selectors={'tag': 'h1', 'attrs': {}},
        summary_selectors={'tag': 'p', 'attrs': {'class': 'article__subhead'}},
    )


@pytest.fixture
def contents() -> Dict[str, Dict[str, Any]]:
    contents = {
        "_start": {
            "link": "https://www.aljazeera.com/news/",
            "content": read_file(directory=FILES_DIR, file_name="_start.html"),
        },
        "asian_cup": {
            "link":  "https://www.aljazeera.com/news/2024/2/10/football-fever-hits-"
                     "jordan-ahead-of-historic-asian-cup-final",
            "content": read_file(directory=FILES_DIR, file_name="asian_cup.html"),
        },
        "football": {
            "link": "https://www.aljazeera.com/sports/2024/2/10/football-fans-souq-waqif",
            "content": read_file(directory=FILES_DIR, file_name="football.html"),
        },
        "footprints": {
            "link": "https://www.aljazeera.com/news/2024/2/10/what-newly-found-"
                      "90000-year-old-footprints-say-about-early-humans",
            "content": read_file(directory=FILES_DIR, file_name="footprints.html"),
        },
        "girl": {
            "link": "https://www.aljazeera.com/news/2024/2/10/body-of-6-year-old-killed-"
                    "in-deliberate-israeli-fire-found-after-12-days",
            "content": read_file(directory=FILES_DIR, file_name="girl.html"),
        },
        "indonesia": {
            "link": "https://www.aljazeera.com/news/2024/2/10/big-election-rallies-"
                    "in-indonesia-on-final-day-of-campaign",
            "content": read_file(directory=FILES_DIR, file_name="indonesia.html"),
        },
        "israel": {
            "link": "https://www.aljazeera.com/gallery/2024/2/10/photos-israel-bombs-"
                    "homes-in-central-gaza-killing-several-families",
            "content": read_file(directory=FILES_DIR, file_name="israel.html"),
        },
        "israel2": {
            "link": "https://www.aljazeera.com/news/2024/2/10/israeli-military-kills-"
                    "28-after-netanyahu-signals-rafah-invasion-plan",
            "content": read_file(directory=FILES_DIR, file_name="israel2.html"),
        },
        "lunar": {
            "link": "https://www.aljazeera.com/news/2024/2/10/lunar-new-year-2024-"
                   "explained-in-five-emblematic-dishes",
            "content": read_file(directory=FILES_DIR, file_name="lunar.html"),
        },
        "resistence": {
            "link": "https://www.aljazeera.com/news/2024/2/10/analysis-who-is-the-"
                    "islamic-resistance-in-iraq",
            "content": read_file(directory=FILES_DIR, file_name="resistance.html"),
        },
        "russia": {
            "link": "https://www.aljazeera.com/news/2024/2/10/overnight-russian-drone-"
                    "attack-kills-at-least-seven-in-ukraines-kharkiv",
            "content": read_file(directory=FILES_DIR, file_name="russia.html"),
        },
        "student": {
            "link": "https://www.aljazeera.com/news/2024/2/10/student-killed-in-senegal-"
                    "protests-over-election-delay",
            "content": read_file(directory=FILES_DIR, file_name="student.html"),
        },
        "taiwan": {
            "link": "https://www.aljazeera.com/news/2024/2/10/how-taiwans-elections-"
                    "challenge-the-power-of-chinas-communist-party",
            "content": read_file(directory=FILES_DIR, file_name="taiwan.html"),
        }
    }
    return contents


#
# tests
#
@pytest.mark.django_db
def test_run_spider(source, contents, expected_aj, mocker) -> None:
    #
    # setup
    #
    def return_value(*args, **kwargs):
        for k, v in contents.items():
            if args[0] == v["link"]:
                return MockResponse(text=v["content"])

    mocker.patch("aiohttp.ClientSession.get", side_effect=return_value)

    #
    # asserts
    #
    sitemap = source.to_dict()
    starting_urls = [
        sitemap["base_url"] + path for path in sitemap["paths"]
    ]
    spider = Spider(starting_urls, sitemap)

    spider.run()

    articles = [json.loads(article) for article in spider.articles]

    assert len(articles) == 12

    for expected_data in expected_aj.values():
        article = next(
            (article for article in articles if article["headline"] == expected_data["headline"])
        )
        assert article["slug"] == expected_data["slug"]
        assert article["summary"] == expected_data["summary"]
        assert article["language"] == expected_data["language"]
        assert article["url"] == expected_data["url"]
        assert article["source_link"] == expected_data["source_link"]
