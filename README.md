# 🧠 AI/Product Weekly Newsletter Research Agent

An automated research pipeline that monitors multiple AI/tech sources, filters and enriches content with an LLM, stores results in queryable CSVs, and generates a publish-ready weekly newsletter digest.

---

## ✨ What It Does

1. **Collects** items from 7 source types: RSS blogs, LinkedIn, X (Twitter), arXiv, Product Hunt, Google AI Blog, and GitHub trending repos.
2. **Filters** each item for AI/ML/Agent relevance using an LLM (YES/NO check).
3. **Enriches** relevant items with a structured summary, key insight, impact statement, category, and extracted data points (funding rounds, model releases, launches, benchmarks).
4. **Stores** everything in queryable CSV files.
5. **Generates** a weekly Markdown digest with top themes, a data-points table, and categorized, linked article sections.

Runs as a one-off script or on a weekly schedule (every Monday, 9 AM).

---

## 🏗️ Project Structure

```text
PythonProject/
├── main.py                # CLI entrypoint (--mode run | schedule)
├── scheduler.py            # Orchestrates the full pipeline; weekly cron job
├── config.py                # Env vars, experiment profiles, source URLs
├── model.py                  # Article schema (Pydantic)
├── llm.py                     # OpenAI wrapper (generate + safe JSON parsing)
├── prompts.py                 # Filter + summarization prompt templates
├── research_agent.py           # Core pipeline: collect → filter → summarize → store
├── database.py                  # CSV-based storage layer (read/write/migrate)
├── digest_generator.py           # Builds the weekly digest + data-points CSV
├── sources/
│   ├── rss_source.py              # Generic RSS reader
│   ├── linkedin_source.py          # LinkedIn RSS + public-page fallback
│   ├── x_source.py                  # X/Twitter via Nitter RSS mirrors
│   ├── arxiv_source.py               # arXiv Atom API
│   ├── producthunt_source.py          # Product Hunt RSS
│   ├── google_ai_source.py             # Google AI Blog RSS
│   └── github_source.py                 # GitHub trending repos (REST API)
├── utils/
│   ├── logger.py                          # Single print() gateway
│   └── helper.py                           # Text cleanup & date helpers
└── outputs/
    ├── newsletter.csv                        # One row per processed article
    ├── key_data_points.csv                     # Flattened structured facts
    └── weekly_digest.md                          # Final newsletter draft
```

---

## ⚙️ Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4.1-mini
DB_PATH=outputs/newsletter.csv
EXPERIMENT_PROFILE=medium
SOURCE_MAX_CANDIDATES=10
VERBOSE_LOGGING=true
TRACE_ARTICLES=true
```

---

## ▶️ Usage

**One-time run:**

```bash
python main.py --mode run
```

**Scheduled weekly run** (every Monday at 09:00):

```bash
python main.py --mode schedule
```

---

## 🎛️ Experiment Profiles

`EXPERIMENT_PROFILE` controls the cost-vs-quality tradeoff of a run. Any individual setting can still be overridden via its own environment variable.

| Setting | `low` | `medium` | `full` |
|---|---|---|---|
| `FETCH_LIMIT` (per source) | 1 | 5 | 10 |
| `PROCESS_LIMIT` (items sent to LLM) | 2 | 3 | 60 |
| `FILTER_CONTENT_CHAR_LIMIT` | 500 | 1200 | 3000 |
| `SUMMARY_CONTENT_CHAR_LIMIT` | 700 | 1800 | 4000 |
| `THEME_ARTICLE_LIMIT` | 3 | 5 | 20 |
| `DIGEST_ITEMS_PER_CATEGORY` | 1 | 3 | 10 |
| `RESET_STORAGE_ON_RUN` | true | true | false |

> ⚠️ `low` fetches only 1 item per source and processes 2 total — great for cheap testing, but the most common reason a run produces an empty digest.

Other overridable settings: `FETCH_LIMIT`, `PROCESS_LIMIT`, `FILTER_CONTENT_CHAR_LIMIT`, `SUMMARY_CONTENT_CHAR_LIMIT`, `THEME_ARTICLE_LIMIT`, `DIGEST_ITEMS_PER_CATEGORY`, `RESET_STORAGE_ON_RUN`, `SOURCE_MAX_CANDIDATES`.

---

## 📊 Outputs

| File | Description |
|---|---|
| `outputs/newsletter.csv` | One row per processed article — title, source, summary, insight, impact, category, data points |
| `outputs/key_data_points.csv` | Flattened, queryable table of every extracted fact (funding, launches, model releases, metrics) |
| `outputs/weekly_digest.md` | Writer-ready newsletter draft — top themes, data-point table, categorized article sections with source links |

---

## 🧩 How It Works Internally

- **`model.py`** defines a shared `Article` schema used across every source adapter and pipeline stage.
- **`sources/`** adapters each implement `fetch() -> List[Article]`, keeping every source interchangeable.
- **`llm.py`** wraps the OpenAI client with a `generate()` call and a `safe_json()` parser that gracefully falls back to regex extraction if the model's JSON is malformed.
- **`prompts.py`** holds the two prompt templates: a lightweight relevance filter and a richer summarization/extraction prompt.
- **`research_agent.py`** ties it together — fetch, cap, filter, summarize, and persist — with detailed logging (`TRACE_ARTICLES`) for debugging low-output runs.
- **`digest_generator.py`** groups stored articles by category, extracts weekly themes via one more LLM call, and renders the final Markdown digest.

---

## 🪵 Logging

- `VERBOSE_LOGGING=true|false` — master switch for all pipeline logs
- `TRACE_ARTICLES=true|false` — detailed per-article trace logs (relevance decisions, category, data-point counts)

To hard-disable all output at the code level, comment out the `print(message)` line in `utils/logger.py`.

---

## ✅ Completed

- Multi-category research monitoring across 7+ source types
- LLM-based relevance filtering and structured enrichment
- Structured data-point extraction (funding, launches, model releases, metrics)
- Queryable CSV storage with schema migration handling
- Weekly digest with top themes, data-point tables, and linked sources
- Low / medium / full experiment profiles with configurable overrides
- Verbose + per-article trace logging

## 🔲 Roadmap

- Official LinkedIn/X API integrations (currently RSS/scraping-based)
- Google Sheets / Notion / Airtable sync destination
- Cross-source deduplication by URL/title similarity

---

## 🧰 Tech Stack

Python · OpenAI API (`gpt-4.1-mini` by default) · `feedparser` · `requests` · `pydantic` · `schedule` · CSV-based storage
