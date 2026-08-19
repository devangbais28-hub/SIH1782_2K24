import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings

settings = get_settings()
client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "faiss_index_loaded" in data
    assert "cluster_count" in data
    assert data["cluster_count"] >= 10


def test_verify_validation_error():
    # Empty title triggers Pydantic 422 error
    response = client.post("/api/verify", json={"title": "", "domain": "general"})
    assert response.status_code == 422


def test_verify_endpoint_success():
    response = client.post("/api/verify", json={
        "title": "Climate Change News Daily",
        "domain": "news-environment",
        "language": "English",
        "description": "Daily updates on global environmental issues"
    })
    assert response.status_code == 200
    data = response.json()
    assert "verification_id" in data
    assert "decision" in data
    assert data["decision"] in ("POTENTIAL_CONFLICT", "REVIEW_REQUIRED", "NO_STRONG_CONFLICT")
    assert "score_breakdown" in data
    assert "top_matches" in data


def test_submit_endpoint():
    response = client.post("/api/submit", json={
        "title": "Unique Publication Title Test 99",
        "domain": "technology",
        "language": "English",
        "description": "Unique test publication"
    })
    assert response.status_code == 200
    data = response.json()
    assert "submission_id" in data
    assert "record_status" in data
    assert "verification_result" in data


def test_admin_rebuild_unauthorized():
    response = client.post("/api/admin/rebuild-index")
    assert response.status_code == 401


def test_admin_rebuild_authorized():
    headers = {"X-Admin-Api-Key": settings.ADMIN_API_KEY}
    response = client.post("/api/admin/rebuild-index", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "vector_count" in data
