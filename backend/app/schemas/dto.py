from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class UserResponse(BaseModel):
    username: str
    role: str
    state_id: Optional[str]
    district_id: Optional[str]
    full_name: str

    class Config:
        from_attributes = True

class AthleteSummary(BaseModel):
    id: str
    kid: Optional[str]
    name: str
    gender: str
    state_id: str
    district_id: str
    sport_name: str
    age_band: str
    consent_status: str
    verification_status: str
    is_minor: bool
    is_synthetic: bool

class AchievementResponse(BaseModel):
    id: str
    event: str
    level: str
    result: str
    event_date: str

class JourneyEventResponse(BaseModel):
    id: str
    event_type: str
    event_date: str
    notes: Optional[str]
    created_at: str

class AthleteDetail(AthleteSummary):
    achievements: List[AchievementResponse] = []
    journey_events: List[JourneyEventResponse] = []

class OnboardAthleteRequest(BaseModel):
    name: str
    dob: str  # YYYY-MM-DD
    gender: str
    state_id: str
    district_id: str
    sport_code: str
    guardian_ref: Optional[str] = None
    consent_status: Optional[str] = None  # Mandatory if minor

class CheckDuplicateRequest(BaseModel):
    name: str
    dob: str
    district_id: str

class DuplicateCandidate(BaseModel):
    athlete_id: str
    kid: Optional[str]
    name: str
    confidence_score: float
    name_similarity: float
    dob_match: str
    district_match: bool
    match_fields: List[str]

class DuplicateCheckResponse(BaseModel):
    is_duplicate_candidate: bool
    candidates: List[DuplicateCandidate]
    auto_merged: bool = False
    message: str

class VerificationTransitionRequest(BaseModel):
    target_status: str  # VERIFIED, REJECTED, NEEDS_INFO, UNDER_REVIEW
    reason: str

class JourneyEventCreateRequest(BaseModel):
    event_type: str
    event_date: str
    notes: Optional[str] = None

class FacilityResponse(BaseModel):
    id: str
    name: str
    type: str
    district_id: str
    latitude: float
    longitude: float
    sports: List[str]

class PipelineMetric(BaseModel):
    district_id: str
    state_id: str
    sport_code: str
    sport_name: str
    age_band: str
    identified_count: Optional[int]
    verified_count: Optional[int]
    supported_count: Optional[int]
    progressed_count: Optional[int]
    is_suppressed: bool
    as_of: str

class AuditLogEntry(BaseModel):
    timestamp: str
    actor_id: str
    actor_role: str
    action: str
    target_entity: str
    target_id: str
    payload_hash: str
    prev_hash: Optional[str]
