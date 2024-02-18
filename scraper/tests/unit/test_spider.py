import json
import logging
from pathlib import Path

import aiohttp  # pyre-ignore
import pytest
from aiohttp.web_exceptions import HTTPError

from scraper.spiders import Spider

from ..mocks import MockResponse
from ..utils import read_file

FILES_DIR: Path = Path(__file__).parent.parent.resolve() / "files" / "articles" / "aj"


@pytest.mark.asyncio
async def test_connect_error(starting_urls_aj, sitemap_aj, mocker, caplog):
    spider = Spider(starting_urls_aj, sitemap_aj)

    mocker.patch("aiohttp.ClientSession.get", side_effect=HTTPError)

    with caplog.at_level(logging.ERROR):
        async with aiohttp.ClientSession() as session:
            html = await spider.connect(session, starting_urls_aj[0])

            assert html is None

            assert len(caplog.messages) == 1
            assert caplog.messages[0] == f"Could not fetch {starting_urls_aj[0]}"


@pytest.mark.asyncio
async def test_collect_links(starting_urls_aj, sitemap_aj, mocker):
    spider = Spider(starting_urls_aj, sitemap_aj)
    html = read_file(directory=FILES_DIR, file_name="_start.html")

    mock_response = MockResponse(status_code=200, text=html)
    mocker.patch("aiohttp.ClientSession.get", return_value=mock_response)

    async with aiohttp.ClientSession() as session:
        await spider.collect_links(session, starting_urls_aj)

        assert len(spider.links) == 12


@pytest.mark.asyncio
async def test_collect_metadata(
    starting_urls_aj, sitemap_aj, expected_aj, mocker
) -> None:
    #
    # setup
    #
    spider = Spider(starting_urls_aj, sitemap_aj)
    spider.links = {"https://indonesia.com", "https://taiwan.com"}

    html_indonesia = read_file(directory=FILES_DIR, file_name="indonesia.html")
    html_taiwan = read_file(directory=FILES_DIR, file_name="taiwan.html")

    def return_value(*args, **kwargs):
        mock_response1 = MockResponse(status_code=200, text=html_indonesia)
        mock_response2 = MockResponse(status_code=200, text=html_taiwan)

        if args[0] == "https://indonesia.com":
            return mock_response1
        elif args[0] == "https://taiwan.com":
            return mock_response2

    mocker.patch("aiohttp.ClientSession.get", side_effect=return_value)

    #
    # asserts
    #
    await spider.collect_metadata(aiohttp.ClientSession(), spider.links)

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
