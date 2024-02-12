import pytest
import regex


@pytest.fixture
def sitemap_aj():
    return {
        'base_url': 'https://www.aljazeera.com/',
        'paths': ['news/'],
        'language': 'en',
        'javascript_required': False,
        'filter': regex.Regex(
            '(?<!liveblog)/[0-9]{4}/[0-9]+/[0-9]+/(?!.*terms-and-conditions/|.*community-rules-guidelines/|.*eu-eea-regulatory|.*code-of-ethics|.*liveblog)', flags=regex.V0
        ),
        'headline_selectors': {'tag': 'h1', 'attrs': {}},
        'summary_selectors': {'tag': 'p', 'attrs': {'class': 'article__subhead'}}
    }


@pytest.fixture
def starting_urls_aj():
    return ["https://www.aljazeera.com/news/"]


@pytest.fixture
def expected_aj():
    expected = {
        "asian_cup": {
            'headline': 'Asian Cup final brings FIFA World Cup frenzy back to Qatar’s Souq Waqif',
            'slug': 'asian-cup-final-brings-fifa-world-cup-frenzy-back-to-qatars-souq-waqif',
            'summary': "Excitement for the Asian Cup football final is reaching fever pitch "
                       "as al-Annabi take on an-Nashama at Lusail Stadium.",
            'language': 'en',
            "url": "https://www.aljazeera.com/news/2024/2/10/football-fever-hits-"
                   "jordan-ahead-of-historic-asian-cup-final",
            'source_link': 'https://www.aljazeera.com/'
        },
        "indonesia": {
            "headline": "Big election rallies in Indonesia on final day of campaign",
            "slug": "big-election-rallies-in-indonesia-on-final-day-of-campaign",
            "summary": (
                "Hundreds of thousands of supporters of "
                "presidential contenders pack rallies in capital Jakarta and other cities."
            ),
            "language": "en",
            "url": "https://www.aljazeera.com/news/2024/2/10/big-election-rallies-in-"
                   "indonesia-on-final-day-of-campaign",
            "source_link": "https://www.aljazeera.com/",
        },
        "taiwan": {
            "headline": "How Taiwan’s elections challenge the power of China’s Communist Party",
            "slug": "how-taiwans-elections-challenge-the-power-of-chinas-communist-party",
            "summary": (
                "Elections in Taiwan highlight dissatisfaction in China with a political "
                "system that Beijing says works best for Chinese people."
            ),
            "language": "en",
            "url": "https://www.aljazeera.com/news/2024/2/10/how-taiwans-elections-"
                   "challenge-the-power-of-chinas-communist-party",
            "source_link": "https://www.aljazeera.com/",
        }
    }
    return expected
