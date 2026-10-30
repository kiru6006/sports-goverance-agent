import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_init():
    init_db()

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_minor_record_concealment_returns_404():
    """Sonipat DSO (HR) attempting to access Pune (MH) minor athlete must get 404, not 403."""
    # First get Pune athlete ID using Pune officer
    res = client.get("/api/v1/registry/athletes", headers={"x-user-id": "pune_dso"})
    assert res.status_code == 200
    athletes = res.json()
    minor = next(a for a in athletes if a["is_minor"])
    
    # Query using Sonipat DSO (Haryana)
    cross_res = client.get(f"/api/v1/registry/athletes/{minor['id']}", headers={"x-user-id": "sonipat_dso"})
    assert cross_res.status_code == 404
    assert cross_res.json()["detail"] == "Athlete record not found"

def test_small_cell_suppression():
    """Snapshots with counts < 5 must return suppressed: true and null counts."""
    res = client.get("/api/v1/pipeline/snapshots", headers={"x-user-id": "admin"})
    assert res.status_code == 200
    snapshots = res.json()
    suppressed = next(s for s in snapshots if s["is_suppressed"])
    assert suppressed["identified_count"] is None
    assert suppressed["is_suppressed"] is True
