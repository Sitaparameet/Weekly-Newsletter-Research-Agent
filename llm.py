import json
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from utils.logger import log

client = OpenAI(api_key=OPENAI_API_KEY)


class LLM:
    """
    Lightweight LLM wrapper for:
    - summarization
    - classification
    - filtering
    """

    def generate(self, system: str, user: str) -> str:
        """Send one chat completion request and return the assistant text response."""

        # Print request size so experiments can estimate prompt/token footprint.
        log(
            f"🤖 LLM call model={MODEL_NAME} "
            f"system_chars={len(system)} user_chars={len(user)}"
        )
        res = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        content = res.choices[0].message.content
        log(f"🤖 LLM response chars={len(content or '')}")
        return content

    def safe_json(self, text: str):
        """
        Parse JSON from model text and fallback to first JSON-like object block.
        """
        try:
            return json.loads(text)
        except Exception:
            # fallback: try to extract JSON block
            import re
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return None