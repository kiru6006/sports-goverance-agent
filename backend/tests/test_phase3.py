import json
import datetime
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, init_db
from app.core.seed_phase1 import seed_registry_data
from app.core.seed_phase2 import seed_phase2_data
from app.core.seed_phase3 import seed_phase3_data
from app.models.entities import (
    User, Athlete, Scheme, SchemeRule, Opportunity, Trainer, TrainerCertification, OutboxMessage
)

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    seed_registry_data()
    seed_phase2_data()
    seed_phase3_data()
    yield

def test_draft_or_retired_rule_never_affects_eligibility():
    """Requirement: Only APPROVED rules produce deterministic eligibility results."""
    db = SessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    scheme = db.query(Scheme).first()
    ath = db.query(Athlete).first()
    
    # Create draft rule
    draft_rule = SchemeRule(
        scheme_id=scheme.id,
        version="9.9.9-draft",
        rule_json=json.dumps({
            "schema_version": "1.0",
            "required_fields": ["age"],
            "criteria": [{"field": "age", "operator": "gte", "value": 1, "reason_text": "Always true"}]
        }),
        effective_from=datetime.date(2025, 1, 1),
        source_document="Draft doc",
        source_page="p1",
        source_clause="c1",
        status="DRAFT",
        author_id=admin.id
    )
    db.add(draft_rule)
    db.commit()
    draft_rule_id = draft_rule.id
    ath_id = ath.id
    db.close()

    res = client.get(f"/api/v1/eligibility/athlete/{ath_id}", headers={"X-Actor-Role": "NATIONAL_ADMIN"})
    assert res.status_code == 200
    data = res.json()
    evaluated_versions = [r["rule_version"] for r in data]
    assert "9.9.9-draft" not in evaluated_versions

def test_maker_checker_violation():
    """Requirement: The rule author CANNOT approve their own rule (HTTP 403)."""
    db = SessionLocal()
    scheme = db.query(Scheme).first()
    officer = db.query(User).filter(User.username == "mh_officer").first()
    admin = db.query(User).filter(User.username == "admin").first()
    scheme_id = scheme.id
    officer_id = officer.id
    admin_id = admin.id
    db.close()

    draft_payload = {
        "scheme_id": scheme_id,
        "version": "2.0.0-test",
        "rule_dict": {
            "schema_version": "1.0",
            "required_fields": ["age"],
            "criteria": [
                {"field": "age", "operator": "between", "value": [12, 18], "reason_text": "Age 12-18"}
            ]
        },
        "effective_from": "2026-01-01",
        "source_document": "Policy Guideline 2026",
        "source_page": "Page 10",
        "source_clause": "Clause 2.1"
    }

    create_res = client.post(
        "/api/v1/schemes/rules",
        json=draft_payload,
        headers={"x-user-id": "mh_officer"}
    )
    assert create_res.status_code == 201
    rule_id = create_res.json()["id"]

    # Same officer tries to approve -> must fail with 403 Maker-Checker Violation
    approve_res = client.post(
        f"/api/v1/schemes/rules/{rule_id}/approve",
        json={"rule_id": rule_id, "approval_reason": "Self-approving my rule"},
        headers={"x-user-id": "mh_officer"}
    )
    assert approve_res.status_code == 403
    assert "Maker-Checker Violation" in approve_res.json()["detail"]

    # Distinct officer (admin) approves -> succeeds
    approve_ok = client.post(
        f"/api/v1/schemes/rules/{rule_id}/approve",
        json={"rule_id": rule_id, "approval_reason": "Verified and sanctioned"},
        headers={"x-user-id": "admin"}
    )
    assert approve_ok.status_code == 200
    assert approve_ok.json()["status"] == "APPROVED"

def test_approved_rule_immutability():
    """Requirement: Updating an approved rule returns HTTP 409 Conflict."""
    db = SessionLocal()
    approved_rule = db.query(SchemeRule).filter(SchemeRule.status == "APPROVED").first()
    rule_id = approved_rule.id
    db.close()

    res = client.put(f"/api/v1/schemes/rules/{rule_id}", headers={"x-user-id": "admin"})
    assert res.status_code == 409
    assert "immutable" in res.json()["detail"].lower()

def test_missing_required_fields_return_null_never_false():
    """Requirement: Missing required fields must produce eligible: null, missing_fields list, never false."""
    db = SessionLocal()
    ath = db.query(Athlete).first()
    ath_id = ath.id
    db.close()

    res = client.get(f"/api/v1/eligibility/athlete/{ath_id}", headers={"x-user-id": "admin"})
    assert res.status_code == 200
    evals = res.json()
    assert len(evals) > 0
    # Athletes in seed lack highest_achievement_level so missing_fields triggers
    for ev in evals:
        if ev.get("missing_fields"):
            assert ev["eligible"] is None

def test_invalid_rule_json_rejected():
    """Requirement: Strict closed schema validation; unrecognized keys or invalid structure rejected with 422."""
    db = SessionLocal()
    scheme = db.query(Scheme).first()
    scheme_id = scheme.id
    db.close()

    bad_payload = {
        "scheme_id": scheme_id,
        "version": "9.9.0-bad",
        "rule_dict": {
            "schema_version": "1.0",
            "required_fields": ["age"],
            "criteria": [
                {"field": "age", "operator": "unknown_operator", "value": 15, "reason_text": "Bad op"}
            ]
        },
        "effective_from": "2026-01-01",
        "source_document": "Bad doc",
        "source_page": "p1",
        "source_clause": "c1"
    }
    res = client.post(
        "/api/v1/schemes/rules",
        json=bad_payload,
        headers={"x-user-id": "mh_officer"}
    )
    assert res.status_code == 422

def test_revoked_certification_blocks_placement():
    """Requirement: Trainer with REVOKED certification cannot be placed (HTTP 409)."""
    db = SessionLocal()
    trainer = db.query(Trainer).first()
    from app.models.entities import Institution
    inst = db.query(Institution).first()
    trainer_id = trainer.id
    inst_id = inst.id

    # Add a revoked certification for this trainer
    revoked_cert = TrainerCertification(
        trainer_id=trainer_id,
        course="Ethics Violation Course",
        provider="SAI",
        issued_on=datetime.date(2020, 1, 1),
        expires_on=datetime.date(2025, 1, 1),
        status="REVOKED"
    )
    db.add(revoked_cert)
    db.commit()
    db.close()

    payload = {
        "trainer_id": trainer_id,
        "institution_id": inst_id,
        "role": "HEAD_COACH",
        "start_date": "2026-11-01"
    }
    res = client.post(
        "/api/v1/placements",
        json=payload,
        headers={"X-Actor-Role": "STATE_OFFICER"}
    )
    assert res.status_code == 409
    assert "revoked certification" in res.json()["detail"].lower()

def test_outbox_message_zero_minor_pii():
    """Requirement: Outbox messages store only anonymized reference token; zero plain PII."""
    db = SessionLocal()
    opp = db.query(Opportunity).first()
    ath = db.query(Athlete).filter(Athlete.is_minor == True).first()
    if not ath:
        ath = db.query(Athlete).first()
    opp_id = opp.id
    ath_id = ath.id
    db.close()

    app_payload = {
        "opportunity_id": opp_id,
        "athlete_id": ath_id,
        "status_reason": "Meets all criteria based on recent state championship gold medal"
    }
    res = client.post(
        "/api/v1/opportunities/apply",
        json=app_payload,
        headers={"X-Actor-Role": "NATIONAL_ADMIN"}
    )
    assert res.status_code == 201

    # Verify outbox messages
    db = SessionLocal()
    messages = db.query(OutboxMessage).all()
    assert len(messages) > 0
    for msg in messages:
        payload_data = json.loads(msg.payload_json)
        # Verify no direct plain PII
        assert "first_name" not in payload_data
        assert "last_name" not in payload_data
        assert "phone" not in payload_data
        assert "aadhaar" not in payload_data
        assert "dob" not in payload_data
        assert "token" in payload_data
    db.close()
