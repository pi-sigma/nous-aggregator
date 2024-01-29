import asyncio
import logging
import random
from http.cookiejar import DefaultCookiePolicy

import pyppeteer
import requests
from django.conf import settings
from requests_html import AsyncHTMLSession, HTMLResponse
from websockets.exceptions import ConnectionClosedError

from . import headers, parser

logger = logging.getLogger(__name__)


class Spider:
    """
    Class Attributes:
        headers (list): a collection of HTTP headers

    Instance Attributes:
        sitemap (dict): contains information about a particular page
        starting_urls (list): the urls where each Spider object searches for
            links
        links (set): urls of pages targeted for scraping
        articles (set): a collection of JSON strings representing article
            metadata
    """

    headers = headers.headers

    def __init__(self, starting_urls: list, sitemap: dict):
        self.sitemap = sitemap
        self.starting_urls = starting_urls
        self.links: set[str] = set()
        self.articles: set[str] = set()

    @staticmethod
    async def connect(asession: AsyncHTMLSession, url: str) -> HTMLResponse | None:
        """GET request wrapper"""
        try:
            response = await asession.get(
                url,
                headers=random.choice(Spider.headers),  # nosec
                timeout=settings.REQUESTS_TIMEOUT,
            )
        except requests.exceptions.RequestException as e:
            logger.error("Could not fetch %s (%s)", url, e)
            return None
        return response

    async def get_links(self, asession: AsyncHTMLSession, url: str):
        response = await Spider.connect(asession, url)
        if not response:
            return

        if self.sitemap["javascript_required"]:
            try:
                await response.html.arender(timeout=settings.REQUESTS_TIMEOUT)
            except pyppeteer.errors.TimeoutError as e:
                logger.error("Could not render JavaScript for %s (%s)", url, e)
        for link in response.html.absolute_links:
            if self.sitemap["filter"].search(link):
                self.links.add(link)

    async def scrape(self, asession: AsyncHTMLSession, url: str):
        response = await Spider.connect(asession, url)
        if not response:
            return

        html = response.text
        article = parser.parse(html, self.sitemap, url)
        if article:
            self.articles.add(article)

    async def collect_links(self, asession: AsyncHTMLSession):
        """
        Create & gather tasks for collection of links
        """
        coros = [self.get_links(asession, url) for url in self.starting_urls]
        await asyncio.gather(*coros)

    async def collect_metadata(self, asession: AsyncHTMLSession):
        """
        Create & gather tasks for scraping
        """
        coros = [self.scrape(asession, link) for link in self.links]
        await asyncio.gather(*coros)


def run(spider: Spider):
    """
    Run `spider` with async HTML session inside event loop
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asession = AsyncHTMLSession()
    asession.cookies.set_policy(DefaultCookiePolicy(allowed_domains=[]))
    try:
        loop.run_until_complete(spider.collect_links(asession))
        loop.run_until_complete(spider.collect_metadata(asession))
    except ConnectionClosedError as ex:
        logger.warning("Connection closed", exc_info=ex)
