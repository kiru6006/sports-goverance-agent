import datetime
import json
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.rbac import get_current_user, verify_district_scope, record_audit_event
from app.core.crypto import encrypt_pii, decrypt_pii
from app.core.age_bands import get_age_band, calculate_age
from app.core.dedup import find_duplicate_candidates
from app.models.entities import (
    User, Athlete, Sport, Facility, Achievement, JourneyEvent, PipelineSnapshot, AuditLog
)
from app.schemas.dto import (
    AthleteSummary, AthleteDetail, AchievementResponse, JourneyEventResponse,
    OnboardAthleteRequest, CheckDuplicateRequest, DuplicateCheckResponse, DuplicateCandidate,
    VerificationTransitionRequest, JourneyEventCreateRequest, FacilityResponse,
    PipelineMetric, AuditLogEntry, UserResponse
)

api_router = APIRouter()

@api_router.get("/auth/me", response_model=UserResponse)
def get_auth_context(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.get("/auth/users", response_model=List[UserResponse])
def list_demo_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Duplicate Candidate Check (Never auto-merges)
@api_router.post("/registry/athletes/check-duplicate", response_model=DuplicateCheckResponse)
def check_duplicate_candidate(
    req: CheckDuplicateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    athletes = db.query(Athlete).all()
    decrypted_list = []
    for a in athletes:
        decrypted_list.append({
            "id": a.id,
            "kid": a.kid,
            "name": decrypt_pii(a.encrypted_name),
            "dob": decrypt_pii(a.encrypted_dob),
            "district_id": a.district_id
        })

    candidates = find_duplicate_candidates(
        name=req.name,
        dob_str=req.dob,
        district_id=req.district_id,
        existing_athletes=decrypted_list
    )

    return DuplicateCheckResponse(
        is_duplicate_candidate=len(candidates) > 0,
        candidates=[DuplicateCandidate(**c) for c in candidates],
        auto_merged=False,
        message="Deduplication candidates evaluated. Auto-merge disabled. Human review required." if candidates else "No duplicates detected."
    )

# Athlete Onboarding
@api_router.post("/registry/athletes", response_model=AthleteSummary, status_code=status.HTTP_201_CREATED)
def onboard_athlete(
    req: OnboardAthleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verify geographic scope for creation
    verify_district_scope(req.district_id, current_user)

    # Parse and compute age
    try:
        dob_date = datetime.date.fromisoformat(req.dob)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format for DOB, expected YYYY-MM-DD")

    age = calculate_age(dob_date)
    is_minor = age < 18

    # Minor Consent Invariant: Under 18 requires consent_status
    if is_minor:
        if not req.consent_status or req.consent_status not in ("GRANTED", "PENDING"):
            raise HTTPException(
                status_code=422,
                detail="Minor record submission requires explicit guardian consent_status (GRANTED/PENDING)"
            )
        if not req.guardian_ref:
            raise HTTPException(
                status_code=422,
                detail="Guardian reference is required for minor athletes"
            )

    sport = db.query(Sport).filter(Sport.code == req.sport_code).first()
    if not sport:
        raise HTTPException(status_code=404, detail=f"Sport code {req.sport_code} not recognized")

    kid_generated = f"KID-{req.state_id}-{datetime.datetime.utcnow().year}-{math.floor(math.sin(len(req.name))*1000 + 5000)}"

    athlete = Athlete(
        kid=kid_generated,
        encrypted_name=encrypt_pii(req.name),
        encrypted_dob=encrypt_pii(req.dob),
        gender=req.gender,
        state_id=req.state_id,
        district_id=req.district_id,
        primary_sport_id=sport.id,
        encrypted_guardian=encrypt_pii(req.guardian_ref) if req.guardian_ref else None,
        consent_status=req.consent_status or "GRANTED",
        verification_status="SUBMITTED",
        coach_id=current_user.id if current_user.role == "COACH" else None,
        is_minor=is_minor,
        is_synthetic=True
    )
    db.add(athlete)
    db.commit()
    db.refresh(athlete)

    record_audit_event(
        db, current_user, "ONBOARD_ATHLETE", "Athlete", athlete.id,
        {"district": athlete.district_id, "is_minor": is_minor}
    )

    age_band = get_age_band(dob_date)

    return AthleteSummary(
        id=athlete.id,
        kid=athlete.kid,
        name=req.name,
        gender=athlete.gender,
        state_id=athlete.state_id,
        district_id=athlete.district_id,
        sport_name=sport.name,
        age_band=age_band,
        consent_status=athlete.consent_status,
        verification_status=athlete.verification_status,
        is_minor=athlete.is_minor,
        is_synthetic=athlete.is_synthetic
    )

# List Athletes with filtering & scope enforcement
@api_router.get("/registry/athletes", response_model=List[AthleteSummary])
def list_athletes(
    district_id: Optional[str] = None,
    sport_code: Optional[str] = None,
    verification_status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Athlete, Sport).join(Sport, Athlete.primary_sport_id == Sport.id)
    
    if current_user.role in ("DISTRICT_OFFICER", "COACH"):
        query = query.filter(Athlete.district_id == current_user.district_id)
    elif current_user.role == "STATE_OFFICER":
        query = query.filter(Athlete.state_id == current_user.state_id)
        if district_id:
            query = query.filter(Athlete.district_id == district_id)
    elif current_user.role == "NATIONAL_ADMIN":
        if district_id:
            query = query.filter(Athlete.district_id == district_id)

    if sport_code:
        query = query.filter(Sport.code == sport_code)
    if verification_status:
        query = query.filter(Athlete.verification_status == verification_status)

    results = query.all()
    summaries = []
    
    for ath, sport in results:
        # Conceal minor records to unauthorized viewers
        if ath.is_minor and current_user.role not in ("NATIONAL_ADMIN", "STATE_OFFICER") and current_user.district_id != ath.district_id:
            continue
        
        dob_str = decrypt_pii(ath.encrypted_dob)
        try:
            dob_date = datetime.date.fromisoformat(dob_str)
            age_band = get_age_band(dob_date)
        except Exception:
            age_band = "Unknown"

        if ath.is_minor:
            record_audit_event(
                db, current_user, "READ_MINOR_RECORD", "Athlete", ath.id, {"district": ath.district_id}
            )

        summaries.append(AthleteSummary(
            id=ath.id,
            kid=ath.kid,
            name=decrypt_pii(ath.encrypted_name),
            gender=ath.gender,
            state_id=ath.state_id,
            district_id=ath.district_id,
            sport_name=sport.name,
            age_band=age_band,
            consent_status=ath.consent_status,
            verification_status=ath.verification_status,
            is_minor=ath.is_minor,
            is_synthetic=ath.is_synthetic
        ))
    return summaries

# Athlete Details (Profile + Journey Timeline)
@api_router.get("/registry/athletes/{athlete_id}", response_model=AthleteDetail)
def get_athlete_details(
    athlete_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    row = db.query(Athlete, Sport).join(Sport, Athlete.primary_sport_id == Sport.id).filter(Athlete.id == athlete_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Athlete record not found")
    
    ath, sport = row
    
    # Minor concealment invariant: unauthorized roles get 404, never 403
    if ath.is_minor and current_user.role in ("DISTRICT_OFFICER", "COACH") and current_user.district_id != ath.district_id:
        raise HTTPException(status_code=404, detail="Athlete record not found")

    if ath.is_minor:
        record_audit_event(
            db, current_user, "READ_MINOR_PROFILE", "Athlete", ath.id, {"district": ath.district_id}
        )

    dob_str = decrypt_pii(ath.encrypted_dob)
    try:
        dob_date = datetime.date.fromisoformat(dob_str)
        age_band = get_age_band(dob_date)
    except Exception:
        age_band = "Unknown"

    achievements = db.query(Achievement).filter(Achievement.athlete_id == ath.id).all()
    journey_events = db.query(JourneyEvent).filter(JourneyEvent.athlete_id == ath.id).order_by(JourneyEvent.event_date.desc()).all()

    return AthleteDetail(
        id=ath.id,
        kid=ath.kid,
        name=decrypt_pii(ath.encrypted_name),
        gender=ath.gender,
        state_id=ath.state_id,
        district_id=ath.district_id,
        sport_name=sport.name,
        age_band=age_band,
        consent_status=ath.consent_status,
        verification_status=ath.verification_status,
        is_minor=ath.is_minor,
        is_synthetic=ath.is_synthetic,
        achievements=[
            AchievementResponse(
                id=a.id,
                event=a.event,
                level=a.level,
                result=a.result,
                event_date=a.event_date.isoformat()
            ) for a in achievements
        ],
        journey_events=[
            JourneyEventResponse(
                id=j.id,
                event_type=j.event_type,
                event_date=j.event_date.isoformat(),
                notes=j.notes,
                created_at=j.created_at.isoformat()
            ) for j in journey_events
        ]
    )

# Verification State Machine Transition
VALID_TRANSITIONS = {
    "SUBMITTED": ["UNDER_REVIEW"],
    "UNDER_REVIEW": ["VERIFIED", "REJECTED", "NEEDS_INFO"],
    "NEEDS_INFO": ["SUBMITTED"],
    "VERIFIED": ["UNDER_REVIEW"],
    "REJECTED": []
}

@api_router.post("/registry/athletes/{athlete_id}/verify", response_model=AthleteSummary)
def transition_verification_status(
    athlete_id: str,
    req: VerificationTransitionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ath = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not ath:
        raise HTTPException(status_code=404, detail="Athlete record not found")

    # Authorisation: Only District Officer or above can verify
    if current_user.role not in ("DISTRICT_OFFICER", "STATE_OFFICER", "NATIONAL_ADMIN"):
        raise HTTPException(status_code=403, detail="Coaches cannot execute verification transitions")

    # Authorisation: Scope check
    if current_user.role == "DISTRICT_OFFICER" and current_user.district_id != ath.district_id:
        raise HTTPException(status_code=403, detail="District Officers can only verify athletes within their district")

    # Invariant: Coach cannot verify their own athlete
    if ath.coach_id and ath.coach_id == current_user.id:
        raise HTTPException(status_code=403, detail="Conflict of interest: You cannot verify an athlete you coach")

    current_status = ath.verification_status
    allowed_next = VALID_TRANSITIONS.get(current_status, [])

    if req.target_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid verification transition from {current_status} to {req.target_status}. Allowed next states: {allowed_next}"
        )

    # Execute transition
    ath.verification_status = req.target_status
    ath.verifier_id = current_user.id
    ath.verification_notes = req.reason
    ath.verified_at = datetime.datetime.utcnow()
    db.commit()

    record_audit_event(
        db, current_user, "VERIFICATION_TRANSITION", "Athlete", ath.id,
        {"from": current_status, "to": req.target_status, "reason": req.reason}
    )

    sport = db.query(Sport).filter(Sport.id == ath.primary_sport_id).first()
    dob_str = decrypt_pii(ath.encrypted_dob)
    try:
        dob_date = datetime.date.fromisoformat(dob_str)
        age_band = get_age_band(dob_date)
    except Exception:
        age_band = "Unknown"

    return AthleteSummary(
        id=ath.id,
        kid=ath.kid,
        name=decrypt_pii(ath.encrypted_name),
        gender=ath.gender,
        state_id=ath.state_id,
        district_id=ath.district_id,
        sport_name=sport.name,
        age_band=age_band,
        consent_status=ath.consent_status,
        verification_status=ath.verification_status,
        is_minor=ath.is_minor,
        is_synthetic=ath.is_synthetic
    )

# Append-Only Journey Events
@api_router.post("/registry/athletes/{athlete_id}/journey", response_model=JourneyEventResponse, status_code=status.HTTP_201_CREATED)
def append_journey_event(
    athlete_id: str,
    req: JourneyEventCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ath = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not ath:
        raise HTTPException(status_code=404, detail="Athlete record not found")

    verify_district_scope(ath.district_id, current_user)

    try:
        event_date = datetime.date.fromisoformat(req.event_date)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format, expected YYYY-MM-DD")

    event = JourneyEvent(
        athlete_id=ath.id,
        event_type=req.event_type,
        event_date=event_date,
        notes=req.notes
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    record_audit_event(
        db, current_user, "APPEND_JOURNEY_EVENT", "JourneyEvent", event.id,
        {"athlete_id": ath.id, "type": req.event_type}
    )

    return JourneyEventResponse(
        id=event.id,
        event_type=event.event_type,
        event_date=event.event_date.isoformat(),
        notes=event.notes,
        created_at=event.created_at.isoformat()
    )

@api_router.put("/registry/athletes/{athlete_id}/journey/{journey_id}")
def update_journey_event_rejected():
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Journey events are strictly append-only")

@api_router.delete("/registry/athletes/{athlete_id}/journey/{journey_id}")
def delete_journey_event_rejected():
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Journey events are strictly append-only")

# Facilities with Radius Query
@api_router.get("/facilities", response_model=List[FacilityResponse])
def list_facilities(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    radius_km: Optional[float] = 50.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Facility)
    if current_user.role in ("DISTRICT_OFFICER", "COACH"):
        query = query.filter(Facility.district_id == current_user.district_id)
    elif current_user.role == "STATE_OFFICER":
        query = query.filter(Facility.state_id == current_user.state_id)

    facilities = query.all()
    out = []

    for f in facilities:
        if lat is not None and lon is not None:
            # Haversine distance
            dlat = math.radians(f.latitude - lat)
            dlon = math.radians(f.longitude - lon)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat)) * math.cos(math.radians(f.latitude)) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            dist = 6371 * c
            if dist > (radius_km or 50.0):
                continue

        out.append(FacilityResponse(
            id=f.id,
            name=f.name,
            type=f.type,
            district_id=f.district_id,
            latitude=f.latitude,
            longitude=f.longitude,
            sports=json.loads(f.sports_json) if f.sports_json else []
        ))
    return out

# Pipeline Diagnosis Snapshots
@api_router.get("/pipeline/snapshots", response_model=List[PipelineMetric])
def get_pipeline_snapshots(
    district_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(PipelineSnapshot, Sport).join(Sport, PipelineSnapshot.sport_id == Sport.id)
    
    if current_user.role in ("DISTRICT_OFFICER", "COACH"):
        query = query.filter(PipelineSnapshot.district_id == current_user.district_id)
    elif current_user.role == "STATE_OFFICER":
        query = query.filter(PipelineSnapshot.state_id == current_user.state_id)
        if district_id:
            query = query.filter(PipelineSnapshot.district_id == district_id)
    elif current_user.role == "NATIONAL_ADMIN":
        if district_id:
            query = query.filter(PipelineSnapshot.district_id == district_id)

    metrics = []
    for snap, sport in query.all():
        identified = None if snap.is_suppressed else snap.identified_count
        verified = None if snap.is_suppressed else snap.verified_count
        supported = None if snap.is_suppressed else snap.supported_count
        progressed = None if snap.is_suppressed else snap.progressed_count

        metrics.append(PipelineMetric(
            district_id=snap.district_id,
            state_id=snap.state_id,
            sport_code=sport.code,
            sport_name=sport.name,
            age_band=snap.age_band,
            identified_count=identified,
            verified_count=verified,
            supported_count=supported,
            progressed_count=progressed,
            is_suppressed=snap.is_suppressed,
            as_of=snap.as_of.isoformat()
        ))
    return metrics

# Audit Trail
@api_router.get("/audit/logs", response_model=List[AuditLogEntry])
def list_audit_trail(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        AuditLogEntry(
            timestamp=l.timestamp.isoformat(),
            actor_id=l.actor_id,
            actor_role=l.actor_role,
            action=l.action,
            target_entity=l.target_entity,
            target_id=l.target_id,
            payload_hash=l.payload_hash,
            prev_hash=l.prev_hash
        ) for l in logs
    ]
