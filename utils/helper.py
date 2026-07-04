from datetime import datetime


def clean_text(text: str) -> str:
    """Basic text cleanup."""
    return text.replace("\n", " ").strip()


def get_today():
    return datetime.utcnow().strftime("%Y-%m-%d")