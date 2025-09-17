import os
import logging
from typing import Any, Dict

logger = logging.getLogger("legal_demystifier")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


def safe_parse_json(text: str):
    import json
    try:
        return json.loads(text)
    except Exception:
        # fallback: try to find JSON object in text
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except Exception:
            logger.exception("Failed to parse JSON from model text")
            return None


def make_clause_provenance(documents):
    """
    Helper to transform retrieval result pieces into provenance objects.
    'documents' is expected to be list of retrieval chunks/objects.
    """
    provs = []
    for d in documents or []:
        # expected shape: {'text': '...', 'page': n, 'start_offset': x}
        provs.append({"text": d.get("text"), "page": d.get("page"), "start_offset": d.get("start_offset")})
    return provs
