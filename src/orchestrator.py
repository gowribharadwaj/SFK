from src.kernel_client import classify_and_extract
from src.agents.qa_agent import QnAAgent
from src.agents.feedback_agent import FeedbackAgent
from src.utils import get_logger
from src.store import store

logger = get_logger("orchestrator")
qa_agent = QnAAgent()
fb_agent = FeedbackAgent()

class Orchestrator:
    async def handle_message(self, session_id: str, message: str):
        session = store.get_session(session_id)
        last = session.get("last", {}) or {}
        intent, extraction = classify_and_extract(session_id=session_id, message=message, context=last)
        logger.info("Intent=%s Extraction=%s", intent, extraction)

        if intent == "question":
            reply, meta = await qa_agent.handle(session_id=session_id, message=message, extraction=extraction)
            return reply, meta
        elif intent == "feedback":
            reply, meta = await fb_agent.handle(session_id=session_id, message=message, extraction=extraction)
            return reply, meta
        else:
            # default heuristic: treat as question if contains ? or known keywords
            # but keep safe fallback
            reply, meta = await qa_agent.handle(session_id=session_id, message=message, extraction=extraction)
            return reply, meta
