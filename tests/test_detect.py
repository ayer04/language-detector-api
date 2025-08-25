
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
headers = {"X-API-Key": "dev"}

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert "status" in r.json()

def test_detect_en():
    r = client.post("/detect", json={"text":"Hello world, this is a test."}, headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert "language" in j
    assert j["language"] in ["en", "und"]

def test_detect_batch():
    r = client.post("/detect/batch", json={"items":["Guten Tag","Merhaba dünya","Buenos días"]}, headers=headers)
    assert r.status_code == 200
    j = r.json()
    assert isinstance(j, list)
    assert len(j) == 3
