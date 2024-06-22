from datetime import datetime
from typing import Protocol


class Source(Protocol):
    title: str
    slug: str
    description: str
    created_at: datetime
    language: str
    url: str
    source: str


class Feed(Protocol):
    source: Source
    url: str
