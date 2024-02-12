import json
from pathlib import Path

import pytest
from requests_html import AsyncHTMLSession

from scraper.spiders import Spider

from ..utils import read_file

FILES_DIR = Path(__file__).parent.parent.resolve() / "files" / "articles" / "aj"


@pytest.mark.asyncio
async def test_collect_links(starting_urls_aj, sitemap_aj, requests_mock):
    spider = Spider(starting_urls_aj, sitemap_aj)
    spider.asession = AsyncHTMLSession()

    html = read_file(directory=FILES_DIR, file_name="_start.html")

    requests_mock.get(starting_urls_aj[0], text=html)

    await spider.collect_links()

    assert len(spider.links) == 12


@pytest.mark.asyncio
async def test_collect_metadata(
    starting_urls_aj, sitemap_aj, expected_aj, requests_mock
):
    #
    # setup
    #
    spider = Spider(starting_urls_aj, sitemap_aj)
    spider.links = ["https://indonesia.com", "https://taiwan.com"]
    spider.asession = AsyncHTMLSession()

    html_indonesia = read_file(directory=FILES_DIR, file_name="indonesia.html")
    html_taiwan = read_file(directory=FILES_DIR, file_name="taiwan.html")

    requests_mock.get("https://indonesia.com", text=html_indonesia)
    requests_mock.get("https://taiwan.com", text=html_taiwan)

    #
    # asserts
    #
    await spider.collect_metadata()

    articles = [json.loads(article) for article in spider.articles]

    assert len(articles) == 2

    article_indonesia = next(
        (article for article in articles if article["url"] == "https://indonesia.com")
    )

    assert article_indonesia["headline"] == expected_aj["indonesia"]["headline"]
    assert article_indonesia["slug"] == expected_aj["indonesia"]["slug"]
    assert article_indonesia["summary"] == expected_aj["indonesia"]["summary"]
    assert article_indonesia["language"] == expected_aj["indonesia"]["language"]

    article_taiwan = next(
        (article for article in articles if article["url"] == "https://taiwan.com")
    )

    assert article_taiwan["headline"] == expected_aj["taiwan"]["headline"]
    assert article_taiwan["slug"] == expected_aj["taiwan"]["slug"]
    assert article_taiwan["summary"] == expected_aj["taiwan"]["summary"]
    assert article_indonesia["language"] == expected_aj["taiwan"]["language"]
