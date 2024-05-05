from datetime import datetime, timedelta, timezone
from xml.etree import ElementTree

# TODO: get from RSSMap
DELTA = timedelta(hours=1128)


def parse_from_content(content):
    response_xml = ElementTree.fromstring(content)

    articles = response_xml.findall("./channel/item")

    for elem in articles:
        # skip old entries
        pubDate = elem.find("pubDate").text
        # TODO: from RSSMap
        format_str = "%a, %d %b %Y %H:%M:%S %z"
        pubdate = datetime.strptime(pubDate, format_str)
        now_utc = datetime.now(timezone.utc)

        if now_utc - pubdate > DELTA:
            continue

        title = elem.find("title").text
        # TODO: from RSSMap
        url = elem.find("guid").text
        description = elem.find("description").text

        # TODO: investigate, perhaps get from RSSMap
        ns = {"dc": "http://purl.org/dc/elements/1.1/"}
        creators = elem.find(".//dc:creator", ns).text

        # TODO: return dict (or other DS)
        print(title)
        print(url)
        print(description)
        print(creators)
        print("\n")
