import feedparser
from typing import List
from model import Article
from utils.helper import clean_text
from config import FETCH_LIMIT


class ProductHuntSource:
    """
    Product Hunt RSS feed (AI tools + launches).
    """

    def __init__(self, limit: int = FETCH_LIMIT):
        self.url = "https://www.producthunt.com/feed"
        self.limit = limit

    def fetch(self) -> List[Article]:
        """Fetch Product Hunt feed items and normalize them as articles."""

        feed = feedparser.parse(self.url)

        articles = []

        for entry in feed.entries[:self.limit]:
            articles.append(
                Article(
                    title=clean_text(entry.title),
                    url=entry.link,
                    source="producthunt",
                    source_type="product_launch",
                    published=entry.get("published", ""),
                    content=clean_text(entry.get("summary", "")),
                )
            )

        return articles