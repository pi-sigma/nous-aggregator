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


def find_title(doc: PyQuery, sitemap: dict, url: str) -> Optional[str]:
    """ Use `doc` + `sitemap` to extract headline from article at `url` """

    search_params = sitemap["search_params"]["title"]

    if not search_params.get("find", ""):
        logger.warning("No search params for title of %s", url)
        return None

    # TODO: error handling; except cssselect.SelectorSyntaxError
    for param in search_params["find"]:
        if title_doc := doc.find(param):
            break

    if not title_doc:
        return None

    if remove_params := search_params.get("remove", []):
        for item in remove_params:
            title_doc(f"{item}").remove()

    try:
        title_text = title_doc.text().strip()
    except AttributeError:
        return None

    return title_text


def find_description(doc: PyQuery, sitemap: dict, url: str) -> Optional[str]:
    """ Use `doc` + `sitemap` to extract summary from article at `url` """

    search_params = sitemap["search_params"]["description"]

    if not search_params.get("find", ""):
        logger.warning("No search params for summary of %s", url)
        return None

    for param in search_params["find"]:
        if description_doc := doc.find(param):
            break

    if not description_doc:
        return None

    if remove_params := search_params.get("remove", []):
        for item in remove_params:
            description_doc(f"{item}").remove()

    try:
        description_text = description_doc.text().strip()
    except AttributeError:
        return None

    return description_text[:1000]


def find_language(description: str, title: str, doc: PyQuery, url: str) -> Optional[str]:
    """ Detect the language of the page at `url` """

    for item in (description, title, doc.text()):
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

    title = find_title(doc, sitemap=sitemap, url=url)
    if title is None:
        logger.warning("No title for %s", url)
        return None

    description = find_description(doc, sitemap=sitemap, url=url)
    if description is None:
        logger.warning("Missing summary for %s", url)
        description = "No description"

    language = find_language(description, title, doc, url)
    if language is None:
        language = sitemap["language"]

    article = {
        "title": title,
        "slug": slugify(title),
        "description": description,
        "language": language,
        "url": url,
        "source_link": sitemap["base_url"],
    }
    json_data = json.dumps(article)
    return json_data
