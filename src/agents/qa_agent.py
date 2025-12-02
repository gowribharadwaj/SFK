from typing import Tuple, Dict
from src.datasheets import datasheets
from src.store import store
from src.utils import get_logger

logger = get_logger("qa_agent")

class QnAAgent:
    def __init__(self):
        self.datasheets = datasheets
        self.store = store

    async def handle(self, session_id: str, message: str, extraction: Dict) -> Tuple[str, Dict]:
        # extraction may contain designation & attribute
        designation = extraction.get("designation")
        attribute = extraction.get("attribute")

        # attempt to fill from session if missing
        session = self.store.get_session(session_id)
        last = session.get("last", {}) or {}
        if not designation:
            designation = last.get("designation")
        if not attribute:
            attribute = last.get("attribute")

        # If still missing, we cannot answer
        if not designation or not attribute:
            return "Sorry — I couldn't identify the product designation or attribute. Please rephrase (e.g., 'What is the width of 6205?').", {}

        designation_norm = designation.strip()
        attribute_norm = attribute.strip().lower()

        cache_key = f"{designation_norm}:{attribute_norm}"
        cached = self.store.get_cache(cache_key)
        if cached:
            reply = f"The {attribute_norm} of the {designation_norm} bearing is {cached}."
            meta = {"designation": designation_norm, "attribute": attribute_norm, "source": "cache"}
            self.store.update_session(session_id, {"last": {"designation": designation_norm, "attribute": attribute_norm, "answer": reply}})
            return reply, meta

        val, source = self.datasheets.lookup(designation_norm, attribute_norm)
        if val is None:
            return f"Sorry, I can't find that information for '{designation_norm}'. Please try another designation or attribute.", {"designation": designation_norm, "attribute": attribute_norm, "found": False}

        # store in cache
        self.store.set_cache(cache_key, val)
        reply = f"The {attribute_norm} of the {designation_norm} bearing is {val}."
        meta = {"designation": designation_norm, "attribute": attribute_norm, "source": source}
        self.store.update_session(session_id, {"last": {"designation": designation_norm, "attribute": attribute_norm, "answer": reply}})
        return reply, meta
