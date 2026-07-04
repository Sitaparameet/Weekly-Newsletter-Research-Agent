import feedparser
import requests
import re
from typing import List
from model import Article
from utils.helper import clean_text
from config import FETCH_LIMIT


class LinkedInSource:
    """
    LinkedIn-oriented source via public RSS feeds.
    Example: LinkedIn Engineering blog RSS.
    """

    def __init__(self, urls: List[str], pages: List[str], limit: int = FETCH_LIMIT):
        self.urls = urls
        self.pages = pages
        self.limit = limit

    def fetch(self) -> List[Article]:
        """Fetch LinkedIn items via RSS first, then fallback to public blog pages."""

        articles = []

        for url in self.urls:
            feed = feedparser.parse(url)
            for entry in feed.entries[:self.limit]:
                articles.append(
                    Article(
                        title=clean_text(entry.get("title", "")),
                        url=entry.get("link", ""),
                        source="linkedin",
                        source_type="linkedin",
                        published=entry.get("published", ""),
                        content=clean_text(entry.get("summary", "")),
                    )
                )

        if articles:
            return articles

        # RSS may be unavailable; fallback to public LinkedIn blog pages.
        for page_url in self.pages:
            page = requests.get(
                page_url,
                timeout=30,
                headers={"User-Agent": "Mozilla/5.0"},
            )
            page.raise_for_status()
            html = page.text

            links = re.findall(r'href="(https://www\.linkedin\.com/blog/member/[^"]+)"', html)
            deduped = []
            for link in links:
                if link not in deduped and "?" not in link and "#" not in link:
                    deduped.append(link)

            for link in deduped:
                if len(articles) >= self.limit:
                    break
                title = link.rstrip("/").split("/")[-1].replace("-", " ").title()
                articles.append(
                    Article(
                        title=clean_text(title),
                        url=link,
                        source="linkedin",
                        source_type="linkedin",
                        published="",
                        content=clean_text(title),
                    )
                )
            if len(articles) >= self.limit:
                break

        return articles
