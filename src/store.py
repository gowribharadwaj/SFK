import json
import uuid
from src.config import settings
from src.utils import get_logger

logger = get_logger("store")
try:
    import redis
except Exception:
    redis = None

class Store:
    def __init__(self):
        self.use_redis = settings.USE_REDIS and redis is not None
        if self.use_redis:
            self._r = redis.from_url(settings.REDIS_URL, decode_responses=True)
        else:
            self._mem = {"sessions": {}, "cache": {}, "feedback": {}}

    # session
    def get_session(self, session_id: str):
        if self.use_redis:
            raw = self._r.get(f"session:{session_id}")
            return json.loads(raw) if raw else {}
        return self._mem["sessions"].get(session_id, {})

    def update_session(self, session_id: str, data: dict):
        if self.use_redis:
            cur = self.get_session(session_id)
            cur.update(data)
            self._r.set(f"session:{session_id}", json.dumps(cur))
        else:
            self._mem["sessions"].setdefault(session_id, {}).update(data)

    # cache
    def get_cache(self, key: str):
        if self.use_redis:
            v = self._r.get(f"cache:{key}")
            return v
        return self._mem["cache"].get(key)

    def set_cache(self, key: str, value: str):
        if self.use_redis:
            self._r.set(f"cache:{key}", value)
        else:
            self._mem["cache"][key] = value

    # feedback
    def save_feedback(self, record: dict) -> str:
        fid = str(uuid.uuid4())
        if self.use_redis:
            self._r.hset("feedbacks", fid, json.dumps(record))
        else:
            self._mem["feedback"][fid] = record
        return fid

store = Store()
