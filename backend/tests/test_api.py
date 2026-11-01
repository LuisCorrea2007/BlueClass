from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_and_dashboard():
    assert client.get("/api/health").status_code == 200
    assert client.get("/").status_code == 200
    assert client.get("/assets/style.css").status_code == 200

def test_memory_and_conversation_ingestion():
    created = client.post("/api/memories", json={
        "title":"Regression memory", "content":"Persistent test content",
        "source":"pytest", "tags":["test"], "importance":4
    })
    assert created.status_code == 200
    memory_id = created.json()["id"]
    assert len(client.get("/api/memories?q=Persistent").json()) >= 1
    assert client.delete(f"/api/memories/{memory_id}").status_code == 200
    ingested = client.post("/api/ingest/conversation", json={
        "platform":"chatgpt", "title":"Imported", "content":"Imported test conversation body"
    })
    assert ingested.status_code == 200
    assert "conversation" in ingested.json()["tags"]

def test_skill_exports():
    created = client.post("/api/skills", json={
        "name":"Regression Skill", "description":"Testing", "instructions":"Run checks."
    })
    assert created.status_code == 200
    sid = created.json()["id"]
    md = client.get(f"/api/skills/{sid}/export?format=md")
    assert md.status_code == 200 and b"name: regression-skill" in md.content
    archive = client.get(f"/api/skills/{sid}/export?format=zip")
    assert archive.status_code == 200 and archive.content[:2] == b"PK"

def test_android_retry_is_idempotent():
    payload = {"title":"Mobile retry", "content":"Same record",
        "source":"android", "source_ref":"stable-client-uuid", "tags":["mobile"]}
    first = client.post("/api/memories", json=payload)
    second = client.post("/api/memories", json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json()["id"] == second.json()["id"]

def test_bearer_token_gate(monkeypatch):
    import app.main as api
    monkeypatch.setattr(api, "API_TOKEN", "test-secret")
    denied = client.get("/api/memories")
    allowed = client.get("/api/memories", headers={"Authorization":"Bearer test-secret"})
    assert denied.status_code == 401
    assert allowed.status_code == 200
    monkeypatch.setattr(api, "API_TOKEN", "")

def test_agent_context_retrieval():
    client.post("/api/memories", json={
        "title":"MEMORA authentication architecture",
        "content":"Use bearer tokens for the API and protect agent context retrieval.",
        "source":"test", "importance":5, "tags":["security"]
    })
    result = client.get("/api/agents/context?q=authentication API")
    assert result.status_code == 200
    assert result.json()["retrieval"] == "lexical-v1"
    assert result.json()["context"]
    assert result.json()["context"][0]["provenance"]["source"] == "test"
