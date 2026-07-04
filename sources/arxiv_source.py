import requests
import xml.etree.ElementTree as ET
from typing import List
from model import Article
from config import FETCH_LIMIT


class ArxivSource:
    """
    Fetch AI papers from arXiv API.
    """

    def __init__(self, query: str, limit: int = FETCH_LIMIT):
        self.query = query
        self.limit = limit

    def fetch(self) -> List[Article]:
        """Query arXiv Atom API and map entries to the shared Article schema."""

        response = requests.get(
            "https://export.arxiv.org/api/query",
            params={
                "search_query": self.query,
                "start": 0,
                "max_results": self.limit,
            },
            timeout=30,
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)

        ns = {"atom": "http://www.w3.org/2005/Atom"}

        articles = []

        for entry in root.findall("atom:entry", ns):
            title = entry.find("atom:title", ns).text
            link = entry.find("atom:id", ns).text
            summary = entry.find("atom:summary", ns).text
            published = entry.find("atom:published", ns).text

            articles.append(
                Article(
                    title=title.strip(),
                    url=link,
                    source="arxiv",
                    source_type="ai_research",
                    published=published,
                    content=summary.strip(),
                )
            )

        return articles