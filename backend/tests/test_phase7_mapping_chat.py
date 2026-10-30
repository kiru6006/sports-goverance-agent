import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_candidate_rejection_audit_and_report():
    # 1. Onboard a fresh athlete candidate to guarantee SUBMITTED status
    onboard_payload = {
        "name": "Audit Test Candidate",
        "dob": "2006-03-12",
        "gender": "MALE",
        "state_id": "MH",
        "district_id": "MH-PUN",
        "sport_code": "BOX",
        "guardian_ref": "Mr. Test Guardian",
        "consent_status": "GRANTED"
    }
    res_onboard = client.post("/api/v1/registry/athletes", json=onboard_payload, headers={"x-user-id": "pune_dso"})
    assert res_onboard.status_code in (200, 201)
    ath = res_onboard.json()
    ath_id = ath["id"]

    # 2. Transition from SUBMITTED to UNDER_REVIEW
    res_ur = client.post(
        f"/api/v1/registry/athletes/{ath_id}/verify",
        json={"target_status": "UNDER_REVIEW", "reason": "Officer initiating audit review"},
        headers={"x-user-id": "pune_dso"}
    )
    assert res_ur.status_code == 200

    # 2. Transition verification to REJECTED with reason and comprehensive report
    rejection_payload = {
        "target_status": "REJECTED",
        "reason": "Date of Birth certificate discrepancy with Aadhaar card",
        "rejection_report": "Field Audit Report:\n1. Birth certificate issued by non-accredited authority.\n2. Discrepancy of 2 years in primary schooling admission record.\n3. Verified by MH State Director on-site."
    }
    res_reject = client.post(
        f"/api/v1/registry/athletes/{ath_id}/verify",
        json=rejection_payload,
        headers={"x-user-id": "mh_officer"}
    )
    assert res_reject.status_code == 200
    res_data = res_reject.json()
    assert res_data["verification_status"] == "REJECTED"

    # 3. Retrieve athlete details to verify who rejected, why rejected, and full report
    res_details = client.get(f"/api/v1/registry/athletes/{ath_id}", headers={"x-user-id": "mh_officer"})
    assert res_details.status_code == 200
    details = res_details.json()
    assert details["verification_status"] == "REJECTED"
    assert details["rejection_reason"] == rejection_payload["reason"]
    assert details["rejection_report"] == rejection_payload["rejection_report"]
    assert "Maharashtra State Officer" in details["rejected_by"] or "mh_officer" in details["rejected_by"]

def test_direct_messaging_channel():
    # Send a message between coach and official regarding an athlete
    msg_payload = {
        "recipient_id": "mh_officer@sports.gov.in",
        "recipient_name": "MH State Director",
        "recipient_role": "STATE_OFFICER",
        "athlete_context_id": "test-ath-1",
        "message_text": "Requesting clarification on the verification requirements for national camp entry."
    }
    res_send = client.post(
        "/api/v1/messages",
        json=msg_payload,
        headers={"x-user-id": "pune_coach"}
    )
    assert res_send.status_code in (200, 201)
    msg_data = res_send.json()
    assert msg_data["sender_id"] == "pune_coach"
    assert msg_data["recipient_id"] == msg_payload["recipient_id"]
    assert msg_data["message_text"] == msg_payload["message_text"]

    # Retrieve messages
    res_msgs = client.get("/api/v1/messages", headers={"x-user-id": "pune_coach"})
    assert res_msgs.status_code == 200
    msgs = res_msgs.json()
    assert any(m["message_text"] == msg_payload["message_text"] for m in msgs)

def test_profile_mapping_support_demands_and_services():
    res = client.get("/api/v1/registry/athletes", headers={"x-user-id": "mh_officer"})
    ath_id = res.json()[0]["id"]

    mapping_payload = {
        "support_demands": ["High-altitude conditioning", "Sports orthopedic consultation", "Kitting sponsorship"],
        "services_offered": ["Sparring partner for sub-junior category", "Youth clinic mentor"],
        "services_needed": ["Sports nutritionist", "Sports physiotherapist", "Biomechanical video review"],
        "specialist_contact_ref": "Dr. Joshi, SAI High Performance Centre"
    }
    res_update = client.put(
        f"/api/v1/registry/athletes/{ath_id}/profile-mapping",
        json=mapping_payload,
        headers={"x-user-id": "pune_coach"}
    )
    assert res_update.status_code == 200
    updated_ath = res_update.json()
    assert "High-altitude conditioning" in updated_ath["support_demands"]
    assert "Sparring partner for sub-junior category" in updated_ath["services_offered"]
    assert "Sports nutritionist" in updated_ath["services_needed"]
    assert updated_ath["specialist_contact_ref"] == "Dr. Joshi, SAI High Performance Centre"
