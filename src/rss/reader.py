import logging
import random
from typing import TYPE_CHECKING

import requests
from requests.exceptions import RequestException

from utils.data_structures import hashabledict

from . import parser

if TYPE_CHECKING:
    from .typing import Feed

logger = logging.getLogger(__name__)


class Reader:
    """
    Instance Attributes:
        feeds (list): a list of RSS feeds
        headers (list): a collection of HTTP headers
        time_delta (int): the maximum age (in minutes) of articles to be
            collected
        articles (set): a collection of dicts representing article
            metadata
    """

    def __init__(self, feeds: list["Feed"], headers: list[dict], time_delta: int):
        self.feeds = feeds
        self.headers = headers
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

    def get_articles(self, session: requests.Session, feed: "Feed") -> list[hashabledict]:
        content = self.connect(session, feed.url)
        if not content:
            return None

        articles = parser.parse(content, self.time_delta)
        return articles

    def get_feeds(self):
        with requests.Session() as session:
            for feed in self.feeds.all():
                articles = self.get_articles(session, feed)
                for article in articles:
                    self.articles.add(article)
