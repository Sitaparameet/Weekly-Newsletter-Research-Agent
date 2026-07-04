from pydantic import BaseModel
from typing import Optional


class Article(BaseModel):
    """Normalized article object used across source adapters and pipeline stages."""

    title: str
    url: str
    source: str
    source_type: Optional[str] = None
    published: Optional[str] = None
    content: Optional[str] = None

    summary: Optional[str] = None
    insight: Optional[str] = None
    impact: Optional[str] = None
    category: Optional[str] = None
    data_points_json: Optional[str] = None