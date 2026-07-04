import json
from llm import LLM
from prompts import SUMMARIZE_PROMPT, FILTER_PROMPT
from database import insert_article
from model import Article
from config import (
    EXPERIMENT_PROFILE,
    SOURCES,
    FETCH_LIMIT,
    PROCESS_LIMIT,
    SOURCE_MAX_CANDIDATES,
    FILTER_CONTENT_CHAR_LIMIT,
    SUMMARY_CONTENT_CHAR_LIMIT,
    TRACE_ARTICLES,
)
from utils.logger import log

from sources.rss_source import RSSSource
from sources.arxiv_source import ArxivSource
from sources.producthunt_source import ProductHuntSource
from sources.google_ai_source import GoogleAISource
from sources.github_source import GitHubSource
from sources.linkedin_source import LinkedInSource
from sources.x_source import XSource


class ResearchAgent:
    """
    Now becomes an AI-powered pipeline:
    1. Collect
    2. Filter
    3. Summarize
    4. Categorize
    5. Store
    """

    def __init__(self):
        self.llm = LLM()

    # -------------------------
    # FILTER STEP
    # -------------------------
    def is_relevant(self, content: str) -> bool:
        # Keep filter prompt small during experiments to reduce tokens.
        prompt = FILTER_PROMPT.format(content=content[:FILTER_CONTENT_CHAR_LIMIT])
        result = self.llm.generate("You are a filter.", prompt)
        return "YES" in result.upper()

    # -------------------------
    # SUMMARIZE STEP
    # -------------------------
    def summarize(self, article: Article):
        """Generate structured newsletter metadata for one article via LLM."""

        # Summary prompt can be larger than filter prompt, but is still capped.
        prompt = SUMMARIZE_PROMPT.format(content=article.content[:SUMMARY_CONTENT_CHAR_LIMIT])
        result = self.llm.generate("You are a summarizer.", prompt)

        data = self.llm.safe_json(result)

        if not data:
            return None

        return data

    # -------------------------
    # PIPELINE
    # -------------------------
    def run(self):
        """Execute full research flow: collect, evaluate, enrich, and persist articles."""

        log("📡 Collecting articles...")
        log(
            f"🧪 Experiment profile: {EXPERIMENT_PROFILE}"
        )
        log(
            f"⚙️ Limits: fetch_per_source={FETCH_LIMIT}, "
            f"process_limit={PROCESS_LIMIT}, "
            f"max_candidates_per_source={SOURCE_MAX_CANDIDATES}, "
            f"filter_chars={FILTER_CONTENT_CHAR_LIMIT}, "
            f"summary_chars={SUMMARY_CONTENT_CHAR_LIMIT}"
        )

        sources = [
            RSSSource(SOURCES["rss"]),
            LinkedInSource(SOURCES["linkedin_rss"], SOURCES["linkedin_pages"]),
            XSource(SOURCES["x_rss"]),
            ArxivSource(SOURCES["arxiv_query"]),
            ProductHuntSource(),
            GoogleAISource(SOURCES["google_ai_rss"]),
            GitHubSource()
        ]

        raw_articles = []

        for source in sources:
            source_name = source.__class__.__name__
            try:
                if hasattr(source, "urls"):
                    log(f"🔗 {source_name} URLs: {', '.join(source.urls)}")
                elif hasattr(source, "url"):
                    log(f"🔗 {source_name} URL: {source.url}")
                if hasattr(source, "pages"):
                    log(f"🔗 {source_name} fallback pages: {', '.join(source.pages)}")
                fetched = source.fetch()
                if len(fetched) > SOURCE_MAX_CANDIDATES:
                    # Hard cap protects full profile from over-collecting one source.
                    fetched = fetched[:SOURCE_MAX_CANDIDATES]
                    log(f"✂️ {source_name}: capped to {SOURCE_MAX_CANDIDATES} candidates")
                raw_articles.extend(fetched)
                log(f"📥 {source_name}: retrieved {len(fetched)} items")
                if TRACE_ARTICLES:
                    for i, item in enumerate(fetched, start=1):
                        log(f"   {source_name} #{i}: {item.title}")
            except Exception as exc:
                log(f"⚠️ Failed to fetch from {source_name}: {exc}")

        log(f"📊 Collected {len(raw_articles)} articles")

        processed = 0

        # Process only a bounded subset to control LLM usage per run.
        processing_pool = raw_articles[:PROCESS_LIMIT]
        log(f"🧪 Processing {len(processing_pool)} items with LLM")

        for idx, article in enumerate(processing_pool, start=1):
            if TRACE_ARTICLES:
                log(f"🔎 Evaluating #{idx}: {article.title}")

            # 1. Filter irrelevant content
            relevant = self.is_relevant(article.content or "")
            if TRACE_ARTICLES:
                log(f"   Relevance: {'YES' if relevant else 'NO'}")
            if not relevant:
                continue

            # 2. Summarize
            summary = self.summarize(article)

            if not summary:
                if TRACE_ARTICLES:
                    log("   Summary parse failed: skipped")
                continue

            # 3. Attach AI output
            data_points = summary.get("data_points", [])
            if not isinstance(data_points, list):
                data_points = []
            article.summary = summary.get("summary")
            article.insight = summary.get("insight")
            article.impact = summary.get("impact")
            article.category = summary.get("category", "Uncategorized")
            article.data_points_json = json.dumps(data_points)
            if TRACE_ARTICLES:
                log(f"   Category: {article.category}")
                log(f"   Data points: {len(data_points)}")

            # 4. Store
            insert_article(article)
            if TRACE_ARTICLES:
                log("   Stored in CSV")

            processed += 1

        log(f"✅ Processed {processed} AI-relevant articles")