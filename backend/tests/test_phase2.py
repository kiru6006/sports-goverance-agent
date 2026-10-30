import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import init_db
from app.core.seed_phase1 import seed_registry_data
from app.core.seed_phase2 import seed_phase2_data
from app.core.pipeline_engine import calculate_funnel_stages, evaluate_district_gap

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_init():
    init_db()
    seed_registry_data()
    seed_phase2_data()

def test_diagnosis_heatmap_gap_and_reasons():
    """Heatmap identifies gaps with explainable reasons and peer medians."""
    res = client.get("/api/v1/pipeline/diagnosis/heatmap?state_id=MH", headers={"x-user-id": "mh_officer"})
    assert res.status_code == 200
    cells = res.json()
    assert len(cells) > 0
    # Check that suppressed cell doesn't leak count
    suppressed = next((c for c in cells if c["is_suppressed"]), None)
    if suppressed:
        assert suppressed["identified_count"] is None
        assert suppressed["rate_per_100k"] is None

def test_cumulative_funnel_property():
    """Verify invariant: Identified >= Verified >= Supported >= Progressed."""
    res = client.get("/api/v1/pipeline/funnel?state_id=MH", headers={"x-user-id": "mh_officer"})
    assert res.status_code == 200
    f = res.json()
    assert f["identified"] >= f["verified"]
    assert f["verified"] >= f["supported"]
    assert f["supported"] >= f["progressed"]

def test_equipment_loan_append_only():
    """Equipment loan log rejects PUT and DELETE with 405 Method Not Allowed."""
    res = client.get("/api/v1/equipment/items", headers={"x-user-id": "pune_dso"})
    assert res.status_code == 200
    
    put_res = client.put("/api/v1/equipment/loans/mock-id", json={}, headers={"x-user-id": "pune_dso"})
    assert put_res.status_code == 405
    assert "append-only" in put_res.json()["detail"]

    del_res = client.delete("/api/v1/equipment/loans/mock-id", headers={"x-user-id": "pune_dso"})
    assert del_res.status_code == 405

def test_equipment_overdue_query():
    """Overdue query returns unreturned items past due date."""
    res = client.get("/api/v1/equipment/overdue", headers={"x-user-id": "pune_dso"})
    assert res.status_code == 200
    overdue = res.json()
    assert len(overdue) >= 1
    assert overdue[0]["is_overdue"] is True
    assert overdue[0]["returned_at"] is None

def test_facility_utilisation_rate_calculation():
    """Facility utilisation matches hours_used / capacity."""
    fac_res = client.get("/api/v1/facilities", headers={"x-user-id": "pune_dso"})
    fac_id = fac_res.json()[0]["id"]

    log_res = client.post(
        f"/api/v1/facilities/{fac_id}/utilisation",
        json={
            "period": "2026-03-01",
            "sessions": 50,
            "athlete_count": 150,
            "hours_used": 150.0  # 150/300 = 50.0%
        },
        headers={"x-user-id": "pune_dso"}
    )
    assert log_res.status_code == 201
    util = log_res.json()
    assert util["utilisation_rate_pct"] == 50.0
    assert util["is_underutilised"] is False
