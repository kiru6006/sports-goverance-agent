import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.db import SessionLocal, init_db
from app.core.seed_phase1 import seed_registry_data
from app.core.seed_phase2 import seed_phase2_data
from app.core.seed_phase3 import seed_phase3_data
from app.core.seed_phase4 import seed_policy_chunks
from app.models.entities import ActionProposal, AuditLog

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_db()
    seed_registry_data()
    seed_phase2_data()
    seed_phase3_data()
    seed_policy_chunks()
    yield

def test_agent_write_isolation_and_proposal_token():
    """Requirement: Agent cannot mutate database state directly; emits ActionProposal requiring approval token."""
    res = client.post(
        "/api/v1/agent/chat",
        json={"prompt": "Verify athlete Aarav Patil for state talent assessment scheme"},
        headers={"x-user-id": "pune_dso"}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["proposed_actions"]) > 0
    proposal = data["proposed_actions"][0]
    token = proposal["approval_token"]
    proposal_id = proposal["proposal_id"]
    assert token.startswith("PROPOSAL-TOKEN-")

    # Try to execute proposal with wrong token -> 403 Forbidden
    bad_exec = client.post(
        f"/api/v1/agent/proposals/{proposal_id}/execute",
        json={"approval_token": "INVALID-WRONG-TOKEN", "approval_notes": "Attempting illegal execute"},
        headers={"x-user-id": "pune_dso"}
    )
    assert bad_exec.status_code == 403

    # Execute with correct token -> 200 Success
    good_exec = client.post(
        f"/api/v1/agent/proposals/{proposal_id}/execute",
        json={"approval_token": token, "approval_notes": "Sanctioned after verification audit"},
        headers={"x-user-id": "pune_dso"}
    )
    assert good_exec.status_code == 200
    assert good_exec.json()["status"] == "EXECUTED"

    # Replay protection: Re-executing already executed proposal returns 409 Conflict
    replay_exec = client.post(
        f"/api/v1/agent/proposals/{proposal_id}/execute",
        json={"approval_token": token, "approval_notes": "Replay attempt"},
        headers={"x-user-id": "pune_dso"}
    )
    assert replay_exec.status_code == 409

def test_agent_rbac_and_geo_scoping():
    """Requirement: Pune DSO cannot query or leak athletes from another district (e.g. Sonipat HR-SON)."""
    res = client.post(
        "/api/v1/agent/chat",
        json={"prompt": "List all athletes and boxers"},
        headers={"x-user-id": "pune_dso"}
    )
    assert res.status_code == 200
    data = res.json()
    tool_calls = data["tool_calls_executed"]
    assert len(tool_calls) > 0
    ath_tool = next(tc for tc in tool_calls if tc["tool"] == "search_athletes")
    athletes = ath_tool["result"]["athletes"]
    
    # Pune DSO must ONLY see Pune athletes (MH-PUN)
    for a in athletes:
        assert a["district_id"] == "MH-PUN"
        assert a["district_id"] != "HR-SON"

def test_policy_rag_100_percent_citation():
    """Requirement: Policy queries return official source document, page, and clause."""
    res = client.post(
        "/api/v1/agent/chat",
        json={"prompt": "What are the talent identification benchmarks and verification requirements?"},
        headers={"x-user-id": "admin"}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["citations"]) > 0
    top_cite = data["citations"][0]
    assert "MYAS Khelo India Operational Guidelines" in top_cite["source_document"]
    assert "Clause 4.2" in top_cite["source_clause"]
    assert "Page 28" in top_cite["source_page"]
    assert data["confidence_level"] == "HIGH"

def test_policy_rag_fallback_on_unsupported_query():
    """Requirement: Answers without an approved source strictly return fallback notice."""
    res = client.post(
        "/api/v1/agent/chat",
        json={"prompt": "What are the tax implications of cryptocurrency trading in Mars colony?"},
        headers={"x-user-id": "admin"}
    )
    assert res.status_code == 200
    data = res.json()
    assert len(data["citations"]) == 0
    assert "No source found in approved guidelines" in data["response_text"]
    assert data["confidence_level"] == "LOW"

def test_agent_audit_log_recorded():
    """Requirement: Agent interactions are logged with prompt metadata into audit trail."""
    db = SessionLocal()
    agent_logs = db.query(AuditLog).filter(AuditLog.action == "AGENT_QUERY").all()
    assert len(agent_logs) > 0
    latest_log = agent_logs[-1]
    assert latest_log.target_entity == "AgentService"
    assert latest_log.payload_hash is not None
    db.close()
