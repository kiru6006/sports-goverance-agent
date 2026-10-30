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
    dob: str
    gender: str
    state_id: str
    district_id: str
    sport_code: str
    guardian_ref: Optional[str] = None
    consent_status: Optional[str] = None

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
    target_status: str
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
    open_hours_monthly: float = 300.0

class HeatmapCell(BaseModel):
    sport_code: str
    sport_name: str
    district_id: str
    state_id: str
    age_band: str
    identified_count: Optional[int]
    rate_per_100k: Optional[float]
    peer_median_rate_per_100k: Optional[float]
    is_suppressed: bool
    is_gap: bool
    reasons: List[Dict[str, Any]] = []
    as_of: str

class FunnelResponse(BaseModel):
    sport_code: Optional[str]
    state_id: str
    district_id: Optional[str]
    identified: int
    verified: int
    supported: int
    progressed: int
    identified_to_verified_pct: float
    verified_to_supported_pct: float
    supported_to_progressed_pct: float
    as_of: str

class EquipmentItemResponse(BaseModel):
    id: str
    facility_id: str
    item_name: str
    item_type: str
    condition: str
    qr_code: str
    status: str

class EquipmentLoanResponse(BaseModel):
    id: str
    item_id: str
    item_name: str
    borrower_type: str
    borrower_id: str
    issued_at: str
    due_at: str
    returned_at: Optional[str]
    condition_out: str
    condition_in: Optional[str]
    is_overdue: bool

class IssueEquipmentRequest(BaseModel):
    item_id: str
    borrower_type: str
    borrower_id: str
    due_at: str
    condition_out: str = "GOOD"

class ReturnEquipmentRequest(BaseModel):
    condition_in: str

class UtilisationLogRequest(BaseModel):
    period: str
    sessions: int
    athlete_count: int
    hours_used: float

class UtilisationResponse(BaseModel):
    id: str
    facility_id: str
    period: str
    sessions: int
    athlete_count: int
    hours_used: float
    capacity_hours: float
    utilisation_rate_pct: float
    is_underutilised: bool
    advisory_reason: Optional[str]

# --- PHASE 3 DTOs ---

class SchemeRuleResponse(BaseModel):
    id: str
    scheme_id: str
    version: str
    rule_json: str
    effective_from: str
    effective_to: Optional[str]
    source_document: str
    source_page: str
    source_clause: str
    status: str
    author_id: str
    approver_id: Optional[str]
    approved_at: Optional[str]

class SchemeResponse(BaseModel):
    id: str
    code: str
    name: str
    level: str
    owner_body: str
    is_placeholder: bool
    verify_with_ministry: bool
    rules: List[SchemeRuleResponse] = []

class CreateSchemeRuleRequest(BaseModel):
    scheme_id: str
    version: str
    rule_dict: Dict[str, Any]
    effective_from: str  # YYYY-MM-DD
    effective_to: Optional[str] = None
    source_document: str
    source_page: str
    source_clause: str

class ApproveSchemeRuleRequest(BaseModel):
    rule_id: str
    approval_reason: str

class EvaluateEligibilityResponse(BaseModel):
    scheme_id: str
    scheme_name: str
    rule_version: str
    eligible: Optional[bool]
    missing_fields: List[str]
    reasons: List[Dict[str, Any]]
    source_refs: List[Dict[str, str]]
    evaluated_at: str

class OpportunityResponse(BaseModel):
    id: str
    title: str
    type: str
    employer: str
    slots: int
    state_scope: Optional[str]
    district_scope: Optional[str]
    deadline: str
    status: str
    is_eligible: Optional[bool] = None

class ApplyOpportunityRequest(BaseModel):
    opportunity_id: str
    athlete_id: str
    status_reason: str

class OpportunityApplicationResponse(BaseModel):
    id: str
    opportunity_id: str
    athlete_id: str
    status: str
    status_reason: str
    created_at: str

class TrainerCertificationResponse(BaseModel):
    id: str
    trainer_id: str
    course: str
    provider: str
    issued_on: str
    expires_on: str
    status: str
    days_to_expiry: int

class CreatePlacementRequest(BaseModel):
    trainer_id: str
    institution_id: str
    role: str
    start_date: str
    end_date: Optional[str] = None

class PlacementResponse(BaseModel):
    id: str
    trainer_id: str
    institution_id: str
    role: str
    start_date: str
    end_date: Optional[str]

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

# --- PHASE 4 DTOs ---

class PolicyCitation(BaseModel):
    source_document: str
    source_page: str
    source_clause: str
    title: str
    relevance_score: float

class AgentChatRequest(BaseModel):
    prompt: str
    district_filter: Optional[str] = None
    sport_filter: Optional[str] = None

class AgentChatResponse(BaseModel):
    response_text: str
    tool_calls_executed: List[Dict[str, Any]]
    citations: List[PolicyCitation]
    proposed_actions: List[Dict[str, Any]] = []
    confidence_level: str
    audit_hash: str

class CreateProposalRequest(BaseModel):
    action_type: str
    target_entity: str
    target_id: str
    proposed_payload: Dict[str, Any]
    reasoning: str
    citations: List[Dict[str, str]]

class ActionProposalResponse(BaseModel):
    id: str
    action_type: str
    target_entity: str
    target_id: str
    proposed_payload: Dict[str, Any]
    reasoning: str
    citations: List[Dict[str, str]]
    status: str
    approval_token: str
    created_by_agent: str
    created_at: str
    executed_at: Optional[str]

class ExecuteProposalRequest(BaseModel):
    approval_token: str
    approval_notes: str

# --- PHASE 5 DTOs ---

class StateManifestResponse(BaseModel):
    id: str
    state_id: str
    state_name: str
    version: str
    primary_language: str
    supported_languages: List[str]
    priority_sports: List[str]
    state_policies: List[Dict[str, Any]]
    is_active: bool

class OfflineActionItem(BaseModel):
    client_sync_id: str
    entity_name: str
    entity_id: str
    action_type: str  # UPDATE, CREATE
    client_timestamp: str
    payload: Dict[str, Any]

class SyncBatchRequest(BaseModel):
    actions: List[OfflineActionItem]

class SyncResultItem(BaseModel):
    client_sync_id: str
    status: str  # APPLIED, CONFLICT_SERVER_WON, REJECTED
    conflict_notes: Optional[str] = None
    applied_fields: List[str] = []

class SyncBatchResponse(BaseModel):
    total_received: int
    applied_count: int
    conflict_count: int
    results: List[SyncResultItem]
