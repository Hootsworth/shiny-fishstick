from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)

def test_health_check_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}

def test_ready_endpoint():
    res = client.get("/ready")
    assert res.status_code == 200
    assert res.json() == {"status": "ready", "db": "ok"}

def test_list_projects_endpoint():
    res = client.get("/api/projects")
    assert res.status_code == 200
    assert isinstance(res.json(), list)
