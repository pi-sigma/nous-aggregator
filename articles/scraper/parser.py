import json
import logging
from typing import Optional

import langdetect  # type: ignore
from bs4 import BeautifulSoup  # type: ignore
from django.utils.text import slugify

logger = logging.getLogger(__name__)


def find_headline(soup: BeautifulSoup, sitemap: dict, url: str) -> Optional[str]:
    """Use `sitemap` to extract headline from article"""

    try:
        headline = soup.find(
            sitemap["headline_selectors"]["tag"],
            attrs=sitemap["headline_selectors"]["attrs"],
        )
    except KeyError as e:
        logger.error("KeyError (%s) for headline of %s", e, url)
        raise KeyError from e  # Abort job after logging error
    if headline is None:
        return None
    headline_text = headline.get_text().strip()
    return headline_text


def find_summary(soup: BeautifulSoup, sitemap: dict, url: str) -> Optional[str]:
    """Use `parser` & `sitemap` to extract summary from article"""

    if sitemap["summary_selectors"] is None:
        return None

    try:
        summary = soup.find(
            sitemap["summary_selectors"]["tag"],
            attrs=sitemap["summary_selectors"]["attrs"],
        )
    except KeyError as e:
        logger.error("KeyError (%s) for summary of %s", e, url)
        summary = None  # Continue job, set `summary` to avoid UnboundLocalError
    if summary is None:
        logger.warning("Missing summary for %s", url)
        return None
    summary_text = summary.get_text().strip()
    return summary_text


def find_language(soup: BeautifulSoup, url: str) -> Optional[str]:
    """Detect the language of the page at `url`."""

    if (body := soup.body) is None or (text := body.get_text()) is None:
        return None

    language = langdetect.detect(text)
    if language is None:
        logger.warning("Missing language for %s", url)
    return language


def parse(html: str, sitemap: dict, url: str) -> Optional[str]:
    """
    Parse the `html` at `url` with lxml, use html.parser as a fallback,
    return data as JSON. If html.parser fails to return a headline, return `None`
    (every article must have a headline); if the language does not match the one
    specified in `sitemap`, return `None`.
    """

    # try first parser
    parser = "lxml"
    soup = BeautifulSoup(html, parser)
    headline = find_headline(soup, sitemap, url)
    # try second parser
    if headline is None:
        parser = "html.parser"
        soup = BeautifulSoup(html, parser)
        headline = find_headline(soup, sitemap, url)
    if headline is None:
        logger.warning("No headline for %s", url)
        return None
    language = find_language(soup, url)
    if not language == sitemap["language"]:
        logger.warning(
            "Language of article (%s) + source (%s) do not match: %s",
            language,
            sitemap["language"],
            url,
        )
        return None
    summary = find_summary(soup, sitemap, url)
    article = {
        "headline": headline,
        "slug": slugify(headline),
        "summary": summary if summary else "No description",
        "language": language,
        "link": url,
        "source_link": sitemap["base_url"],
    }
    json_data = json.dumps(article)
    return json_data
