import datetime

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from ..models import Article, Language, PublicationType, Source

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
