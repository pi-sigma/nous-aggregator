from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree

import dateutil
from django.utils.text import slugify

from utils.data_structures import hashabledict

from .constants import tzinfos


def parse(content: str, time_delta: int) -> list[hashabledict]:
    """Parse the content of an RSS feed and return article metadata

    Args:
        content: XML string with RSS feed content
        time_delta: number representing the max age (in minutes) of
            articles

    Returns:
        Collection of hashable dicts with article metadata
    """
    response_xml = ElementTree.fromstring(content)

    channel = response_xml.find("./channel")
    articles = channel.findall("item")

    data = []

    for article in articles:
        # 1. title
        title = article.find("title").text

        # 2. url
        url = article.find("link").text

        # 3. date (skip old entries)
        pubdate_string = article.find("pubDate").text
        pubdate = dateutil.parser.parse(pubdate_string, tzinfos=tzinfos)
        now_utc = datetime.now(timezone.utc)
        delta = timedelta(minutes=time_delta)

        if now_utc - pubdate > delta:
            continue

        # 4. description
        description = article.find("description").text

        # 5. creators
        ns = {"dc": "http://purl.org/dc/articleents/1.1/"}
        if creators := article.find(".//dc:creator", ns):
            creators = creators.text

        # 6. language
        language = channel.find("language").text

        article_dict = hashabledict(
            title=title,
            slug=slugify(title),
            url=url,
            pubdate=pubdate,
            description=description,
            creators=creators or "",
            language=language,
        )

        data.append(article_dict)

    return data
