import feedparser
from typing import List
from model import Article
from utils.helper import clean_text
from config import FETCH_LIMIT


class XSource:
    """
    X (Twitter) source via public RSS-compatible endpoints (for example Nitter).
    If an endpoint is unavailable, the caller handles failures at the source level.
    """

    def __init__(self, urls: List[str], limit: int = FETCH_LIMIT):
        self.urls = urls
        self.limit = limit

    def fetch(self) -> List[Article]:
        """Fetch X updates from RSS-compatible feed endpoints."""

        articles = []

        for url in self.urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:self.limit]:
                articles.append(
                    Article(
                        title=clean_text(entry.get("title", "")),
                        url=entry.get("link", ""),
                        source="x",
                        source_type="x_twitter",
                        published=entry.get("published", ""),
                        content=clean_text(entry.get("summary", "")),
                    )
                )

        return articles
