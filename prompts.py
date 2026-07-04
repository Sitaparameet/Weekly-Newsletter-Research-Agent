# =========================
# ARTICLE SUMMARIZATION
# =========================

SUMMARIZE_PROMPT = """
You are an AI research assistant for a weekly AI newsletter.

Given an article, do the following:

1. Summarize in 3-5 bullet points
2. Extract key technical insight
3. Identify impact (why it matters)
4. Classify into exactly ONE category:

Categories:
- Research
- Model Release
- Product Launch
- Funding
- Open Source
- Benchmark
- Opinion

5. Extract key data points for newsletter tables.
   Focus on concrete facts that can be tracked:
   - funding rounds / investments
   - product launches
   - model releases / model updates
   - tool comparisons / performance comparisons
   - notable adoption or usage metrics

Return STRICT JSON:

{{
  "summary": "...",
  "insight": "...",
  "impact": "...",
  "category": "...",
  "data_points": [
    {{
      "type": "Funding | Launch | Model Release | Tool Comparison | Metric | Other",
      "label": "...",
      "value": "...",
      "evidence": "short quote or fact from article"
    }}
  ]
}}

ARTICLE:
{content}
"""

# =========================
# QUALITY FILTER
# =========================

FILTER_PROMPT = """
Decide if this article is relevant to AI / LLM / Agents / ML.

Return only:
YES or NO

ARTICLE:
{content}
"""