import json

from django.test import TestCase
from bs4 import BeautifulSoup  # type: ignore

from ..scraper.parser import find_headline, find_body, find_language, parse
from ..models import Source, PublicationType, Language


class TestParsers(TestCase):
    def setUp(self):
        self.html = "<html lang='en'><h1>Test Headline</h1><body>...</body><h2>Hello there!</h2></html>"
        self.html_2 = "<html lang='en'><h1>  Test Headline  </h1><body>...</body><h2>Hello there!</h2></html>"
        self.soup = BeautifulSoup(self.html, features="lxml")
        self.language = Language.objects.create(name="en")
        self.pubtype = PublicationType.objects.create(name="newspaper/journal")
        self.source = Source.objects.create(
            name="The Intercept",
            link="https://theintercept.com/",
            publication_type=self.pubtype,
            language=self.language,
            paths=["world/"],
            javascript=False,
            regex="[0-9]{4}/[0-9]{2}/[0-9]{2}",
            headline={"tag": "h1", "attrs": {}},
            body={"tag": "h2", "attrs": {}},
        )
        self.sitemap = self.source.to_dict()
        self.url = "https://theintercept.com"

    def test_find_headline(self):
        headline = find_headline(self.soup, self.sitemap, self.url)
        self.assertEqual(headline, "Test Headline")

    def test_find_body(self):
        body = find_body(self.soup, self.sitemap, self.url)
        self.assertEqual(body, "Hello there!")

    def test_find_language(self):
        language = find_language(self.soup, self.url)
        self.assertEqual(language, "en")

    def test_parse(self):
        json_data = json.loads(parse(self.html, self.sitemap, self.url))
        self.assertEqual(json_data["headline"], "Test Headline")
        self.assertEqual(json_data["body"], "Hello there!")
        self.assertEqual(json_data["language"], "en")
        self.assertEqual(json_data["link"], self.url)
        self.assertEqual(json_data["source_link"], self.source.link)
