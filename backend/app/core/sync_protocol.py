import json
import datetime
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session
from app.models.entities import Athlete, OfflineSyncRecord, User
from app.core.crypto import encrypt_pii

# Fields where Server Wins over client mutations during offline sync
SERVER_WINS_FIELDS = {"verification_status", "verifier_id", "verified_at", "consent_status", "is_minor"}

# Fields where Last-Write-Wins based on client timestamp
LAST_WRITE_WINS_FIELDS = {"encrypted_guardian", "guardian_ref", "verification_notes"}

def resolve_offline_sync_action(
    action: Dict[str, Any],
    submitted_by_user: User,
    db: Session
) -> Dict[str, Any]:
    """Applies conflict resolution matrix:
    - Verification fields: Server state wins. Attempting to override returns CONFLICT_SERVER_WON.
    - Contact/notes fields: Client updates applied under last-write-wins.
    - Duplicate client_sync_id: Idempotent no-op.
    """
    client_sync_id = action["client_sync_id"]
    entity_name = action["entity_name"]
    entity_id = action["entity_id"]
    payload = action["payload"]
    client_ts_str = action["client_timestamp"]
    
    try:
        client_ts = datetime.datetime.fromisoformat(client_ts_str.replace("Z", "+00:00"))
    except Exception:
        client_ts = datetime.datetime.utcnow()

    # Check idempotency
    existing_sync = db.query(OfflineSyncRecord).filter(OfflineSyncRecord.client_sync_id == client_sync_id).first()
    if existing_sync:
        return {
            "client_sync_id": client_sync_id,
            "status": existing_sync.status,
            "conflict_notes": "Idempotent duplicate sync action ignored.",
            "applied_fields": []
        }

    applied_fields = []
    conflict_notes = None
    action_status = "APPLIED"

    if entity_name == "Athlete":
        athlete = db.query(Athlete).filter(Athlete.id == entity_id).first()
        if not athlete:
            return {
                "client_sync_id": client_sync_id,
                "status": "REJECTED",
                "conflict_notes": f"Athlete {entity_id} not found on server.",
                "applied_fields": []
            }

        # Check server-wins violation
        for f in SERVER_WINS_FIELDS:
            if f in payload and payload[f] != getattr(athlete, f, None):
                action_status = "CONFLICT_SERVER_WON"
                conflict_notes = (
                    f"Conflict on '{f}': Server value '{getattr(athlete, f)}' retained over offline client value '{payload[f]}'."
                )
                break

        # Apply last-write-wins non-sensitive contact fields
        if "guardian_ref" in payload:
            athlete.encrypted_guardian = encrypt_pii(payload["guardian_ref"])
            applied_fields.append("guardian_ref")
        if "verification_notes" in payload and action_status == "APPLIED":
            athlete.verification_notes = payload["verification_notes"]
            applied_fields.append("verification_notes")

    # Record sync journal
    sync_entry = OfflineSyncRecord(
        client_sync_id=client_sync_id,
        entity_name=entity_name,
        entity_id=entity_id,
        client_timestamp=client_ts,
        server_timestamp=datetime.datetime.utcnow(),
        payload_json=json.dumps(payload),
        status=action_status,
        conflict_notes=conflict_notes,
        submitted_by=submitted_by_user.id
    )
    db.add(sync_entry)
    db.commit()

    return {
        "client_sync_id": client_sync_id,
        "status": action_status,
        "conflict_notes": conflict_notes,
        "applied_fields": applied_fields
    }

def process_batch_sync(actions: List[Dict[str, Any]], user: User, db: Session) -> Dict[str, Any]:
    """Processes a batch of offline synchronization records."""
    results = []
    applied_count = 0
    conflict_count = 0

    for act in actions:
        res = resolve_offline_sync_action(act, user, db)
        if res["status"] == "APPLIED":
            applied_count += 1
        elif res["status"] == "CONFLICT_SERVER_WON":
            conflict_count += 1
        results.append(res)

    return {
        "total_received": len(actions),
        "applied_count": applied_count,
        "conflict_count": conflict_count,
        "results": results
    }
