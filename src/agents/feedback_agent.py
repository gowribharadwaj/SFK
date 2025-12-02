from typing import Tuple, Dict
from src.store import store
from src.utils import get_logger

logger = get_logger("feedback_agent")

class FeedbackAgent:
    def __init__(self):
        self.store = store

    async def handle(self, session_id: str, message: str, extraction: Dict) -> Tuple[str, Dict]:
        designation = extraction.get("designation")
        attribute = extraction.get("attribute")
        value = extraction.get("value")

        session = self.store.get_session(session_id)
        last = session.get("last", {}) or {}

        if not designation:
            designation = last.get("designation")
        if not attribute:
            attribute = last.get("attribute")

        if not designation:
            return "Thanks — your feedback was received but I couldn't tie it to a specific product. Please include a designation like '6205' if you can.", {}

        record = {
            "session_id": session_id,
            "designation": designation,
            "attribute": attribute,
            "value": value,
            "raw_message": message,
            "linked_answer": last.get("answer")
        }
        fid = self.store.save_feedback(record)
        # link in session
        self.store.update_session(session_id, {"last_feedback_id": fid})
        return f"Thanks — your feedback for {designation} / {attribute} has been saved (id={fid}).", {"feedback_id": fid}
