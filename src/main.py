from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from src.orchestrator import Orchestrator
from src.store import store
from src.utils import get_logger

logger = get_logger("main")
app = FastAPI(title="SKF Product Assistant (Mini) - FastAPI")

orch = Orchestrator()

class MessageRequest(BaseModel):
    session_id: str
    message: str

class MessageResponse(BaseModel):
    reply: str
    metadata: dict = {}

@app.post("/message", response_model=MessageResponse)
async def message_endpoint(req: MessageRequest):
    if not req.session_id or not req.message:
        raise HTTPException(status_code=400, detail="session_id and message are required")
    reply, meta = await orch.handle_message(session_id=req.session_id, message=req.message)
    return MessageResponse(reply=reply, metadata=meta)
