import logging
import random

import requests
from requests.exceptions import RequestException

from articles.models import Feed
from scraper import headers
from utils.data_structures import hashabledict

from . import parser

logger = logging.getLogger(__name__)


class Reader:
    """
    Class Attributes:
        headers (list): a collection of HTTP headers

    Instance Attributes:
        feeds (list): a list of RSS feeds
        time_delta (int): the maximum age (unit agnostic) of articles to be
            collected
        articles (set): a collection of dicts representing article
            metadata
    """

    headers = headers

    def __init__(self, feeds: list[Feed], time_delta: int):
        self.feeds = feeds
        self.time_delta = time_delta
        self.articles: set[dict] = set()

    def connect(self, session: requests.Session, url: str) -> str | None:
        headers = random.choice(self.headers)  # nosec

        try:
            with session.get(url, headers=headers) as response:
                content = response.content
        except RequestException as exc:
            logger.error("Could not fetch %s", url, exc_info=exc)
            return None
        return content

    def get_articles(self, session: requests.Session, feed: Feed) -> list[hashabledict]:
        content = self.connect(session, feed.url)
        if not content:
            return None

        articles = parser.parse(content, self.time_delta)
        return articles

    def get_feed(self):
        with requests.Session() as session:
            for feed in self.feeds.all():
                articles = self.get_articles(session, feed)
                for article in articles:
                    self.articles.add(article)
