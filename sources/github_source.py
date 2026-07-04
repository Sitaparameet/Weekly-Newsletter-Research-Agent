import requests
from typing import List
from model import Article
from config import FETCH_LIMIT


class GitHubSource:
    """
    GitHub AI trending repos.
    MCP-first design:
    - If MCP tool exists → use it
    - else fallback to REST API
    """

    def __init__(self, limit: int = FETCH_LIMIT):
        self.api_url = "https://api.github.com/search/repositories"
        self.query = "ai OR llm OR agent"
        self.headers = {"Accept": "application/vnd.github+json"}
        self.limit = limit

    # ---------------------------
    # MCP PLACEHOLDER
    # ---------------------------
    def fetch_from_mcp(self):
        """
        In real MCP setup, this would call:
        GitHub MCP server → search repositories
        """
        return None  # fallback for now

    # ---------------------------
    # API FALLBACK
    # ---------------------------
    def fetch_from_api(self) -> List[Article]:
        """Fetch repositories from GitHub Search API and map to article records."""

        params = {
            "q": self.query,
            "sort": "stars",
            "order": "desc",
            "per_page": self.limit,
        }

        res = requests.get(self.api_url, params=params, headers=self.headers)
        data = res.json()

        articles = []

        for repo in data.get("items", []):
            articles.append(
                Article(
                    title=repo["full_name"],
                    url=repo["html_url"],
                    source="github",
                    source_type="open_source",
                    published=repo.get("created_at"),
                    content=repo.get("description", ""),
                )
            )

        return articles

    def fetch(self) -> List[Article]:
        """
        Return MCP-backed results if available, else fallback to GitHub REST API.
        """
        mcp_result = self.fetch_from_mcp()

        if mcp_result:
            return mcp_result

        return self.fetch_from_api()