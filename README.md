# SKF Product Assistant (Mini) : FastAPI implementation

Quickstart:
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. copy .env.example -> .env and add keys (Azure OpenAI, Redis if used)
5. uvicorn src.main:app --reload --port 8000

API:
POST /message
Body: {"session_id": "alice", "message": "What is the width of 6205?"}

Notes:
- Q&A agent only returns values present in local JSON files (data/*.json).
- If Azure OpenAI is configured, it will be used for intent/field extraction via function-calling style.
- If not configured, robust heuristics are used.
- Feedback saved to Redis if enabled, otherwise stored in memory.
