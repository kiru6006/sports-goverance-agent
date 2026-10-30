import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, init_db
from app.core.seed_phase1 import seed_registry_data
from app.core.seed_phase2 import seed_phase2_data
from app.core.seed_phase3 import seed_phase3_data
from app.core.seed_phase4 import seed_policy_chunks
from app.core.seed_phase5 import seed_state_manifests
from app.models.entities import Athlete, OfflineSyncRecord

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    seed_registry_data()
    seed_phase2_data()
    seed_phase3_data()
    seed_policy_chunks()
    seed_state_manifests()
    yield

def test_state_adapter_manifest_contract():
    """Requirement: State adapter loads versioned configuration (languages, sports, policies)."""
    res = client.get("/api/v1/adapters/states/MH")
    assert res.status_code == 200
    data = res.json()
    assert data["state_id"] == "MH"
    assert data["state_name"] == "Maharashtra"
    assert data["primary_language"] == "mr"
    assert "Boxing" in data["priority_sports"]
    assert len(data["state_policies"]) > 0

    # Non-existent state returns 404
    missing_res = client.get("/api/v1/adapters/states/NONEXISTENT")
    assert missing_res.status_code == 404

def test_offline_batch_sync_50_items():
    """Requirement: Batch of 50 offline queued updates processes accurately without duplicates."""
    db = SessionLocal()
    ath = db.query(Athlete).first()
    ath_id = ath.id
    db.close()

    actions = []
    for i in range(50):
        actions.append({
            "client_sync_id": f"SYNC-TEST-BATCH-{i}-{datetime.datetime.utcnow().timestamp()}",
            "entity_name": "Athlete",
            "entity_id": ath_id,
            "action_type": "UPDATE",
            "client_timestamp": datetime.datetime.utcnow().isoformat(),
            "payload": {"guardian_ref": f"Parent Contact Update #{i}"}
        })

    res = client.post(
        "/api/v1/sync/batch",
        json={"actions": actions},
        headers={"x-user-id": "pune_dso"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_received"] == 50
    assert data["applied_count"] == 50
    assert data["conflict_count"] == 0

def test_conflict_resolution_server_wins_on_verification():
    """Requirement: Verification status cannot be mutated offline (Server Wins)."""
    db = SessionLocal()
    ath = db.query(Athlete).first()
    ath.verification_status = "REJECTED"
    db.commit()
    ath_id = ath.id
    db.close()

    # Offline client attempts to declare athlete as VERIFIED
    action = {
        "client_sync_id": f"SYNC-CONFLICT-VERIF-{datetime.datetime.utcnow().timestamp()}",
        "entity_name": "Athlete",
        "entity_id": ath_id,
        "action_type": "UPDATE",
        "client_timestamp": datetime.datetime.utcnow().isoformat(),
        "payload": {
            "verification_status": "VERIFIED",
            "guardian_ref": "Valid Guardian Contact"
        }
    }

    res = client.post(
        "/api/v1/sync/batch",
        json={"actions": [action]},
        headers={"x-user-id": "pune_dso"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["conflict_count"] == 1
    result = data["results"][0]
    assert result["status"] == "CONFLICT_SERVER_WON"
    assert "Server value 'REJECTED' retained" in result["conflict_notes"]

    # Verify database state retained server value
    db = SessionLocal()
    re_ath = db.query(Athlete).filter(Athlete.id == ath_id).first()
    assert re_ath.verification_status == "REJECTED"
    db.close()

def test_conflict_resolution_last_write_wins_on_contacts():
    """Requirement: Contact reference field accepts client mutation under last-write-wins."""
    db = SessionLocal()
    ath = db.query(Athlete).first()
    ath_id = ath.id
    db.close()

    new_guardian = "Mrs. Sunita Jadhav (Mother - Updated Offline)"
    action = {
        "client_sync_id": f"SYNC-LWW-CONTACT-{datetime.datetime.utcnow().timestamp()}",
        "entity_name": "Athlete",
        "entity_id": ath_id,
        "action_type": "UPDATE",
        "client_timestamp": datetime.datetime.utcnow().isoformat(),
        "payload": {"guardian_ref": new_guardian}
    }

    res = client.post(
        "/api/v1/sync/batch",
        json={"actions": [action]},
        headers={"x-user-id": "pune_dso"}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["applied_count"] == 1
    result = data["results"][0]
    assert result["status"] == "APPLIED"
    assert "guardian_ref" in result["applied_fields"]
