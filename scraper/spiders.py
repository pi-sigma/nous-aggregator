import asyncio
import logging
import random
from http.cookiejar import DefaultCookiePolicy

import pyppeteer
import requests
from django.conf import settings
from requests_html import AsyncHTMLSession, HTMLResponse
from websockets.exceptions import ConnectionClosedError  # pyre-ignore

from . import headers, parser

logger = logging.getLogger(__name__)


class Spider:
    """
    Class Attributes:
        headers (list): a collection of HTTP headers

    Instance Attributes:
        event_loop: the event loop is explicitly set on the `Spider` instance and
            passed to the requests session in order to minimize the risk of
            attaching Futures to different event loops by accident
        asession (AsyncHTMLSession): requests session that supports asynchronous
            requests
        sitemap (dict): contains information about a particular page
        starting_urls (list): the urls where each `Spider` instance searches for
            links
        links (set): urls of pages targeted for scraping
        articles (set): a collection of JSON strings representing article
            metadata
    """

    headers = headers.headers

    def __init__(self, starting_urls: list[str], sitemap: dict):
        self.event_loop = asyncio.get_event_loop()
        self.asession = AsyncHTMLSession(loop=self.event_loop)
        self.sitemap: dict = sitemap
        self.starting_urls: list[str] = starting_urls
        self.links: set[str] = set()
        self.articles: set[str] = set()

        @property
        def asession(self):
            return self._asession

        @asession.setter
        def asession(self, asession: AsyncHTMLSession):
            self._asession = asession
            self._asession.cookies.set_policy(DefaultCookiePolicy(allowed_domains=[]))

    async def connect(self, url: str) -> HTMLResponse | None:
        """GET request wrapper"""
        try:
            response = await self.asession.get(  # pyre-ignore
                url,
                headers=random.choice(self.headers),  # nosec
                timeout=settings.REQUESTS_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            logger.error("Could not fetch %s (%s)", url, e)
            return None
        return response

    async def get_links(self, url: str) -> None:
        response = await self.connect(url)
        if not response:
            return

        if self.sitemap["javascript_required"]:
            try:
                await response.html.arender()
            except pyppeteer.errors.TimeoutError as e:
                logger.error("Could not render JavaScript for %s (%s)", url, e)
        for link in response.html.absolute_links:
            if self.sitemap["filter"].search(link):
                self.links.add(link)

    async def scrape(self, url: str) -> None:
        response = await self.connect(url)
        if not response:
            return

        html = response.text
        article = parser.parse(html, self.sitemap, url)
        if article:
            self.articles.add(article)

    async def collect_links(self) -> None:
        """
        Create & gather tasks for collection of links
        """
        coros = [self.get_links(url) for url in self.starting_urls]
        await asyncio.gather(*coros)

    async def collect_metadata(self) -> None:
        """
        Create & gather tasks for scraping
        """
        coros = [self.scrape(link) for link in self.links]
        await asyncio.gather(*coros)

    def run(self):
        """
        Run the `spider` instance inside the event loop
        """
        try:
            self.event_loop.run_until_complete(self.collect_links())
            self.event_loop.run_until_complete(self.collect_metadata())
        except ConnectionClosedError as ex:
            logger.warning("Connection closed", exc_info=ex)
