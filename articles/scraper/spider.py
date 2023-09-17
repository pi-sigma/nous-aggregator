import asyncio
import logging
import random
from typing import Optional

import pyppeteer
import requests
from django.conf import settings
from requests_html import AsyncHTMLSession, HTMLResponse
from websockets.exceptions import ConnectionClosedError

from . import headers, parser

logger = logging.getLogger(__name__)


class Spider:
    """
    The Spider class is for extracting article metadata.

    Class Attributes:
        headers (list): a collection of HTTP headers
        articles (set): a collection of JSON strings representing article
            metadata

    Instance Attributes:
        sitemap (dict): contains information about a particular page
        starting_urls (list): the urls where each Spider object searches for
            links
        links (set): urls of pages targeted for scraping

    Public Methods:
        crawl(sitemap): the main method of the Spider class; called from the
            scheduler which supplies the argument `sitemap`; creates a spider
            object for `sitemap` and runs the event loop.
    """

    headers = headers.headers
    articles: set[str] = set()

    def __init__(self, sitemap: dict):
        self.sitemap = sitemap
        self.starting_urls = [
            self.sitemap["base_url"] + path for path in self.sitemap["paths"]
        ]
        self.links: set[str] = set()

    @staticmethod
    async def connect(asession: AsyncHTMLSession, url: str) -> Optional[HTMLResponse]:
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
        """
        Get all article links at `url` and filter them
        """
        response = await Spider.connect(asession, url)
        if not response:
            return

        if self.sitemap["javascript"]:
            try:
                await response.html.arender(timeout=settings.REQUESTS_TIMEOUT_JS)
            except pyppeteer.errors.TimeoutError as e:
                logger.error("Could not render JavaScript for %s (%s)", url, e)
        for link in response.html.absolute_links:
            if self.sitemap["filter"].search(link):
                self.links.add(link)

    async def scrape(self, asession: AsyncHTMLSession, url: str):
        """
        Scrape the page at `url` and store data
        """
        response = await Spider.connect(asession, url)
        if not response:
            return

        html = response.text
        article = parser.parse(html, self.sitemap, url)
        if article:
            Spider.articles.add(article)

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

    @staticmethod
    def crawl(sitemap: dict):
        """
        Create spider instance and run the event loop
        """
        spider = Spider(sitemap)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        asession = AsyncHTMLSession()
        try:
            loop.run_until_complete(spider.collect_links(asession))
            loop.run_until_complete(spider.collect_metadata(asession))
        except ConnectionClosedError:
            logger.warning("Connection closed.")
