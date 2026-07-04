import os
from dotenv import load_dotenv

load_dotenv()


def _get_positive_int(name: str, default: int) -> int:
    """Read a positive integer from environment variables with a safe default."""

    raw = os.getenv(name)
    if raw is None:
        return default
    value = int(raw)
    if value <= 0:
        raise ValueError(f"{name} must be > 0")
    return value


def _profile_defaults(profile: str) -> dict:
    """
    Central place for experiment presets.
    low  -> lower token usage, faster iteration.
    full -> higher recall + richer summaries for final-quality output.
    """
    presets = {
        "low": {
            "FETCH_LIMIT": 1,
            "PROCESS_LIMIT": 2,
            "FILTER_CONTENT_CHAR_LIMIT": 500,
            "SUMMARY_CONTENT_CHAR_LIMIT": 700,
            "THEME_ARTICLE_LIMIT": 3,
            "DIGEST_ITEMS_PER_CATEGORY": 1,
            "RESET_STORAGE_ON_RUN": True,
        },
        "medium": {
            "FETCH_LIMIT": 5,
            "PROCESS_LIMIT": 3,
            "FILTER_CONTENT_CHAR_LIMIT": 1200,
            "SUMMARY_CONTENT_CHAR_LIMIT": 1800,
            "THEME_ARTICLE_LIMIT": 5,
            "DIGEST_ITEMS_PER_CATEGORY": 3,
            "RESET_STORAGE_ON_RUN": True,
        },
        "full": {
            "FETCH_LIMIT": 10,
            "PROCESS_LIMIT": 60,
            "FILTER_CONTENT_CHAR_LIMIT": 3000,
            "SUMMARY_CONTENT_CHAR_LIMIT": 4000,
            "THEME_ARTICLE_LIMIT": 20,
            "DIGEST_ITEMS_PER_CATEGORY": 10,
            "RESET_STORAGE_ON_RUN": False,
        },
    }
    if profile not in presets:
        raise ValueError("EXPERIMENT_PROFILE must be 'low', 'medium', or 'full'")
    return presets[profile]

# =========================
# LLM CONFIG
# =========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4.1-mini")

# =========================
# STORAGE
# =========================
DB_PATH = os.getenv("DB_PATH", "outputs/newsletter_Full_Record.csv")

# =========================
# TOKEN/COST CONTROLS
# =========================
EXPERIMENT_PROFILE = os.getenv("EXPERIMENT_PROFILE", "low").lower()
PROFILE = _profile_defaults(EXPERIMENT_PROFILE)

# You can still override any profile value by defining the env var explicitly.
FETCH_LIMIT = _get_positive_int("FETCH_LIMIT", PROFILE["FETCH_LIMIT"])
PROCESS_LIMIT = _get_positive_int("PROCESS_LIMIT", PROFILE["PROCESS_LIMIT"])
FILTER_CONTENT_CHAR_LIMIT = _get_positive_int(
    "FILTER_CONTENT_CHAR_LIMIT", PROFILE["FILTER_CONTENT_CHAR_LIMIT"]
)
SUMMARY_CONTENT_CHAR_LIMIT = _get_positive_int(
    "SUMMARY_CONTENT_CHAR_LIMIT", PROFILE["SUMMARY_CONTENT_CHAR_LIMIT"]
)
THEME_ARTICLE_LIMIT = _get_positive_int(
    "THEME_ARTICLE_LIMIT", PROFILE["THEME_ARTICLE_LIMIT"]
)
DIGEST_ITEMS_PER_CATEGORY = _get_positive_int(
    "DIGEST_ITEMS_PER_CATEGORY", PROFILE["DIGEST_ITEMS_PER_CATEGORY"]
)
RESET_STORAGE_ON_RUN = (
    os.getenv("RESET_STORAGE_ON_RUN", str(PROFILE["RESET_STORAGE_ON_RUN"])).lower()
    == "true"
)
SOURCE_MAX_CANDIDATES = _get_positive_int("SOURCE_MAX_CANDIDATES", 10)

# =========================
# LOGGING
# =========================
VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "true").lower() == "true"
TRACE_ARTICLES = os.getenv("TRACE_ARTICLES", "true").lower() == "true"

# =========================
# SOURCES
# =========================
SOURCES = {
    "rss": [
        "https://www.theverge.com/rss/index.xml",
        "https://huggingface.co/blog/feed.xml",
        "https://tldr.tech/ai/rss",
    ],
    "linkedin_rss": [
        "https://engineering.linkedin.com/blog.rss",
        "https://blog.linkedin.com/rss",
    ],
    "linkedin_pages": [
        "https://www.linkedin.com/blog/member/product",
        "https://www.linkedin.com/blog/member/company-update",
    ],
    "x_rss": [
        "https://nitter.net/OpenAI/rss",
        "https://nitter.net/AnthropicAI/rss",
    ],
    "arxiv_query": "cat:cs.AI OR cat:cs.LG",
    "product_hunt": "https://www.producthunt.com/feed",
    "google_ai_rss": "https://blog.google/technology/ai/rss/",
}