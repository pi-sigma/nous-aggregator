import asyncio
import logging
import random

import aiohttp  # pyre-ignore
from aiohttp import ClientSession
from aiohttp.web_exceptions import HTTPError

from . import headers, parser

logger: logging.Logger = logging.getLogger(__name__)


class Spider:
    """
    Class Attributes:
        headers (list): a collection of HTTP headers

    Instance Attributes:
        sitemap (dict): contains information about a particular page
        starting_urls (list): the urls where each `Spider` instance searches for
            links
        links (set): urls of pages targeted for scraping
        articles (set): a collection of JSON strings representing article
            metadata
    """

    headers = headers.headers

    def __init__(self, starting_urls: list[str], sitemap: dict) -> None:
        self.sitemap: dict = sitemap
        self.starting_urls: list[str] = starting_urls
        self.links: set[str] = set()
        self.articles: set[str] = set()

    async def connect(self, session: ClientSession, url: str) -> str | None:  # pyre-ignore
        headers = random.choice(self.headers)

        try:
            async with session.get(url, headers=headers) as response:
                html = await response.text()
        except HTTPError as exc:
            logger.error("Could not fetch %s", url, exc_info=exc)
            return None
        return html

    async def get_links(self, session: ClientSession, url: str) -> list[str] | None:
        html = await self.connect(session=session, url=url)
        if not html:
            return None

        for link in parser.generate_filtered_links(html=html, sitemap=self.sitemap):
            self.links.add(link)

    async def scrape(self, session: ClientSession, link: str) -> str | None:
        html = await self.connect(session=session, url=link)
        if not html:
            return None

        article = parser.parse(html, sitemap=self.sitemap, url=link)
        if not article:
            return None

        self.articles.add(article)

    async def collect_links(self, session: ClientSession, starting_urls: list[str]) -> None:
        coros = (self.get_links(session, url) for url in starting_urls)
        await asyncio.gather(*coros)

    async def collect_metadata(self, session: ClientSession, links: set[str]) -> None:
        coros = (self.scrape(session, link) for link in links)
        await asyncio.gather(*coros)

    async def main(self) -> None:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(60),
        ) as session:
            await self.collect_links(session, self.starting_urls)
            await self.collect_metadata(session, self.links)

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.main())
