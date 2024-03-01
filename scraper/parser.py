import json
import logging
import urllib
from typing import Generator, Optional

import langdetect
from django.utils.text import slugify
from langdetect.lang_detect_exception import LangDetectException
from pyquery import PyQuery

logger: logging.Logger = logging.getLogger(__name__)


def generate_filtered_links(html: str, sitemap: dict) -> Generator[str, None, None]:
    doc = PyQuery(html)
    anchors = doc.find("a")

    for anchor in anchors:
        try:
            link = anchor.attrib["href"]
        except KeyError:
            pass
        else:
            if sitemap["filter"].search(link):
                yield urllib.parse.urljoin(sitemap["base_url"], link)


def find_headline(doc: PyQuery, sitemap: dict, url: str) -> Optional[str]:
    """ Use `doc` + `sitemap` to extract headline from article at `url` """

    search_params = sitemap["search_params"]["headline"]

    if not search_params.get("find", ""):
        logger.warning("No search params for headline of %s", url)
        return None

    for param in search_params["find"]:
        if headline_doc := doc.find(param):
            break

    if not headline_doc:
        return None

    for item in search_params.get("remove", []):
        headline_doc(f"{item}").remove()

    try:
        headline_text = headline_doc.text().strip()
    except AttributeError:
        return None

    return headline_text


def find_summary(doc: PyQuery, sitemap: dict, url: str) -> Optional[str]:
    """ Use `doc` + `sitemap` to extract summary from article at `url` """

    search_params = sitemap["search_params"]["summary"]

    if not search_params.get("find", ""):
        logger.warning("No search params for summary of %s", url)
        return None

    for param in search_params["find"]:
        if summary_doc := doc.find(param):
            break

    if not summary_doc:
        return None

    for item in search_params.get("remove", []):
        summary_doc(f"{item}").remove()

    try:
        summary_text = summary_doc.text().strip()
    except AttributeError:
        return None

    return summary_text[:1000]


def find_language(summary: str, headline: str, doc: PyQuery, url: str) -> Optional[str]:
    """ Detect the language of the page at `url` """

    for item in (summary, headline, doc.text()):
        if item:
            try:
                language = langdetect.detect(item)
            except LangDetectException as exc:
                logger.warning(
                    "Failed to detect language for %s", url, exc_info=exc
                )
            else:
                return language
    return None


def parse(html: str, sitemap: dict, url: str) -> Optional[str]:
    doc = PyQuery(html)

    headline = find_headline(doc, sitemap=sitemap, url=url)
    if headline is None:
        logger.warning("No headline for %s", url)
        return None

    summary = find_summary(doc, sitemap=sitemap, url=url)
    if summary is None:
        logger.warning("Missing summary for %s", url)
        summary = "No description"

    language = find_language(summary, headline, doc, url)
    if language is None:
        language = sitemap["language"]

    article = {
        "headline": headline,
        "slug": slugify(headline),
        "summary": summary,
        "language": language,
        "url": url,
        "source_link": sitemap["base_url"],
    }
    json_data = json.dumps(article)
    return json_data
