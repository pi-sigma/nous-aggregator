import datetime

import regex  # type: ignore
from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Article
from .models import Language
from .models import PublicationType
from .models import Source


#######################
# Unit Tests for Models
#######################


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


################################################
            # Unit Tests for Views
################################################

TIMESPAN = 7  # no. of days


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.language = Language.objects.create(name="en")
        self.publication_type = PublicationType.objects.create(
            name="newspaper/journal"
        )

        # creates source
        self.source = Source.objects.create(
            name="The Intercept",
            link="https://theintercept.com/",
            publication_type=self.publication_type,
            language=self.language,
            paths=["world/"],
            javascript=False,
            regex="[0-9]{4}/[0-9]{2}/[0-9]{2}",
            headline={"tag": "h1", "attrs": {}},
            body={"tag": "h2", "attrs": {}},
        )

        # create articles
        self.article = Article.objects.create(
            headline="Restorative Injustice",
            source=self.source,
            body="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
            language=self.language,
            link="https://theintercept.com/2022/05/08/"
                 "maryland-campaign-brandy-brooks-progressive-accountability/",
            pubdate=timezone.now(),
        )
        self.article2 = Article.objects.create(
            headline="UK’s Johnson scrambles to regain authority after rebellion",
            source=self.source,
            body="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
            language=self.language,
            link="https://apnews.com/article/boris-johnson-theresa-may-london-"
                 "government-and-politics-00b21e3552b95cc067ce42e163b80df9",
            pubdate=timezone.now() - datetime.timedelta(days=TIMESPAN)
        )

    def test_response_status(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_sources(self):
        response = self.client.get(reverse("index"))
        sources = response.context["sources"]
        self.assertEqual(self.source in sources, True)
        self.assertEqual(self.source.name, "The Intercept")
        self.assertEqual(self.source.link, "https://theintercept.com/")

    def test_articles(self):
        response = self.client.get(reverse("index"))
        html = response.content.decode("utf-8")
        source = response.context["sources"][0]
        self.assertEqual(source, self.article.source)
        self.assertIn(self.article.headline, html)
        self.assertIn(self.article.link, html)


class SearchResultsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.language = Language.objects.create(name="en")
        self.pubtype = PublicationType.objects.create(name="newspaper/journal")
        self.source1 = Source.objects.create(
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
            paths=["world/"],
            javascript=False,
            regex="[0-9]{4}/[0-9]{2}/[0-9]{2}",
            headline={"tag": "h1", "attrs": {}},
            body={"tag": "h2", "attrs": {}},
        )
        self.article1 = Article.objects.create(
            headline="Restorative Injustice",
            source=self.source1,
            body="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
            language=self.language,
            link="https://theintercept.com/2022/05/08/"
            "maryland-campaign-brandy-brooks-progressive-accountability/",
            pubdate=timezone.now(),
        )
        self.article2 = Article.objects.create(
            headline="UK’s Johnson scrambles to regain authority after rebellion",
            source=self.source2,
            body="Lorem ipsum dolor sit amet, consectetur adipiscing elit...",
            language=self.language,
            link="https://apnews.com/article/boris-johnson-theresa-may-london-"
                 "government-and-politics-00b21e3552b95cc067ce42e163b80df9",
            pubdate=timezone.now()
        )

    def test_response_status(self):
        response = self.client.get(reverse("search"), {"q": "scrambles"})
        self.assertEqual(response.status_code, 200)

    def test_search_successful(self):
        response = self.client.get(reverse("search"), {"q": "scrambles"})
        html = response.content.decode("utf-8")
        source = response.context["sources"][0]

        self.assertEqual(source, self.article2.source)
        self.assertIn(self.article2.headline, html)
        self.assertIn(self.article2.link, html)
        self.assertNotIn(self.article1.headline, html)

    def test_search_unrelated(self):
        """Completely unrelated words should not trigger"""
        response = self.client.get(reverse("search"), {"q": "ROFL"})
        html = response.content.decode("utf-8")

        self.assertNotIn(self.source1.name, html)
        self.assertNotIn(self.source2.name, html)
        self.assertNotIn(self.article1.headline, html)
        self.assertNotIn(self.article2.headline, html)
        self.assertNotIn(self.article1.link, html)
        self.assertNotIn(self.article2.link, html)

    def test_search_substring(self):
        """Substrings of query should not trigger"""
        response = self.client.get(reverse("search"), {"q": "justice"})
        html = response.content.decode("utf-8")

        self.assertNotIn(self.source1.name, html)
        self.assertNotIn(self.source2.name, html)
        self.assertNotIn(self.article1.headline, html)
        self.assertNotIn(self.article2.headline, html)
        self.assertNotIn(self.article1.link, html)
        self.assertNotIn(self.article2.link, html)
