import json
from pathlib import Path

import pytest
from pyquery import PyQuery

from scraper.parser import find_headline, find_language, find_summary, parse

from ..utils import read_file

FILES_DIR: Path = Path(__file__).parent.parent.resolve() / "files" / "articles" / "aj"


URL_ASIAN_CUP = "https://www.aljazeera.com/sports/2024/2/10/football-fans-souq-waqif"
URL_INDONESIA = "https://www.aljazeera.com/news/2024/2/10/big-election-rallies-in-indonesia-on-final-day-of-campaign"
URL_TAIWAN = "https://www.aljazeera.com/news/2024/2/10/how-taiwans-elections-challenge-the-power-of-chinas-communist-party"


@pytest.mark.parametrize("page", ["asian_cup", "indonesia", "taiwan"])
def test_find_headline(sitemap_aj, expected_aj, page) -> None:
    html = read_file(directory=FILES_DIR, file_name=f"{page}.html")
    doc = PyQuery(html)

    headline_text = find_headline(doc, sitemap_aj, url="dummy")

    assert headline_text == expected_aj[f"{page}"]["headline"]


@pytest.mark.parametrize("page", ["asian_cup", "indonesia", "taiwan"])
def test_find_summary(sitemap_aj, expected_aj, page) -> None:
    html = read_file(directory=FILES_DIR, file_name=f"{page}.html")
    doc = PyQuery(html)

    summary = find_summary(doc, sitemap_aj, url="https://www.example.com")

    assert summary
    assert summary == expected_aj[f"{page}"]["summary"]


@pytest.mark.parametrize("page", ["asian_cup", "indonesia", "taiwan"])
def test_find_language(sitemap_aj, expected_aj, page) -> None:
    html = read_file(directory=FILES_DIR, file_name=f"{page}.html")
    doc = PyQuery(html)

    headline = find_headline(doc, sitemap_aj, url="dummy")
    summary = find_summary(doc, sitemap_aj, url="https://www.example.com")

    assert headline
    assert summary

    lang = find_language(summary, headline, doc, url="dummy")

    assert lang == expected_aj[f"{page}"]["language"]


@pytest.mark.parametrize(
    "page, url",
    [("asian_cup", URL_ASIAN_CUP), ("indonesia", URL_INDONESIA), ("taiwan", URL_TAIWAN)]
)
def test_parse(sitemap_aj, expected_aj, page, url) -> None:
    html = read_file(directory=FILES_DIR, file_name=f"{page}.html")

    json_data = parse(html, sitemap_aj, url=url)

    assert json_data

    data = json.loads(json_data)

    assert data
    assert data == expected_aj[f"{page}"]
