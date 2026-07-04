from database import fetch_all_articles
from llm import LLM
from datetime import datetime
from collections import defaultdict
import json
import csv
import os
from config import THEME_ARTICLE_LIMIT, DIGEST_ITEMS_PER_CATEGORY, TRACE_ARTICLES
from utils.logger import log


class DigestGenerator:
    """
    Converts stored AI-processed articles into a weekly newsletter.
    """

    def __init__(self):
        self.llm = LLM()

    # -------------------------
    # GROUP BY CATEGORY
    # -------------------------
    def group_articles(self, rows):
        """Group complete article rows by category for digest rendering."""

        grouped = defaultdict(list)

        for r in rows:
            title = (r.get("title") or "").strip()
            url = (r.get("url") or "").strip()
            summary = (r.get("summary") or "").strip()
            if not (title and url and summary):
                continue
            category = r.get("category") or "Uncategorized"
            grouped[category].append(r)

        return grouped

    def collect_data_points(self, rows):
        """Flatten per-article data points into one list for table output."""

        points = []
        for row in rows:
            raw = row.get("data_points_json") or "[]"
            try:
                parsed = json.loads(raw)
            except Exception:
                parsed = []
            for point in parsed:
                points.append(
                    {
                        "type": point.get("type", "Other"),
                        "label": point.get("label", ""),
                        "value": point.get("value", ""),
                        "evidence": point.get("evidence", ""),
                        "source_title": row.get("title", ""),
                        "source_url": row.get("url", ""),
                    }
                )
        return points

    @staticmethod
    def _md_cell(value):
        """Escape markdown table separators and normalize newlines."""

        text = str(value or "")
        return text.replace("\n", " ").replace("|", "\\|")

    def save_data_points_csv(self, points):
        """Save extracted key data points to a standalone CSV artifact."""

        path = "outputs/key_data_points_Full_Record.csv"
        os.makedirs("outputs", exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "type",
                    "label",
                    "value",
                    "evidence",
                    "source_title",
                    "source_url",
                ],
            )
            writer.writeheader()
            writer.writerows(points)
        return path

    # -------------------------
    # EXTRACT THEMES (LLM OPTIONAL)
    # -------------------------
    def extract_themes(self, articles):
        """
        Lightweight LLM call to summarize week's trends.
        """

        # Theme extraction only uses a capped subset to control token usage.
        text = "\n".join(
            f"- {a['title']}: {a['summary']}" for a in articles[:THEME_ARTICLE_LIMIT]
        )

        prompt = f"""
        You are analyzing AI news for a weekly newsletter.

        Extract 3-5 key themes from this week's content.

        Return bullet points only.

        CONTENT:
        {text}
        """

        result = self.llm.generate("You are a trend analyst.", prompt)
        return result

    # -------------------------
    # BUILD MARKDOWN
    # -------------------------
    def build_markdown(self, grouped, themes):
        """Build the full newsletter markdown document."""

        date = datetime.utcnow().strftime("%Y-%m-%d")
        all_rows = [item for articles in grouped.values() for item in articles]
        data_points = self.collect_data_points(all_rows)

        md = []
        md.append(f"# 🧠 Weekly AI Newsletter ({date})\n")

        # Themes
        md.append("## 🔥 Top Themes\n")
        md.append(themes + "\n")

        md.append("## 📊 Key Data Points\n")
        md.append("| Type | Label | Value | Evidence | Source |\n")
        md.append("| --- | --- | --- | --- | --- |\n")
        for point in data_points[:25]:
            source = f"[{self._md_cell(point['source_title'])}]({point['source_url']})"
            md.append(
                f"| {self._md_cell(point['type'])} | {self._md_cell(point['label'])} | "
                f"{self._md_cell(point['value'])} | {self._md_cell(point['evidence'])} | {source} |\n"
            )
        if not data_points:
            md.append("| - | - | - | No structured data points extracted | - |\n")

        # Categories
        for category, articles in grouped.items():
            md.append(f"\n## 📌 {category}\n")
            if TRACE_ARTICLES:
                log(f"🧩 Digest category '{category}' has {len(articles)} candidates")

            for a in articles[:DIGEST_ITEMS_PER_CATEGORY]:
                md.append(f"""
### {a['title']}

{a['summary']}

**Insight:** {a.get('insight', '')}

**Impact:** {a.get('impact', '')}

🔗 Source: {a['url']}
""")

        return "\n".join(md)

    # -------------------------
    # SAVE FILE
    # -------------------------
    def save(self, content):
        """Write digest markdown to the outputs folder and return its path."""

        os.makedirs("outputs", exist_ok=True)

        path = "outputs/weekly_digest_Full_Record.md"

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

        return path

    # -------------------------
    # MAIN ENTRY
    # -------------------------
    def run(self):
        """Generate digest from stored articles and persist markdown + data points CSV."""

        log("🧾 Generating weekly digest...")
        log(
            f"⚙️ Digest limits: themes_from={THEME_ARTICLE_LIMIT}, "
            f"items_per_category={DIGEST_ITEMS_PER_CATEGORY}"
        )

        rows = fetch_all_articles()

        if not rows:
            log("⚠️ No articles found.")
            return

        grouped = self.group_articles(rows)
        valid_rows = [item for articles in grouped.values() for item in articles]
        dropped_rows = len(rows) - len(valid_rows)
        if dropped_rows:
            log(f"🧹 Skipped {dropped_rows} incomplete rows before digest generation")

        data_points = self.collect_data_points(valid_rows)
        proposed = sum(
            min(len(articles), DIGEST_ITEMS_PER_CATEGORY)
            for articles in grouped.values()
        )
        log(f"🗂️ Loaded {len(rows)} stored articles from CSV")
        log(f"🗂️ Using {len(valid_rows)} valid articles in digest")
        log(f"🧠 Theme extraction will use {min(len(valid_rows), THEME_ARTICLE_LIMIT)} articles")

        # flatten for theme extraction
        all_articles = list(valid_rows)

        themes = self.extract_themes(all_articles)

        markdown = self.build_markdown(grouped, themes)

        path = self.save(markdown)
        points_path = self.save_data_points_csv(data_points)

        log(f"📌 Proposed {proposed} items in digest output")
        log(f"📌 Extracted {len(data_points)} structured data points")
        log(f"✅ Digest saved at: {path}")
        log(f"✅ Data-points CSV saved at: {points_path}")