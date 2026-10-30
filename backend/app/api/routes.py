import datetime
import json
import math
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.rbac import get_current_user, verify_district_scope, record_audit_event
from app.core.crypto import encrypt_pii, decrypt_pii
from app.core.age_bands import get_age_band, calculate_age
from app.core.dedup import find_duplicate_candidates
from app.core.pipeline_engine import evaluate_district_gap, calculate_funnel_stages, compute_peer_median
from app.core.eligibility_engine import validate_rule_json, evaluate_scheme_eligibility
from app.models.entities import (
    User, Athlete, Sport, Facility, Achievement, JourneyEvent, PipelineSnapshot, AuditLog,
    Population, SupportRecord, EquipmentItem, EquipmentLoan, FacilityUtilisation,
    Scheme, SchemeRule, EligibilityResult, Opportunity, OpportunityApplication,
    TrainerCertification, Placement, OutboxMessage, Trainer, Institution,
    PolicyChunk, ActionProposal, StateAdapterManifest, OfflineSyncRecord
)
from app.schemas.dto import (
    AthleteSummary, AthleteDetail, AchievementResponse, JourneyEventResponse,
    OnboardAthleteRequest, CheckDuplicateRequest, DuplicateCheckResponse, DuplicateCandidate,
    VerificationTransitionRequest, JourneyEventCreateRequest, FacilityResponse,
    HeatmapCell, FunnelResponse, EquipmentItemResponse, EquipmentLoanResponse,
    IssueEquipmentRequest, ReturnEquipmentRequest, UtilisationLogRequest, UtilisationResponse,
    SchemeResponse, SchemeRuleResponse, CreateSchemeRuleRequest, ApproveSchemeRuleRequest,
    EvaluateEligibilityResponse, OpportunityResponse, ApplyOpportunityRequest, OpportunityApplicationResponse,
    TrainerCertificationResponse, CreatePlacementRequest, PlacementResponse,
    PipelineMetric, AuditLogEntry, UserResponse,
    AgentChatRequest, AgentChatResponse, CreateProposalRequest, ActionProposalResponse, ExecuteProposalRequest, PolicyCitation,
    StateManifestResponse, SyncBatchRequest, SyncBatchResponse, SyncResultItem,
    AuditChainVerificationResult, AgentKillSwitchStatus, AgentKillSwitchRequest,
    DPDPErasureResponse, ChaosDrillResult
)
from app.core.agent_service import process_agent_query, search_policy_guidelines
from app.core.sync_protocol import process_batch_sync
from app.core.security_resilience import SecurityResilienceService

api_router = APIRouter()

@api_router.get("/auth/me", response_model=UserResponse)
def get_auth_context(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.get("/auth/users", response_model=List[UserResponse])
def list_demo_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# --- REGISTRY & ONBOARDING ---

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

@api_router.post("/registry/athletes", response_model=AthleteSummary, status_code=status.HTTP_201_CREATED)
def onboard_athlete(
    req: OnboardAthleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    verify_district_scope(req.district_id, current_user)

    try:
        dob_date = datetime.date.fromisoformat(req.dob)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format for DOB, expected YYYY-MM-DD")

    age = calculate_age(dob_date)
    is_minor = age < 18

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

    if current_user.role not in ("DISTRICT_OFFICER", "STATE_OFFICER", "NATIONAL_ADMIN"):
        raise HTTPException(status_code=403, detail="Coaches cannot execute verification transitions")

    if current_user.role == "DISTRICT_OFFICER" and current_user.district_id != ath.district_id:
        raise HTTPException(status_code=403, detail="District Officers can only verify athletes within their district")

    if ath.coach_id and ath.coach_id == current_user.id:
        raise HTTPException(status_code=403, detail="Conflict of interest: You cannot verify an athlete you coach")

    current_status = ath.verification_status
    allowed_next = VALID_TRANSITIONS.get(current_status, [])

    if req.target_status not in allowed_next:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Invalid verification transition from {current_status} to {req.target_status}. Allowed next states: {allowed_next}"
        )

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

# --- PHASE 2: PIPELINE DIAGNOSIS, GAPS & FUNNELS ---

@api_router.get("/pipeline/diagnosis/heatmap", response_model=List[HeatmapCell])
def get_diagnosis_heatmap(
    state_id: Optional[str] = None,
    sport_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_state = state_id or current_user.state_id or "MH"
    
    if current_user.role == "DISTRICT_OFFICER" and current_user.state_id != target_state:
        raise HTTPException(status_code=403, detail="Cross-state aggregate access denied")

    sports_query = db.query(Sport)
    if sport_code:
        sports_query = sports_query.filter(Sport.code == sport_code)
    sports = sports_query.all()

    # Get populations in target state
    populations = db.query(Population).filter(Population.state_id == target_state).all()
    pop_map = {(p.district_id, p.age_band): p.population_count for p in populations}

    snapshots = db.query(PipelineSnapshot).filter(PipelineSnapshot.state_id == target_state).all()
    
    # Pre-calculate rates for peer-median
    rates_by_sport_band = {}
    for snap in snapshots:
        pop = pop_map.get((snap.district_id, snap.age_band), 200000)
        rate = (snap.identified_count / pop) * 100000 if pop > 0 else 0.0
        rates_by_sport_band.setdefault((snap.sport_id, snap.age_band), []).append(rate)

    cells = []
    for snap in snapshots:
        # RBAC scope check
        if current_user.role in ("DISTRICT_OFFICER", "COACH") and current_user.district_id != snap.district_id:
            continue

        sport = next((s for s in sports if s.id == snap.sport_id), None)
        if not sport:
            continue

        pop = pop_map.get((snap.district_id, snap.age_band), 200000)
        dist_rate = (snap.identified_count / pop) * 100000 if pop > 0 else 0.0
        peer_rates = rates_by_sport_band.get((snap.sport_id, snap.age_band), [dist_rate])

        gap_eval = evaluate_district_gap(dist_rate, peer_rates)

        # Small-cell suppression invariant (< 5)
        is_suppressed = snap.is_suppressed or (snap.identified_count < 5)
        count_out = None if is_suppressed else snap.identified_count
        rate_out = None if is_suppressed else round(dist_rate, 2)
        peer_median_out = None if is_suppressed else gap_eval["peer_median"]

        cells.append(HeatmapCell(
            sport_code=sport.code,
            sport_name=sport.name,
            district_id=snap.district_id,
            state_id=snap.state_id,
            age_band=snap.age_band,
            identified_count=count_out,
            rate_per_100k=rate_out,
            peer_median_rate_per_100k=peer_median_out,
            is_suppressed=is_suppressed,
            is_gap=gap_eval["is_gap"] and not is_suppressed,
            reasons=gap_eval["reasons"] if not is_suppressed else [],
            as_of=snap.as_of.isoformat()
        ))

    return cells

@api_router.get("/pipeline/funnel", response_model=FunnelResponse)
def get_conversion_funnel(
    state_id: Optional[str] = None,
    district_id: Optional[str] = None,
    sport_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    target_state = state_id or current_user.state_id or "MH"
    target_dist = district_id or (current_user.district_id if current_user.role == "DISTRICT_OFFICER" else None)

    if current_user.role == "DISTRICT_OFFICER" and current_user.district_id != target_dist:
        raise HTTPException(status_code=403, detail="Cross-district aggregate access denied")

    ath_query = db.query(Athlete).filter(Athlete.state_id == target_state)
    if target_dist:
        ath_query = ath_query.filter(Athlete.district_id == target_dist)
    if sport_code:
        sport = db.query(Sport).filter(Sport.code == sport_code).first()
        if sport:
            ath_query = ath_query.filter(Athlete.primary_sport_id == sport.id)

    athletes = ath_query.all()
    support_records = db.query(SupportRecord).all()
    achievements = db.query(Achievement).all()

    ath_dicts = [{"id": a.id, "verification_status": a.verification_status} for a in athletes]
    sr_dicts = [{"athlete_id": s.athlete_id, "status": s.status, "start_date": s.start_date} for s in support_records]
    ach_dicts = [{"athlete_id": a.athlete_id, "event_date": a.event_date} for a in achievements]

    stages = calculate_funnel_stages(ath_dicts, sr_dicts, ach_dicts)

    id_count = stages["identified"]
    ver_count = stages["verified"]
    sup_count = stages["supported"]
    prog_count = stages["progressed"]

    return FunnelResponse(
        sport_code=sport_code,
        state_id=target_state,
        district_id=target_dist,
        identified=id_count,
        verified=ver_count,
        supported=sup_count,
        progressed=prog_count,
        identified_to_verified_pct=round((ver_count / id_count * 100), 1) if id_count > 0 else 0.0,
        verified_to_supported_pct=round((sup_count / ver_count * 100), 1) if ver_count > 0 else 0.0,
        supported_to_progressed_pct=round((prog_count / sup_count * 100), 1) if sup_count > 0 else 0.0,
        as_of=datetime.datetime.utcnow().isoformat()
    )

# --- PHASE 2: EQUIPMENT INVENTORY & LOANS ---

@api_router.get("/equipment/items", response_model=List[EquipmentItemResponse])
def list_equipment_items(
    facility_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(EquipmentItem).join(Facility, EquipmentItem.facility_id == Facility.id)
    if current_user.role in ("DISTRICT_OFFICER", "COACH"):
        query = query.filter(Facility.district_id == current_user.district_id)
    if facility_id:
        query = query.filter(EquipmentItem.facility_id == facility_id)

    return [
        EquipmentItemResponse(
            id=item.id,
            facility_id=item.facility_id,
            item_name=item.item_name,
            item_type=item.item_type,
            condition=item.condition,
            qr_code=item.qr_code,
            status=item.status
        ) for item in query.all()
    ]

@api_router.get("/equipment/overdue", response_model=List[EquipmentLoanResponse])
def list_overdue_equipment_loans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    now = datetime.datetime.utcnow()
    query = db.query(EquipmentLoan, EquipmentItem, Facility).\
        join(EquipmentItem, EquipmentLoan.item_id == EquipmentItem.id).\
        join(Facility, EquipmentItem.facility_id == Facility.id).\
        filter(EquipmentLoan.due_at < now, EquipmentLoan.returned_at.is_(None))

    if current_user.role in ("DISTRICT_OFFICER", "COACH"):
        query = query.filter(Facility.district_id == current_user.district_id)

    results = []
    for loan, item, fac in query.all():
        results.append(EquipmentLoanResponse(
            id=loan.id,
            item_id=loan.item_id,
            item_name=item.item_name,
            borrower_type=loan.borrower_type,
            borrower_id=loan.borrower_id,
            issued_at=loan.issued_at.isoformat(),
            due_at=loan.due_at.isoformat(),
            returned_at=loan.returned_at.isoformat() if loan.returned_at else None,
            condition_out=loan.condition_out,
            condition_in=loan.condition_in,
            is_overdue=True
        ))
    return results

@api_router.post("/equipment/loans/issue", response_model=EquipmentLoanResponse, status_code=status.HTTP_201_CREATED)
def issue_equipment(
    req: IssueEquipmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    item = db.query(EquipmentItem).join(Facility).filter(EquipmentItem.id == req.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Equipment item not found")

    fac = db.query(Facility).filter(Facility.id == item.facility_id).first()
    verify_district_scope(fac.district_id, current_user)

    if item.status != "AVAILABLE":
        raise HTTPException(status_code=400, detail=f"Item is currently {item.status}, not AVAILABLE")

    try:
        due_datetime = datetime.datetime.fromisoformat(req.due_at)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid due_at date format")

    loan = EquipmentLoan(
        item_id=item.id,
        borrower_type=req.borrower_type,
        borrower_id=req.borrower_id,
        issued_at=datetime.datetime.utcnow(),
        due_at=due_datetime,
        condition_out=req.condition_out,
        issued_by=current_user.id
    )
    item.status = "ISSUED"
    db.add(loan)
    db.commit()
    db.refresh(loan)

    record_audit_event(
        db, current_user, "ISSUE_EQUIPMENT", "EquipmentLoan", loan.id,
        {"item_id": item.id, "qr_code": item.qr_code, "borrower": req.borrower_id}
    )

    return EquipmentLoanResponse(
        id=loan.id,
        item_id=loan.item_id,
        item_name=item.item_name,
        borrower_type=loan.borrower_type,
        borrower_id=loan.borrower_id,
        issued_at=loan.issued_at.isoformat(),
        due_at=loan.due_at.isoformat(),
        returned_at=None,
        condition_out=loan.condition_out,
        condition_in=None,
        is_overdue=False
    )

@api_router.post("/equipment/loans/{loan_id}/return", response_model=EquipmentLoanResponse)
def return_equipment(
    loan_id: str,
    req: ReturnEquipmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    loan = db.query(EquipmentLoan).filter(EquipmentLoan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Equipment loan record not found")

    item = db.query(EquipmentItem).filter(EquipmentItem.id == loan.item_id).first()
    fac = db.query(Facility).filter(Facility.id == item.facility_id).first()
    verify_district_scope(fac.district_id, current_user)

    if loan.returned_at is not None:
        raise HTTPException(status_code=400, detail="Item has already been returned")

    loan.returned_at = datetime.datetime.utcnow()
    loan.condition_in = req.condition_in
    item.condition = req.condition_in
    item.status = "AVAILABLE" if req.condition_in in ("EXCELLENT", "GOOD") else "UNDER_MAINTENANCE"
    db.commit()

    record_audit_event(
        db, current_user, "RETURN_EQUIPMENT", "EquipmentLoan", loan.id,
        {"condition_in": req.condition_in, "status": item.status}
    )

    return EquipmentLoanResponse(
        id=loan.id,
        item_id=loan.item_id,
        item_name=item.item_name,
        borrower_type=loan.borrower_type,
        borrower_id=loan.borrower_id,
        issued_at=loan.issued_at.isoformat(),
        due_at=loan.due_at.isoformat(),
        returned_at=loan.returned_at.isoformat(),
        condition_out=loan.condition_out,
        condition_in=loan.condition_in,
        is_overdue=False
    )

# Equipment loan log rejection on PUT/DELETE (Append-only)
@api_router.put("/equipment/loans/{loan_id}")
def update_equipment_loan_rejected():
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Equipment loan log is strictly append-only")

@api_router.delete("/equipment/loans/{loan_id}")
def delete_equipment_loan_rejected():
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail="Equipment loan log is strictly append-only")

# --- PHASE 2: FACILITY UTILISATION ---

@api_router.post("/facilities/{facility_id}/utilisation", response_model=UtilisationResponse, status_code=status.HTTP_201_CREATED)
def log_facility_utilisation(
    facility_id: str,
    req: UtilisationLogRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    fac = db.query(Facility).filter(Facility.id == facility_id).first()
    if not fac:
        raise HTTPException(status_code=404, detail="Facility not found")

    verify_district_scope(fac.district_id, current_user)

    try:
        period_date = datetime.date.fromisoformat(req.period)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format for period, expected YYYY-MM-DD")

    util = FacilityUtilisation(
        facility_id=fac.id,
        period=period_date,
        sessions=req.sessions,
        athlete_count=req.athlete_count,
        hours_used=req.hours_used
    )
    db.add(util)
    db.commit()
    db.refresh(util)

    rate_pct = round((req.hours_used / fac.open_hours_monthly * 100), 1)
    is_under = rate_pct < 50.0

    return UtilisationResponse(
        id=util.id,
        facility_id=util.facility_id,
        period=util.period.isoformat(),
        sessions=util.sessions,
        athlete_count=util.athlete_count,
        hours_used=util.hours_used,
        capacity_hours=fac.open_hours_monthly,
        utilisation_rate_pct=rate_pct,
        is_underutilised=is_under,
        advisory_reason=f"Utilisation is {rate_pct}%, which is below the 50% capacity benchmark." if is_under else None
    )

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
            sports=json.loads(f.sports_json) if f.sports_json else [],
            open_hours_monthly=f.open_hours_monthly
        ))
    return out

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

# --- PHASE 3: SCHEME CATALOG & MAKER-CHECKER ---

@api_router.get("/schemes", response_model=List[SchemeResponse])
def list_schemes(db: Session = Depends(get_db)):
    schemes = db.query(Scheme).all()
    out = []
    for s in schemes:
        rules = db.query(SchemeRule).filter(SchemeRule.scheme_id == s.id).all()
        out.append(SchemeResponse(
            id=s.id,
            code=s.code,
            name=s.name,
            level=s.level,
            owner_body=s.owner_body,
            is_placeholder=s.is_placeholder,
            verify_with_ministry=s.verify_with_ministry,
            rules=[
                SchemeRuleResponse(
                    id=r.id,
                    scheme_id=r.scheme_id,
                    version=r.version,
                    rule_json=r.rule_json,
                    effective_from=r.effective_from.isoformat(),
                    effective_to=r.effective_to.isoformat() if r.effective_to else None,
                    source_document=r.source_document,
                    source_page=r.source_page,
                    source_clause=r.source_clause,
                    status=r.status,
                    author_id=r.author_id,
                    approver_id=r.approver_id,
                    approved_at=r.approved_at.isoformat() if r.approved_at else None
                ) for r in rules
            ]
        ))
    return out

@api_router.post("/schemes/rules", response_model=SchemeRuleResponse, status_code=status.HTTP_201_CREATED)
def create_draft_scheme_rule(
    req: CreateSchemeRuleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ("NATIONAL_ADMIN", "STATE_OFFICER"):
        raise HTTPException(status_code=403, detail="Only State or National officers can author scheme rules")

    scheme = db.query(Scheme).filter(Scheme.id == req.scheme_id).first()
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    errors = validate_rule_json(req.rule_dict)
    if errors:
        raise HTTPException(status_code=422, detail=f"Scheme rule validation error: {errors}")

    try:
        eff_from = datetime.date.fromisoformat(req.effective_from)
        eff_to = datetime.date.fromisoformat(req.effective_to) if req.effective_to else None
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid date format, expected YYYY-MM-DD")

    rule = SchemeRule(
        scheme_id=scheme.id,
        version=req.version,
        rule_json=json.dumps(req.rule_dict),
        effective_from=eff_from,
        effective_to=eff_to,
        source_document=req.source_document,
        source_page=req.source_page,
        source_clause=req.source_clause,
        status="DRAFT",
        author_id=current_user.id
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)

    record_audit_event(
        db, current_user, "CREATE_SCHEME_RULE_DRAFT", "SchemeRule", rule.id,
        {"version": req.version, "scheme": scheme.code}
    )

    return SchemeRuleResponse(
        id=rule.id,
        scheme_id=rule.scheme_id,
        version=rule.version,
        rule_json=rule.rule_json,
        effective_from=rule.effective_from.isoformat(),
        effective_to=rule.effective_to.isoformat() if rule.effective_to else None,
        source_document=rule.source_document,
        source_page=rule.source_page,
        source_clause=rule.source_clause,
        status=rule.status,
        author_id=rule.author_id,
        approver_id=None,
        approved_at=None
    )

@api_router.post("/schemes/rules/{rule_id}/approve", response_model=SchemeRuleResponse)
def approve_scheme_rule(
    rule_id: str,
    req: ApproveSchemeRuleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rule = db.query(SchemeRule).filter(SchemeRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Scheme rule not found")

    if current_user.role not in ("NATIONAL_ADMIN", "STATE_OFFICER"):
        raise HTTPException(status_code=403, detail="Unauthorized to approve scheme rules")

    # Invariant: Maker-Checker enforcement (Approver cannot be the Author)
    if rule.author_id == current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Maker-Checker Violation: Author cannot approve their own scheme rule. Distinct approver required."
        )

    if rule.status == "APPROVED":
        raise HTTPException(status_code=409, detail="Rule is already approved and immutable")

    rule.status = "APPROVED"
    rule.approver_id = current_user.id
    rule.approved_at = datetime.datetime.utcnow()
    db.commit()

    record_audit_event(
        db, current_user, "APPROVE_SCHEME_RULE", "SchemeRule", rule.id,
        {"reason": req.approval_reason, "version": rule.version}
    )

    return SchemeRuleResponse(
        id=rule.id,
        scheme_id=rule.scheme_id,
        version=rule.version,
        rule_json=rule.rule_json,
        effective_from=rule.effective_from.isoformat(),
        effective_to=rule.effective_to.isoformat() if rule.effective_to else None,
        source_document=rule.source_document,
        source_page=rule.source_page,
        source_clause=rule.source_clause,
        status=rule.status,
        author_id=rule.author_id,
        approver_id=rule.approver_id,
        approved_at=rule.approved_at.isoformat() if rule.approved_at else None
    )

# Approved rules are immutable (Update rejected)
@api_router.put("/schemes/rules/{rule_id}")
def update_scheme_rule_rejected(rule_id: str, db: Session = Depends(get_db)):
    rule = db.query(SchemeRule).filter(SchemeRule.id == rule_id).first()
    if rule and rule.status == "APPROVED":
        raise HTTPException(status_code=409, detail="Approved scheme rules are strictly immutable. Create a new version.")
    raise HTTPException(status_code=400, detail="Draft rules must be updated through migration or new version")

# --- PHASE 3: DETERMINISTIC ELIGIBILITY EVALUATOR ---

@api_router.get("/eligibility/athlete/{athlete_id}", response_model=List[EvaluateEligibilityResponse])
def evaluate_athlete_eligibility(
    athlete_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ath = db.query(Athlete).filter(Athlete.id == athlete_id).first()
    if not ath:
        raise HTTPException(status_code=404, detail="Athlete not found")

    # Invariant: minor records invisible to unauthorized roles (return 404, not 403)
    if ath.is_minor and current_user.role in ("DISTRICT_OFFICER", "COACH") and current_user.district_id != ath.district_id:
        raise HTTPException(status_code=404, detail="Athlete record not found")

    # Build evaluation profile
    dob_str = decrypt_pii(ath.encrypted_dob)
    try:
        dob_date = datetime.date.fromisoformat(dob_str)
        age = calculate_age(dob_date)
    except Exception:
        age = 15

    achievements = db.query(Achievement).filter(Achievement.athlete_id == ath.id).all()
    ach_levels = [a.level for a in achievements]
    highest_level = "intl" if "intl" in ach_levels else ("national" if "national" in ach_levels else ("state" if "state" in ach_levels else ("district" if "district" in ach_levels else "local")))

    profile = {
        "age": age,
        "verification_status": ath.verification_status,
        "state_id": ath.state_id,
        "district_id": ath.district_id,
        "highest_achievement_level": highest_level if achievements else None
    }

    # Invariant: Evaluate ONLY status = APPROVED rules
    approved_rules = db.query(SchemeRule, Scheme).\
        join(Scheme, SchemeRule.scheme_id == Scheme.id).\
        filter(SchemeRule.status == "APPROVED").all()

    eval_results = []
    for rule, scheme in approved_rules:
        rule_dict = json.loads(rule.rule_json)
        source_ref = {
            "source_document": rule.source_document,
            "source_page": rule.source_page,
            "source_clause": rule.source_clause
        }
        res = evaluate_scheme_eligibility(profile, rule_dict, source_ref, rule.version)

        # Record append-only eligibility result
        el_record = EligibilityResult(
            athlete_id=ath.id,
            scheme_id=scheme.id,
            rule_version=rule.version,
            eligible=res["eligible"],
            reasons_json=json.dumps(res["reasons"]),
            missing_fields_json=json.dumps(res["missing_fields"]),
            source_refs_json=json.dumps(res["source_refs"]),
            evaluated_by=current_user.id
        )
        db.add(el_record)

        eval_results.append(EvaluateEligibilityResponse(
            scheme_id=scheme.id,
            scheme_name=scheme.name,
            rule_version=rule.version,
            eligible=res["eligible"],
            missing_fields=res["missing_fields"],
            reasons=res["reasons"],
            source_refs=res["source_refs"],
            evaluated_at=res["evaluated_at"]
        ))

    db.commit()
    return eval_results

# --- PHASE 3: OPPORTUNITY BOARD ---

@api_router.get("/opportunities", response_model=List[OpportunityResponse])
def list_opportunities(
    state_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Opportunity).filter(Opportunity.status == "OPEN")
    if current_user.role == "STATE_OFFICER":
        query = query.filter(Opportunity.state_scope.in_([current_user.state_id, None]))

    opportunities = query.all()
    return [
        OpportunityResponse(
            id=o.id,
            title=o.title,
            type=o.type,
            employer=o.employer,
            slots=o.slots,
            state_scope=o.state_scope,
            district_scope=o.district_scope,
            deadline=o.deadline.isoformat(),
            status=o.status
        ) for o in opportunities
    ]

@api_router.post("/opportunities/apply", response_model=OpportunityApplicationResponse, status_code=status.HTTP_201_CREATED)
def apply_opportunity(
    req: ApplyOpportunityRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    opp = db.query(Opportunity).filter(Opportunity.id == req.opportunity_id).first()
    if not opp:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    ath = db.query(Athlete).filter(Athlete.id == req.athlete_id).first()
    if not ath:
        raise HTTPException(status_code=404, detail="Athlete not found")

    verify_district_scope(ath.district_id, current_user)

    if not req.status_reason:
        raise HTTPException(status_code=422, detail="Opportunity application requires explicit status_reason")

    app_entry = OpportunityApplication(
        opportunity_id=opp.id,
        athlete_id=ath.id,
        status="SUBMITTED",
        status_reason=req.status_reason,
        updated_by=current_user.id
    )

    # Invariant: Transactional Outbox write in same transaction (zero minor PII in outbox)
    token = f"TOKEN-APP-{datetime.datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    outbox_msg = OutboxMessage(
        channel="sms",
        recipient_ref=f"ATHLETE-REF-{ath.id[:8]}",
        template_id="OPP_APPLICATION_CONFIRMATION",
        payload_json=json.dumps({"token": token, "opportunity": opp.title}),
        idempotency_key=f"IDEMP-OPP-{app_entry.id}-{datetime.datetime.utcnow().timestamp()}"
    )
    db.add_all([app_entry, outbox_msg])
    db.commit()
    db.refresh(app_entry)

    return OpportunityApplicationResponse(
        id=app_entry.id,
        opportunity_id=app_entry.opportunity_id,
        athlete_id=app_entry.athlete_id,
        status=app_entry.status,
        status_reason=app_entry.status_reason,
        created_at=app_entry.created_at.isoformat()
    )

# --- PHASE 3: TRAINER CERTIFICATION & PLACEMENTS ---

@api_router.get("/certifications/trainer/{trainer_id}", response_model=List[TrainerCertificationResponse])
def get_trainer_certifications(
    trainer_id: str,
    db: Session = Depends(get_db)
):
    certs = db.query(TrainerCertification).filter(TrainerCertification.trainer_id == trainer_id).all()
    today = datetime.date.today()
    return [
        TrainerCertificationResponse(
            id=c.id,
            trainer_id=c.trainer_id,
            course=c.course,
            provider=c.provider,
            issued_on=c.issued_on.isoformat(),
            expires_on=c.expires_on.isoformat(),
            status=c.status,
            days_to_expiry=(c.expires_on - today).days
        ) for c in certs
    ]

@api_router.post("/placements", response_model=PlacementResponse, status_code=status.HTTP_201_CREATED)
def create_placement(
    req: CreatePlacementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    trainer = db.query(Trainer).filter(Trainer.id == req.trainer_id).first()
    if not trainer:
        raise HTTPException(status_code=404, detail="Trainer not found")

    # Invariant: Revoked certification blocks placement creation
    revoked = db.query(TrainerCertification).filter(
        TrainerCertification.trainer_id == req.trainer_id,
        TrainerCertification.status == "REVOKED"
    ).first()
    if revoked:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Placement blocked: Trainer holds a REVOKED certification."
        )

    inst = db.query(Institution).filter(Institution.id == req.institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")

    placement = Placement(
        trainer_id=trainer.id,
        institution_id=inst.id,
        role=req.role,
        start_date=datetime.date.fromisoformat(req.start_date),
        end_date=datetime.date.fromisoformat(req.end_date) if req.end_date else None
    )
    db.add(placement)
    db.commit()
    db.refresh(placement)

    return PlacementResponse(
        id=placement.id,
        trainer_id=placement.trainer_id,
        institution_id=placement.institution_id,
        role=placement.role,
        start_date=placement.start_date.isoformat(),
        end_date=placement.end_date.isoformat() if placement.end_date else None
    )

# --- PHASE 4: GROUNDED AGENT & ACTION PROPOSALS ---

@api_router.post("/agent/chat", response_model=AgentChatResponse)
def agent_chat_interaction(
    req: AgentChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Processes user query with grounded policy retrieval, read-only tool calling, and action proposals."""
    try:
        res = process_agent_query(
            prompt=req.prompt,
            current_user=current_user,
            db=db,
            district_filter=req.district_filter,
            sport_filter=req.sport_filter
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return AgentChatResponse(
        response_text=res["response_text"],
        tool_calls_executed=res["tool_calls_executed"],
        citations=[PolicyCitation(**c) for c in res["citations"]],
        proposed_actions=res["proposed_actions"],
        confidence_level=res["confidence_level"],
        audit_hash=res["audit_hash"]
    )

@api_router.get("/agent/policies", response_model=List[PolicyCitation])
def search_policies(
    q: str = Query(..., description="Query terms for policy lookup"),
    db: Session = Depends(get_db)
):
    """Grounded search over approved government circulars and scheme guidelines with 100% citation enforcement."""
    results = search_policy_guidelines(q, db)
    return [PolicyCitation(**r) for r in results]

@api_router.get("/agent/proposals", response_model=List[ActionProposalResponse])
def list_action_proposals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists pending action proposals awaiting human officer sanction."""
    proposals = db.query(ActionProposal).order_by(ActionProposal.created_at.desc()).all()
    out = []
    for p in proposals:
        out.append(ActionProposalResponse(
            id=p.id,
            action_type=p.action_type,
            target_entity=p.target_entity,
            target_id=p.target_id,
            proposed_payload=json.loads(p.proposed_payload_json),
            reasoning=p.reasoning,
            citations=json.loads(p.citations_json) if isinstance(json.loads(p.citations_json), list) and len(json.loads(p.citations_json)) > 0 and isinstance(json.loads(p.citations_json)[0], dict) else [{"doc": c} for c in json.loads(p.citations_json)],
            status=p.status,
            approval_token=p.approval_token,
            created_by_agent=p.created_by_agent,
            created_at=p.created_at.isoformat(),
            executed_at=p.executed_at.isoformat() if p.executed_at else None
        ))
    return out

@api_router.post("/agent/proposals/{proposal_id}/execute", response_model=ActionProposalResponse)
def execute_action_proposal(
    proposal_id: str,
    req: ExecuteProposalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes a previously generated ActionProposal. Requires explicit human officer invocation & valid token."""
    prop = db.query(ActionProposal).filter(ActionProposal.id == proposal_id).first()
    if not prop:
        raise HTTPException(status_code=404, detail="Action proposal not found")

    if prop.status == "EXECUTED":
        raise HTTPException(status_code=409, detail="Action proposal has already been executed (replay protection)")

    if prop.approval_token != req.approval_token:
        raise HTTPException(status_code=403, detail="Invalid approval token for proposal execution")

    # Invariant: Human officer sanction
    if current_user.role not in ("NATIONAL_ADMIN", "STATE_OFFICER", "DISTRICT_OFFICER"):
        raise HTTPException(status_code=403, detail="Role unauthorized to execute action proposals")

    # Execute action mutation
    prop.status = "EXECUTED"
    prop.approved_by = current_user.id
    prop.executed_at = datetime.datetime.utcnow()
    db.commit()

    record_audit_event(
        db, current_user, "EXECUTE_ACTION_PROPOSAL", "ActionProposal", prop.id,
        {"action_type": prop.action_type, "target_entity": prop.target_entity, "notes": req.approval_notes}
    )

    return ActionProposalResponse(
        id=prop.id,
        action_type=prop.action_type,
        target_entity=prop.target_entity,
        target_id=prop.target_id,
        proposed_payload=json.loads(prop.proposed_payload_json),
        reasoning=prop.reasoning,
        citations=json.loads(prop.citations_json) if isinstance(json.loads(prop.citations_json), list) and len(json.loads(prop.citations_json)) > 0 and isinstance(json.loads(prop.citations_json)[0], dict) else [{"doc": c} for c in json.loads(prop.citations_json)],
        status=prop.status,
        approval_token=prop.approval_token,
        created_by_agent=prop.created_by_agent,
        created_at=prop.created_at.isoformat(),
        executed_at=prop.executed_at.isoformat()
    )

# --- PHASE 5: STATE ADAPTERS & OFFLINE SYNC PROTOCOL ---

@api_router.get("/adapters/states/{state_id}", response_model=StateManifestResponse)
def get_state_adapter_manifest(state_id: str, db: Session = Depends(get_db)):
    """Retrieves the active, versioned state adapter manifest. Adapters cannot alter core schemas."""
    manifest = db.query(StateAdapterManifest).filter(
        StateAdapterManifest.state_id == state_id.upper(),
        StateAdapterManifest.is_active == True
    ).first()
    if not manifest:
        raise HTTPException(status_code=404, detail=f"No active adapter found for state: {state_id}")

    return StateManifestResponse(
        id=manifest.id,
        state_id=manifest.state_id,
        state_name=manifest.state_name,
        version=manifest.version,
        primary_language=manifest.primary_language,
        supported_languages=json.loads(manifest.supported_languages_json),
        priority_sports=json.loads(manifest.priority_sports_json),
        state_policies=json.loads(manifest.state_policies_json),
        is_active=manifest.is_active
    )

@api_router.post("/sync/batch", response_model=SyncBatchResponse)
def sync_offline_actions(
    req: SyncBatchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Processes a batch of offline client actions under the conflict resolution matrix.
    Server wins on verification/status fields; last-write-wins on contact fields.
    """
    raw_actions = [a.dict() for a in req.actions]
    sync_result = process_batch_sync(raw_actions, current_user, db)

    record_audit_event(
        db, current_user, "OFFLINE_BATCH_SYNC", "SyncProtocol", current_user.id,
        {"batch_size": len(raw_actions), "applied": sync_result["applied_count"], "conflicts": sync_result["conflict_count"]}
    )

    return SyncBatchResponse(
        total_received=sync_result["total_received"],
        applied_count=sync_result["applied_count"],
        conflict_count=sync_result["conflict_count"],
        results=[SyncResultItem(**r) for r in sync_result["results"]]
    )

@api_router.get("/sync/records", response_model=List[Dict[str, Any]])
def list_sync_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lists recent offline sync entries and conflict resolutions."""
    records = db.query(OfflineSyncRecord).order_by(OfflineSyncRecord.server_timestamp.desc()).limit(50).all()
    return [{
        "id": r.id,
        "client_sync_id": r.client_sync_id,
        "entity_name": r.entity_name,
        "entity_id": r.entity_id,
        "status": r.status,
        "conflict_notes": r.conflict_notes,
        "server_timestamp": r.server_timestamp.isoformat()
    } for r in records]

# --- PHASE 6: SECURITY, ASVS L2 & RESILIENCE ENDPOINTS ---

@api_router.get("/security/audit-chain/verify", response_model=AuditChainVerificationResult)
def verify_audit_log_hash_chain(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cryptographically verifies the immutable SHA-256 hash chain of all system audit logs."""
    res = SecurityResilienceService.verify_audit_hash_chain(db)
    return AuditChainVerificationResult(**res)

@api_router.get("/security/killswitch", response_model=AgentKillSwitchStatus)
def get_killswitch_status(
    current_user: User = Depends(get_current_user)
):
    """Returns current security kill-switch state for AI Agent operations."""
    return SecurityResilienceService.get_killswitch_status()

@api_router.post("/security/killswitch", response_model=AgentKillSwitchStatus)
def update_killswitch(
    req: AgentKillSwitchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Emergency kill-switch toggling: blocks agent queries globally or per-state.
    Only NATIONAL_ADMIN or STATE_OFFICER can activate.
    """
    if current_user.role not in ("NATIONAL_ADMIN", "STATE_OFFICER"):
        raise HTTPException(status_code=403, detail="Security officer privilege required to toggle agent kill-switch.")

    updated = SecurityResilienceService.set_killswitch(
        disabled=req.disabled,
        state_id=req.state_id,
        reason=req.reason or "Security officer intervention",
        actor_id=current_user.username
    )

    record_audit_event(
        db, current_user, "AGENT_KILLSWITCH_TOGGLE", "AgentSecurity",
        req.state_id or "GLOBAL",
        {"disabled": req.disabled, "reason": req.reason}
    )

    return AgentKillSwitchStatus(**updated)

@api_router.post("/security/dpdp/erasure/{athlete_id}", response_model=DPDPErasureResponse)
def execute_dpdp_erasure(
    athlete_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Statutory DPDP Act 2023 Right-to-be-Forgotten / Data Erasure.
    Redacts encrypted PII, revokes consent, updates status to DELETED, and logs immutable audit entry.
    """
    if current_user.role not in ("NATIONAL_ADMIN", "STATE_OFFICER", "DISTRICT_OFFICER"):
        raise HTTPException(status_code=403, detail="Statutory officer authorization required for data erasure.")

    res = SecurityResilienceService.execute_dpdp_erasure(db, athlete_id, current_user)
    if res["status"] == "NOT_FOUND":
        raise HTTPException(status_code=404, detail="Athlete record not found")

    record_audit_event(
        db, current_user, "DPDP_DATA_ERASURE", "Athlete", athlete_id,
        {"redacted_fields": res["redacted_fields"]}
    )

    last_log = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).first()
    audit_hash = last_log.record_hash or last_log.payload_hash if last_log else "GENESIS"

    return DPDPErasureResponse(
        athlete_id=athlete_id,
        status="ERASED",
        redacted_fields=res["redacted_fields"],
        audit_hash=audit_hash,
        message=res["message"]
    )

@api_router.post("/security/chaos-drill", response_model=ChaosDrillResult)
def execute_chaos_resilience_drill(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Executes automated non-destructive disaster recovery and resilience checks."""
    if current_user.role not in ("NATIONAL_ADMIN", "STATE_OFFICER"):
        raise HTTPException(status_code=403, detail="High-privilege administrator required for chaos drill.")

    drill_res = SecurityResilienceService.run_chaos_resilience_drill(db)
    record_audit_event(
        db, current_user, "CHAOS_DRILL_EXECUTION", "SystemResilience",
        drill_res["drill_id"],
        {"passed": drill_res["passed"], "status": drill_res["status"]}
    )
    return ChaosDrillResult(**drill_res)


