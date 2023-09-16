import json

from ..constants import Language
from ..models import Source
from ..scraper.parser import parse


def test_parse(source_values):
    html = (
        "<html lang='en'><h1>Headline of the article</h1><body>..."
        "</body><h2>Some text...</h2></html>"
    )
    source = Source(**source_values)
    sitemap = source.to_dict()
    url = "https://www.hocusbogus.com/"

    json_data = json.loads(parse(html, sitemap, url))

    assert json_data["headline"] == "Headline of the article"
    assert json_data["body"] == "Some text..."
    assert json_data["language"] == Language.en
    assert json_data["link"] == url
    assert json_data["source_link"] == source.link
