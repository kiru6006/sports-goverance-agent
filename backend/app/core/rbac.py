import hashlib
import json
from fastapi import Request, HTTPException, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import User, AuditLog

def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    username = request.headers.get("x-user-id", "pune_dso")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not recognized")
    return user

def require_role(*allowed_roles):
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403, 
                detail=f"Role {current_user.role} unauthorized. Requires one of: {allowed_roles}"
            )
        return current_user
    return role_checker

def verify_district_scope(requested_district_id: str, current_user: User):
    """Enforces geographic scope: DISTRICT_OFFICER can only access their own district."""
    if current_user.role == "NATIONAL_ADMIN":
        return True
    if current_user.role == "STATE_OFFICER":
        if not requested_district_id.startswith(current_user.state_id):
            raise HTTPException(status_code=403, detail="Cross-state access denied")
        return True
    if current_user.role in ("DISTRICT_OFFICER", "COACH"):
        if current_user.district_id != requested_district_id:
            raise HTTPException(status_code=403, detail="Cross-district access denied")
        return True
    raise HTTPException(status_code=403, detail="Unauthorized geographic scope")

def record_audit_event(
    db: Session,
    actor: User,
    action: str,
    target_entity: str,
    target_id: str,
    payload: dict
):
    payload_str = json.dumps(payload, sort_keys=True)
    payload_hash = hashlib.sha256(payload_str.encode()).hexdigest()
    
    last_log = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
    prev_hash = (last_log.record_hash or last_log.payload_hash) if last_log else "GENESIS_HASH_0000000000000000"

    record_content = f"{prev_hash}:{actor.username}:{action}:{target_entity}:{target_id}:{payload_hash}"
    record_hash = hashlib.sha256(record_content.encode()).hexdigest()

    audit_entry = AuditLog(
        actor_id=actor.username,
        actor_role=actor.role,
        actor_district=actor.district_id,
        action=action,
        target_entity=target_entity,
        target_id=target_id,
        payload_hash=payload_hash,
        prev_hash=prev_hash,
        record_hash=record_hash
    )
    db.add(audit_entry)
    db.commit()
