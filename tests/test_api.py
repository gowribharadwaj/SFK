from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_missing_fields():
    r = client.post("/message", json={})
    assert r.status_code in (400,422)

def test_question_6205():
    r = client.post("/message", json={"session_id":"t1","message":"What is the width of 6205?"})
    assert r.status_code == 200
    d = r.json()
    assert "width" in d["reply"] or "can't find" in d["reply"].lower()
