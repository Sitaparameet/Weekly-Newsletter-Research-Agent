import feedparser
from typing import List
from model import Article
from config import FETCH_LIMIT


class GoogleAISource:
    """
    Google AI Blog RSS feed.
    """

    def __init__(self, url: str, limit: int = FETCH_LIMIT):
        self.url = url
        self.limit = limit

    def fetch(self) -> List[Article]:
        """Fetch Google AI-related blog feed entries."""

        feed = feedparser.parse(self.url)

        articles = []

        for entry in feed.entries[:self.limit]:
            articles.append(
                Article(
                    title=entry.title,
                    url=entry.link,
                    source="google_ai",
                    source_type="blog",
                    published=entry.get("published", ""),
                    content=entry.get("summary", ""),
                )
            )

        return articles