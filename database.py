import csv
import os
from config import DB_PATH, RESET_STORAGE_ON_RUN
from utils.logger import log

FIELDNAMES = [
    "title",
    "url",
    "source",
    "source_type",
    "published",
    "content",
    "summary",
    "insight",
    "impact",
    "category",
    "data_points_json",
]


def _ensure_parent_dir():
    """Create the parent directory for the storage file if it does not exist."""

    folder = os.path.dirname(DB_PATH)
    if folder:
        os.makedirs(folder, exist_ok=True)


def init_db():
    """Initialize CSV storage with header."""
    _ensure_parent_dir()
    if RESET_STORAGE_ON_RUN:
        with open(DB_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
        log(f"🧹 Reset storage file: {DB_PATH}")
        return
    if os.path.exists(DB_PATH) and os.path.getsize(DB_PATH) > 0:
        with open(DB_PATH, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            existing_header = next(reader, [])
            rows = list(reader)
        if existing_header == FIELDNAMES:
            log(f"📁 Using existing storage file: {DB_PATH}")
            return

        # Best-effort header migration keeps available columns and fills new ones.
        log("🔄 Storage schema changed; migrating CSV header")
        index_map = {name: i for i, name in enumerate(existing_header)}
        migrated = []
        for row in rows:
            mapped = {name: "" for name in FIELDNAMES}
            for name, i in index_map.items():
                if name in mapped and i < len(row):
                    mapped[name] = row[i]
            migrated.append(mapped)

        with open(DB_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
            writer.writerows(migrated)
        log(f"✅ Migration complete: {DB_PATH}")
        return
    with open(DB_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
    log(f"🆕 Initialized storage file: {DB_PATH}")


def insert_article(article):
    """Append processed article row to CSV file."""
    _ensure_parent_dir()
    with open(DB_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(
            {
                "title": article.title,
                "url": article.url,
                "source": article.source,
                "source_type": article.source_type,
                "published": article.published,
                "content": article.content,
                "summary": article.summary,
                "insight": article.insight,
                "impact": article.impact,
                "category": article.category,
                "data_points_json": article.data_points_json,
            }
        )


def fetch_all_articles():
    """Fetch all stored article rows from CSV file."""
    if not os.path.exists(DB_PATH):
        return []
    with open(DB_PATH, "r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))