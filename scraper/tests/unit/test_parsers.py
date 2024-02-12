import json
from pathlib import Path

from bs4 import BeautifulSoup

from scraper.parser import find_headline, find_language, find_summary, parse

from ..utils import read_file

FILES_DIR = Path(__file__).parent.parent.resolve() / "files" / "articles" / "aj"

PAGE = "indonesia"
URL = "https://www.aljazeera.com/news/2024/2/10/big-election-rallies-in-indonesia-on-final-day-of-campaign"


def test_find_headline(sitemap_aj, expected_aj):
    html = read_file(directory=FILES_DIR, file_name=f"{PAGE}.html")
    soup = BeautifulSoup(html, "lxml")

    headline_text = find_headline(soup, sitemap_aj, url="dummy")

    assert headline_text == expected_aj[f"{PAGE}"]["headline"]


def test_find_summary(sitemap_aj, expected_aj):
    html = read_file(directory=FILES_DIR, file_name=f"{PAGE}.html")
    soup = BeautifulSoup(html, "lxml")

    summary = find_summary(soup, sitemap_aj, url="https://www.example.com")

    assert summary == expected_aj[f"{PAGE}"]["summary"]


def test_find_language(sitemap_aj, expected_aj):
    html = read_file(directory=FILES_DIR, file_name=f"{PAGE}.html")
    soup = BeautifulSoup(html, "lxml")

    lang = find_language(soup, url="dummy")

    assert lang == expected_aj[f"{PAGE}"]["language"]


def test_parse(sitemap_aj, expected_aj):
    html = read_file(directory=FILES_DIR, file_name=f"{PAGE}.html")

    json_data = parse(html, sitemap_aj, url=URL)
    data = json.loads(json_data)

    assert data == expected_aj[f"{PAGE}"]
