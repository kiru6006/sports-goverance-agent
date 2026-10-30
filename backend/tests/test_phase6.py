import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.entities import Athlete, User, AuditLog
from app.core.security_resilience import SecurityResilienceService
from app.core.db import SessionLocal, init_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def run_init():
    init_db()

def test_audit_hash_chain_verification_and_tamper_detection():
    """Verifies that the audit hash chain is cryptographically intact,
    and detects deliberate tampering with record_hash or prev_hash.
    """
    db = SessionLocal()
    try:
        from app.core.rbac import record_audit_event
        admin_user = db.query(User).filter(User.username == "admin").first()
        record_audit_event(db, admin_user, "CHAIN_INIT_TEST", "System", "0", {"test": True})

        # 1. Verification of untouched chain
        res = client.get("/api/v1/security/audit-chain/verify", headers={"x-user-id": "admin"})
        assert res.status_code == 200
        data = res.json()
        assert data["is_valid"] is True
        assert data["total_records"] >= 1
        assert data["broken_at_index"] is None

        # 2. Introduce artificial tamper in an audit log entry
        tampered_log = db.query(AuditLog).first()
        original_hash = tampered_log.record_hash
        tampered_log.record_hash = "TAMPERED_MALICIOUS_HASH_12345678"
        db.commit()

        # 3. Verification must fail
        res_tampered = client.get("/api/v1/security/audit-chain/verify", headers={"x-user-id": "admin"})
        assert res_tampered.status_code == 200
        tampered_data = res_tampered.json()
        assert tampered_data["is_valid"] is False
        assert tampered_data["broken_at_index"] == 0

        # Restore hash
        tampered_log.record_hash = original_hash
        db.commit()
    finally:
        db.close()

def test_agent_kill_switch_lifecycle_and_enforcement():
    """Ensures that toggling the security kill-switch prevents agent execution
    globally and regionally.
    """
    # 1. Status starts enabled
    res = client.get("/api/v1/security/killswitch", headers={"x-user-id": "admin"})
    assert res.status_code == 200
    status = res.json()
    assert status["is_globally_disabled"] is False

    # 2. Toggle kill-switch to DISABLED (global)
    res_toggle = client.post("/api/v1/security/killswitch", headers={"x-user-id": "admin"}, json={
        "disabled": True,
        "reason": "Security vulnerability test drill"
    })
    assert res_toggle.status_code == 200
    assert res_toggle.json()["is_globally_disabled"] is True

    # 3. Attempt agent query while kill-switch is active -> must fail with 403
    res_query = client.post("/api/v1/agent/chat", headers={"x-user-id": "pune_dso"}, json={
        "prompt": "What are the Khelo India age eligibility norms?"
    })
    assert res_query.status_code == 403

    # 4. Re-enable agent
    res_restore = client.post("/api/v1/security/killswitch", headers={"x-user-id": "admin"}, json={
        "disabled": False,
        "reason": "Drill completed"
    })
    assert res_restore.status_code == 200
    assert res_restore.json()["is_globally_disabled"] is False

    # 5. Agent query succeeds again
    res_query_ok = client.post("/api/v1/agent/chat", headers={"x-user-id": "pune_dso"}, json={
        "prompt": "What are the Khelo India age eligibility norms?"
    })
    assert res_query_ok.status_code == 200

def test_dpdp_erasure_workflow():
    """Validates statutory DPDP Act data erasure: PII is redacted,
    status set to DELETED, consent REVOKED, and audit log recorded.
    """
    db = SessionLocal()
    try:
        # Create test athlete
        res_create = client.post("/api/v1/registry/athletes", headers={"x-user-id": "pune_dso"}, json={
            "name": "Erasure Candidate",
            "dob": "2006-03-12",
            "gender": "MALE",
            "state_id": "MH",
            "district_id": "MH-PUN",
            "sport_code": "BOX",
            "guardian_ref": "Erasure Guardian",
            "consent_status": "GRANTED"
        })
        assert res_create.status_code in (200, 201)
        ath_id = res_create.json()["id"]

        # Execute DPDP erasure
        res_erasure = client.post(f"/api/v1/security/dpdp/erasure/{ath_id}", headers={"x-user-id": "pune_dso"})
        assert res_erasure.status_code == 200
        data = res_erasure.json()
        assert data["status"] == "ERASED"
        assert "encrypted_name" in data["redacted_fields"]

        # Verify athlete in DB
        ath_db = db.query(Athlete).filter(Athlete.id == ath_id).first()
        assert ath_db.encrypted_name == "REDACTED_DPDP"
        assert ath_db.verification_status == "DELETED"
        assert ath_db.consent_status == "REVOKED"
        assert ath_db.encrypted_dob == "REDACTED"
    finally:
        db.close()

def test_chaos_resilience_drill():
    """Executes automated non-destructive resilience and integrity checks."""
    res = client.post("/api/v1/security/chaos-drill", headers={"x-user-id": "admin"})
    assert res.status_code == 200
    data = res.json()
    assert data["passed"] is True
    assert data["status"] == "HEALTHY"
    check_names = [c["check"] for c in data["checks"]]
    assert "DATABASE_INTEGRITY" in check_names
    assert "AUDIT_HASH_CHAIN_INTEGRITY" in check_names
    assert "PII_ENCRYPTION_SUBSYSTEM" in check_names
