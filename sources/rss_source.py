import feedparser
from typing import List
from model import Article
from utils.helper import clean_text
from config import FETCH_LIMIT


class RSSSource:
    """
    Generic RSS reader for AI blogs and newsletters.
    """

    def __init__(self, urls: List[str], name: str = "rss", limit: int = FETCH_LIMIT):
        self.urls = urls
        self.name = name
        self.limit = limit

    def fetch(self) -> List[Article]:
        """Fetch and normalize entries from configured RSS feeds."""

        articles = []

        for url in self.urls:
            feed = feedparser.parse(url)

            for entry in feed.entries[:self.limit]:
                article = Article(
                    title=clean_text(entry.get("title", "")),
                    url=entry.get("link", ""),
                    source=self.name,
                    source_type="rss",
                    published=entry.get("published", ""),
                    content=clean_text(entry.get("summary", "")),
                )
                articles.append(article)

        return articles