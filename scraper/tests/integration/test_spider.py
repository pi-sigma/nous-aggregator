import json
from pathlib import Path

import pytest

import scraper
from scraper.spiders import Spider

from ..utils import read_file

FILES_DIR = Path(__file__).parent.parent.resolve() / "files" / "articles" / "aj"


#
# fixtures
#
@pytest.fixture
def contents():
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
def test_run_spider(starting_urls_aj, sitemap_aj, contents, expected_aj, requests_mock):
    spider = Spider(starting_urls_aj, sitemap_aj)

    for item in contents.values():
        requests_mock.get(item["link"], text=item["content"])

    spider.run()

    articles = [json.loads(article) for article in list(spider.articles)]

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
