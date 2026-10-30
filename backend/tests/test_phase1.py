import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import init_db, SessionLocal
from app.core.seed_phase1 import seed_registry_data
from app.core.age_bands import get_age_band

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_init():
    init_db()
    seed_registry_data()

def test_minor_record_concealment_returns_404():
    """Sonipat DSO (HR) attempting to access Pune (MH) minor athlete must get 404."""
    res = client.get("/api/v1/registry/athletes", headers={"x-user-id": "pune_dso"})
    assert res.status_code == 200
    athletes = res.json()
    minor = next(a for a in athletes if a["is_minor"])
    
    cross_res = client.get(f"/api/v1/registry/athletes/{minor['id']}", headers={"x-user-id": "sonipat_dso"})
    assert cross_res.status_code == 404

def test_duplicate_detection_returns_candidates_never_auto_merges():
    """Duplicate candidate detection must return candidates and verify auto_merged=False."""
    # Check duplicate against existing "Aarav Shinde"
    req = {
        "name": "Mr. Aarav Shinde",
        "dob": "2009-04-12",
        "district_id": "MH-PUN"
    }
    res = client.post("/api/v1/registry/athletes/check-duplicate", json=req, headers={"x-user-id": "pune_dso"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_duplicate_candidate"] is True
    assert data["auto_merged"] is False
    assert len(data["candidates"]) > 0
    candidate = data["candidates"][0]
    assert candidate["name"] == "Aarav Shinde"
    assert candidate["confidence_score"] >= 0.85
    assert "name" in candidate["match_fields"]
    assert "dob_exact" in candidate["match_fields"]

def test_verification_state_machine_transitions():
    """Invalid transitions return 409; valid transitions transition state."""
    # Query an athlete and set verification_status to VERIFIED explicitly for the test
    db = SessionLocal()
    from app.models.entities import Athlete
    test_ath = db.query(Athlete).first()
    test_ath.verification_status = "VERIFIED"
    db.commit()
    ath_id = test_ath.id
    db.close()
    
    # Try invalid direct jump: VERIFIED -> REJECTED (must go through UNDER_REVIEW)
    inv_res = client.post(
        f"/api/v1/registry/athletes/{ath_id}/verify",
        json={"target_status": "REJECTED", "reason": "Arbitrary rejection"},
        headers={"x-user-id": "pune_dso"}
    )
    assert inv_res.status_code == 409
    assert "Invalid verification transition" in inv_res.json()["detail"]

    # Valid: VERIFIED -> UNDER_REVIEW
    valid_res = client.post(
        f"/api/v1/registry/athletes/{ath_id}/verify",
        json={"target_status": "UNDER_REVIEW", "reason": "Annual re-verification"},
        headers={"x-user-id": "pune_dso"}
    )
    assert valid_res.status_code == 200
    assert valid_res.json()["verification_status"] == "UNDER_REVIEW"

def test_coach_cannot_verify_own_athlete():
    """Coaches cannot execute verification transitions (returns 403)."""
    res = client.get("/api/v1/registry/athletes", headers={"x-user-id": "pune_dso"})
    ath = res.json()[0]
    
    res = client.post(
        f"/api/v1/registry/athletes/{ath['id']}/verify",
        json={"target_status": "VERIFIED", "reason": "I coached him"},
        headers={"x-user-id": "pune_coach"}
    )
    assert res.status_code == 403
    assert "Coaches cannot execute verification transitions" in res.json()["detail"]

def test_minor_onboarding_requires_consent_status():
    """Submitting a minor athlete without consent status returns 422."""
    # Athlete born in 2012 is a minor
    req = {
        "name": "Kiran Jadhav",
        "dob": "2012-05-10",
        "gender": "MALE",
        "state_id": "MH",
        "district_id": "MH-PUN",
        "sport_code": "BOX",
        "guardian_ref": None,
        "consent_status": None
    }
    res = client.post("/api/v1/registry/athletes", json=req, headers={"x-user-id": "pune_dso"})
    assert res.status_code == 422
    assert "guardian consent_status" in res.json()["detail"]

def test_journey_events_append_only():
    """Journey events allow append (POST) but reject PUT and DELETE with 405."""
    res = client.get("/api/v1/registry/athletes", headers={"x-user-id": "pune_dso"})
    ath_id = res.json()[0]["id"]

    # POST journey event
    create_res = client.post(
        f"/api/v1/registry/athletes/{ath_id}/journey",
        json={"event_type": "injury", "event_date": "2026-02-10", "notes": "Wrist sprain during sparring"},
        headers={"x-user-id": "pune_dso"}
    )
    assert create_res.status_code == 201
    j_id = create_res.json()["id"]

    # PUT and DELETE return 405
    put_res = client.put(f"/api/v1/registry/athletes/{ath_id}/journey/{j_id}", json={}, headers={"x-user-id": "pune_dso"})
    assert put_res.status_code == 405
    
    del_res = client.delete(f"/api/v1/registry/athletes/{ath_id}/journey/{j_id}", headers={"x-user-id": "pune_dso"})
    assert del_res.status_code == 405

@pytest.mark.parametrize("dob,as_of,expected_band", [
    (datetime.date(2017, 1, 1), datetime.date(2026, 1, 1), "U-10"),
    (datetime.date(2016, 1, 1), datetime.date(2026, 1, 1), "U-14"),
    (datetime.date(2012, 1, 1), datetime.date(2026, 1, 1), "U-17"),
    (datetime.date(2008, 1, 1), datetime.date(2026, 1, 1), "U-19"),
    (datetime.date(2005, 1, 1), datetime.date(2026, 1, 1), "Senior"),
    (datetime.date(1985, 1, 1), datetime.date(2026, 1, 1), "Post-Career"),
])
def test_age_band_boundaries(dob, as_of, expected_band):
    assert get_age_band(dob, as_of) == expected_band

def test_facility_radius_query_scope():
    """Facility query scoped to caller jurisdiction."""
    res = client.get("/api/v1/facilities", headers={"x-user-id": "pune_dso"})
    assert res.status_code == 200
    facilities = res.json()
    assert all(f["district_id"] == "MH-PUN" for f in facilities)
