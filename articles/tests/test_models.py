import regex  # type: ignore
from django.test import TestCase
from django.utils import timezone

from ..models import Article
from ..models import Language
from ..models import PublicationType
from ..models import Source


class PublicationTypeTest(TestCase):
    def setUp(self):
        self.pub_type = PublicationType.objects.create(name="newspaper/journal")

    def test_pubtype_content(self):
        self.assertEqual(self.pub_type.name, "newspaper/journal")

    def test_pubtype_str_representation(self):
        self.assertEqual(str(self.pub_type), "newspaper/journal")


class LanguageTest(TestCase):
    def setUp(self):
        self.language = Language.objects.create(name="en")

    def test_pubtype_content(self):
        self.assertEqual(self.language.name, "en")

    def test_pubtype_str_representation(self):
        self.assertEqual(str(self.language), "en")


class SourceTest(TestCase):
    def setUp(self):
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
        self.source2 = Source.objects.create(
            name="Associated Press",
            link="https://apnews.com/",
            publication_type=self.pubtype,
            language=self.language,
            paths=["hub/world-news/", "hub/business/"],
            javascript=False,
            regex="article/",
            headline={"tag": "h1", "attrs": {}},
            body={"tag": "div", "attrs": {"class": "Article"}},
        )

    def test_source_content(self):
        self.assertEqual(self.source.name, "The Intercept")
        self.assertEqual(self.source.link, "https://theintercept.com/")
        self.assertEqual(self.source.publication_type.name, "newspaper/journal")
        self.assertEqual(self.source.language.name, "en")
        self.assertEqual(self.source.paths, ["world/"])
        self.assertEqual(self.source.javascript, False)
        self.assertEqual(self.source.regex, "[0-9]{4}/[0-9]{2}/[0-9]{2}")
        self.assertEqual(self.source.headline, {"tag": "h1", "attrs": {}})
        self.assertEqual(self.source.body, {"tag": "h2", "attrs": {}})

    def test_source_to_dict(self):
        sitemap = self.source.to_dict()
        self.assertEqual(self.source.link, sitemap["base_url"])
        self.assertEqual(self.source.paths, sitemap["paths"])
        self.assertEqual(self.source.language.name, sitemap["language"])
        self.assertEqual(self.source.javascript, sitemap["javascript"])
        self.assertEqual(regex.compile(self.source.regex), sitemap["filter"])
        self.assertEqual(self.source.headline, sitemap["headline"])
        self.assertEqual(self.source.body, sitemap["body"])

    def test_source_str_representation(self):
        self.assertEqual(str(self.source), "The Intercept")

    def test_ordering(self):
        all_sources = Source.objects.all()
        self.assertEqual(all_sources[0].name, self.source2.name)


class ArticleTest(TestCase):
    def setUp(self):
        self.publication_type = PublicationType.objects.create(
            name="newspaper/journal"
        )
        self.article = Article.objects.create(
            headline="Restorative Injustice",
            source=Source.objects.create(
                name="The Intercept",
                link="https://theintercept.com/",
                publication_type=self.publication_type,
                language=Language.objects.create(name="en"),
                paths=["world/"],
                javascript=False,
                regex="[0-9]{4}/[0-9]{2}/[0-9]{2}",
                headline={"tag": "h1", "attrs": {}},
                body={"tag": "h2", "attrs": {}},
            ),
            body="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
            link="https://theintercept.com/2022/05/08/"
                 "maryland-campaign-brandy-brooks-progressive-accountability/",
            pubdate=timezone.now(),
        )

    def test_article_content(self):
        self.assertEqual(self.article.headline, "Restorative Injustice")
        self.assertEqual(self.article.source.name, "The Intercept")
        self.assertEqual(self.article.source.link, "https://theintercept.com/")
        self.assertEqual(
            self.article.source.publication_type.name,
            "newspaper/journal"
        )
        self.assertEqual(
            self.article.body,
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit..."
        )
        self.assertEqual(
            self.article.link,
            "https://theintercept.com/2022/05/08/"
            "maryland-campaign-brandy-brooks-progressive-accountability/",
        )

    def test_article_str_representation(self):
        self.assertEqual(str(self.article), "The Intercept: Restorative Injustice")
