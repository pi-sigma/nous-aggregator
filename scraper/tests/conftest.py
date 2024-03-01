from typing import Dict, List

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
        'search_params': {
            'headline': {
                'find': ["h1"],
                'remove': []
            },
            'summary': {
                'find': [".p1", "p"],
                'remove': []
            }
        }
    }


@pytest.fixture
def starting_urls_aj() -> List[str]:
    return ["https://www.aljazeera.com/news/"]


@pytest.fixture
def expected_aj() -> Dict[str, Dict[str, str]]:
    expected = {
        "asian_cup": {
            'headline': 'Asian Cup final brings FIFA World Cup frenzy back to Qatar’s Souq Waqif',
            'slug': 'asian-cup-final-brings-fifa-world-cup-frenzy-back-to-qatars-souq-waqif',
            "summary": (
                "Excitement for the Asian Cup football final is reaching fever pitch as al-Annabi take on an-Nashama at Lusail Stadium. Save articles to read later and create your own reading list. Doha, Qatar – On Friday nights, Souq Waqif – Qatar’s old-style all-purpose market that also serves as the country’s central tourist attraction – brings together people from all walks of life, dozens of different nationalities and varying interests for a unique mix of colour and noise. But when the country plays host to a football tournament – be it the world’s biggest sporting event such as the FIFA World Cup or a regional championship – the excitement reaches a fever pitch. On the eve of the final of the ongoing AFC Asian Cup 2023, the famous marketplace in the heart of Doha was the marching ground of football fans of both teams vying for the continental crown in Saturday’s final at Lusail Stadium. Passionate supporters of an-Nashama – the gentlemen, as Jordan’s football team is lovingly known – gathered in"
            ),
            'language': 'en',
            "url": "https://www.aljazeera.com/sports/2024/2/10/football-fans-souq-waqif",
            'source_link': 'https://www.aljazeera.com/'
        },
        "indonesia": {
            "headline": "Big election rallies in Indonesia on final day of campaign",
            "slug": "big-election-rallies-in-indonesia-on-final-day-of-campaign",
            "summary": (
                "Tens of thousands of supporters of Indonesia’s presidential candidates have poured onto its streets as they hold final campaigns before heading to the polls in the world’s biggest single-day election. The contenders to lead the world’s third-largest democracy are popular former governors, Ganjar Pranowo and Anies Baswedan, and ex-special forces commander Prabowo Subianto, who has soared in opinion polls with the tacit backing of the president, and with the incumbent’s son as his running mate. The elections on Wednesday will elect a new president and vice president, in addition to parliamentary and local representatives. High-schooler Alfiatnan, 18, said she would vote for Subianto because this was his third attempt at the presidency. “I think there’s no harm [in] giving opportunity to someone who is trying. His optimistic spirit influenced me to choose him.” Also in the running is Baswedan, the former governor of Jakarta who is running as an independent candidate. The 54-year-old was e"
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
                "Elections in Taiwan highlight dissatisfaction in China with a political system that Beijing says works best for Chinese people. Save articles to read later and create your own reading list. If free and fair national elections are considered the hallmark of a democratic state, Taiwan has much to boast about. In January, the self-ruled island held its eighth presidential election concurrently with a parliamentary vote. Just 160km (100 miles) away on the other side of the narrow Taiwan Strait, the Communist Party of China (CPC) has ruled China since 1949, and though the party often claims that it governs a democratic state, there is no electoral process comparable with Taiwan’s. China’s President Xi Jinping has referred to “whole-process people’s democracy” to describe the Chinese political system where the “people are the masters” but the party-state apparatus runs the people’s affairs on their behalf. Ken Cai*, a 35-year-old entrepreneur from Shanghai, does not subscribe to Xi’s definit"
            ),
            "language": "en",
            "url": "https://www.aljazeera.com/news/2024/2/10/how-taiwans-elections-"
                   "challenge-the-power-of-chinas-communist-party",
            "source_link": "https://www.aljazeera.com/",
        }
    }
    return expected
