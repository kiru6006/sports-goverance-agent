import datetime
import uuid
from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Float, ForeignKey, Text, Date
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    state_id = Column(String, nullable=True)
    district_id = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    services_offered_json = Column(Text, nullable=True)
    services_needed_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Sport(Base):
    __tablename__ = "sports"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    is_olympic = Column(Boolean, default=True)
    is_national = Column(Boolean, default=True)
    federation = Column(String, nullable=True)

class Athlete(Base):
    __tablename__ = "athletes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kid = Column(String, index=True, nullable=True)
    encrypted_name = Column(String, nullable=False)
    encrypted_dob = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    state_id = Column(String, index=True, nullable=False)
    district_id = Column(String, index=True, nullable=False)
    primary_sport_id = Column(String, ForeignKey("sports.id"), nullable=False)
    encrypted_guardian = Column(String, nullable=True)
    consent_status = Column(String, nullable=False, default="PENDING")
    verification_status = Column(String, nullable=False, default="SUBMITTED")
    verifier_id = Column(String, ForeignKey("users.id"), nullable=True)
    coach_id = Column(String, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    rejection_report = Column(Text, nullable=True)
    rejected_by = Column(String, ForeignKey("users.id"), nullable=True)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    support_demands_json = Column(Text, nullable=True)
    services_offered_json = Column(Text, nullable=True)
    services_needed_json = Column(Text, nullable=True)
    specialist_contact_ref = Column(String, nullable=True)
    is_minor = Column(Boolean, default=False)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    achievements = relationship("Achievement", back_populates="athlete", cascade="all, delete-orphan")
    journey_events = relationship("JourneyEvent", back_populates="athlete", cascade="all, delete-orphan")
    affiliations = relationship("Affiliation", back_populates="athlete", cascade="all, delete-orphan")
    support_records = relationship("SupportRecord", back_populates="athlete", cascade="all, delete-orphan")

# --- PHASE 3 ENTITIES ---

class Scheme(Base):
    __tablename__ = "schemes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    level = Column(String, nullable=False)  # central, state
    owner_body = Column(String, nullable=False)  # SAI, State Sports Directorate
    is_placeholder = Column(Boolean, default=True)
    verify_with_ministry = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    rules = relationship("SchemeRule", back_populates="scheme")

class SchemeRule(Base):
    __tablename__ = "scheme_rules"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    scheme_id = Column(String, ForeignKey("schemes.id"), nullable=False)
    version = Column(String, nullable=False)
    rule_json = Column(Text, nullable=False)  # JSON Schema validated
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    source_document = Column(String, nullable=False)
    source_page = Column(String, nullable=False)
    source_clause = Column(String, nullable=False)
    status = Column(String, default="DRAFT")  # DRAFT, SUBMITTED_FOR_APPROVAL, APPROVED, RETIRED
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    approver_id = Column(String, ForeignKey("users.id"), nullable=True)  # Must != author_id
    approved_at = Column(DateTime, nullable=True)

    scheme = relationship("Scheme", back_populates="rules")

class EligibilityResult(Base):
    __tablename__ = "eligibility_results"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    scheme_id = Column(String, ForeignKey("schemes.id"), nullable=False)
    rule_version = Column(String, nullable=False)
    eligible = Column(Boolean, nullable=True)  # True, False, or None (if missing fields)
    reasons_json = Column(Text, nullable=False)
    missing_fields_json = Column(Text, nullable=False)
    source_refs_json = Column(Text, nullable=False)
    evaluated_at = Column(DateTime, default=datetime.datetime.utcnow)
    evaluated_by = Column(String, ForeignKey("users.id"), nullable=False)

class Opportunity(Base):
    __tablename__ = "opportunities"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    type = Column(String, nullable=False)  # job, sponsorship, quota
    employer = Column(String, nullable=False)  # Indian Railways, Armed Forces, PSU
    eligibility_rule_id = Column(String, ForeignKey("scheme_rules.id"), nullable=True)
    slots = Column(Integer, nullable=False)
    district_scope = Column(String, nullable=True)
    state_scope = Column(String, nullable=True)
    deadline = Column(Date, nullable=False)
    status = Column(String, default="OPEN")  # OPEN, CLOSED

class OpportunityApplication(Base):
    __tablename__ = "opportunity_applications"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    opportunity_id = Column(String, ForeignKey("opportunities.id"), nullable=False)
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    status = Column(String, default="SUBMITTED")  # SUBMITTED, SHORTLISTED, REJECTED, WITHDRAWN, OFFERED, ACCEPTED
    status_reason = Column(Text, nullable=False)
    updated_by = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TrainerCertification(Base):
    __tablename__ = "trainer_certifications"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trainer_id = Column(String, ForeignKey("trainers.id"), nullable=False)
    course = Column(String, nullable=False)
    provider = Column(String, nullable=False)  # SAI, National Federation
    issued_on = Column(Date, nullable=False)
    expires_on = Column(Date, nullable=False)
    status = Column(String, default="ACTIVE")  # ACTIVE, EXPIRED, REVOKED

class Placement(Base):
    __tablename__ = "placements"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    trainer_id = Column(String, ForeignKey("trainers.id"), nullable=False)
    institution_id = Column(String, ForeignKey("institutions.id"), nullable=False)
    role = Column(String, default="HEAD_COACH")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)

class OutboxMessage(Base):
    __tablename__ = "outbox_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    channel = Column(String, nullable=False)  # email, sms
    recipient_ref = Column(String, nullable=False)
    template_id = Column(String, nullable=False)
    payload_json = Column(Text, nullable=False)  # No minor identifiers! Token only
    status = Column(String, default="PENDING")  # PENDING, DELIVERED, DEAD_LETTER
    idempotency_key = Column(String, unique=True, index=True, nullable=False)
    attempts = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# --- PHASE 4 ENTITIES ---

class PolicyChunk(Base):
    __tablename__ = "policy_chunks"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    source_document = Column(String, nullable=False)   # e.g., MYAS Khelo India Operational Guidelines 2024
    source_page = Column(String, nullable=False)       # e.g., Page 28
    source_clause = Column(String, nullable=False)     # e.g., Clause 4.2
    title = Column(String, nullable=False)
    text_content = Column(Text, nullable=False)
    keywords_json = Column(Text, nullable=False)      # Keywords/terms for lexical + semantic retrieval
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class ActionProposal(Base):
    __tablename__ = "action_proposals"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    action_type = Column(String, nullable=False)       # VERIFY_ATHLETE, ISSUE_EQUIPMENT, APPLY_OPPORTUNITY
    target_entity = Column(String, nullable=False)     # Athlete, EquipmentLoan, OpportunityApplication
    target_id = Column(String, nullable=False)
    proposed_payload_json = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=False)
    citations_json = Column(Text, nullable=False)
    status = Column(String, default="PENDING_APPROVAL") # PENDING_APPROVAL, APPROVED, REJECTED, EXECUTED
    approval_token = Column(String, unique=True, index=True, nullable=False)
    created_by_agent = Column(String, default="TrackNet-Assistant-v1")
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# --- PHASE 5 ENTITIES ---

class StateAdapterManifest(Base):
    __tablename__ = "state_adapter_manifests"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id = Column(String, unique=True, index=True, nullable=False)
    state_name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    primary_language = Column(String, default="hi")
    supported_languages_json = Column(Text, nullable=False)
    priority_sports_json = Column(Text, nullable=False)
    state_policies_json = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow)

class OfflineSyncRecord(Base):
    __tablename__ = "offline_sync_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    client_sync_id = Column(String, unique=True, index=True, nullable=False)
    entity_name = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    client_timestamp = Column(DateTime, nullable=False)
    server_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    payload_json = Column(Text, nullable=False)
    status = Column(String, default="APPLIED")  # APPLIED, CONFLICT_SERVER_WON, REJECTED
    conflict_notes = Column(Text, nullable=True)
    submitted_by = Column(String, ForeignKey("users.id"), nullable=False)

# Existing Phase 1 & 2 Entities
class Population(Base):
    __tablename__ = "population"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id = Column(String, index=True, nullable=False)
    district_id = Column(String, index=True, nullable=False)
    age_band = Column(String, nullable=False)
    gender = Column(String, nullable=False)
    population_count = Column(Integer, nullable=False)
    source = Column(String, default="Synthetic Census Estimate")
    is_synthetic = Column(Boolean, default=True)

class SupportRecord(Base):
    __tablename__ = "support_records"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    support_type = Column(String, nullable=False)
    status = Column(String, nullable=False, default="ACTIVE")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)
    athlete = relationship("Athlete", back_populates="support_records")

class EquipmentItem(Base):
    __tablename__ = "equipment_items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    facility_id = Column(String, ForeignKey("facilities.id"), nullable=False)
    item_name = Column(String, nullable=False)
    item_type = Column(String, nullable=False)
    condition = Column(String, nullable=False, default="GOOD")
    qr_code = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="AVAILABLE")
    loans = relationship("EquipmentLoan", back_populates="item")

class EquipmentLoan(Base):
    __tablename__ = "equipment_loans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String, ForeignKey("equipment_items.id"), nullable=False)
    borrower_type = Column(String, nullable=False)
    borrower_id = Column(String, nullable=False)
    issued_at = Column(DateTime, default=datetime.datetime.utcnow)
    due_at = Column(DateTime, nullable=False)
    returned_at = Column(DateTime, nullable=True)
    condition_out = Column(String, nullable=False)
    condition_in = Column(String, nullable=True)
    issued_by = Column(String, ForeignKey("users.id"), nullable=False)
    item = relationship("EquipmentItem", back_populates="loans")

class Facility(Base):
    __tablename__ = "facilities"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    state_id = Column(String, nullable=False)
    district_id = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    sports_json = Column(Text, nullable=False)
    open_hours_monthly = Column(Float, default=300.0)
    is_synthetic = Column(Boolean, default=True)
    utilisations = relationship("FacilityUtilisation", back_populates="facility")

class FacilityUtilisation(Base):
    __tablename__ = "facility_utilisation"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    facility_id = Column(String, ForeignKey("facilities.id"), nullable=False)
    period = Column(Date, nullable=False)
    sessions = Column(Integer, default=0)
    athlete_count = Column(Integer, default=0)
    hours_used = Column(Float, default=0.0)
    facility = relationship("Facility", back_populates="utilisations")

class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    encrypted_name = Column(String, nullable=False)
    state_id = Column(String, nullable=False)
    district_id = Column(String, nullable=False)
    sports_json = Column(Text, nullable=False)
    certifications_json = Column(Text, nullable=False)
    contact_phone = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    specialization = Column(String, nullable=True)
    services_offered_json = Column(Text, nullable=True)
    services_needed_json = Column(Text, nullable=True)
    verification_status = Column(String, default="VERIFIED")
    is_synthetic = Column(Boolean, default=True)

class Institution(Base):
    __tablename__ = "institutions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    state_id = Column(String, nullable=False)
    district_id = Column(String, nullable=False)
    sports_facilities_json = Column(Text, nullable=True)
    is_synthetic = Column(Boolean, default=True)

class Affiliation(Base):
    __tablename__ = "affiliations"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    trainer_id = Column(String, ForeignKey("trainers.id"), nullable=True)
    institution_id = Column(String, ForeignKey("institutions.id"), nullable=True)
    role = Column(String, default="STUDENT_ATHLETE")
    valid_from = Column(Date, nullable=False)
    valid_to = Column(Date, nullable=True)
    athlete = relationship("Athlete", back_populates="affiliations")

class Achievement(Base):
    __tablename__ = "achievements"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    sport_id = Column(String, ForeignKey("sports.id"), nullable=False)
    event = Column(String, nullable=False)
    level = Column(String, nullable=False)
    result = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    athlete = relationship("Athlete", back_populates="achievements")

class JourneyEvent(Base):
    __tablename__ = "journey_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    event_type = Column(String, nullable=False)
    event_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    athlete = relationship("Athlete", back_populates="journey_events")

class PipelineSnapshot(Base):
    __tablename__ = "pipeline_snapshots"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id = Column(String, index=True, nullable=False)
    district_id = Column(String, index=True, nullable=False)
    sport_id = Column(String, ForeignKey("sports.id"), nullable=False)
    age_band = Column(String, nullable=False)
    identified_count = Column(Integer, default=0)
    verified_count = Column(Integer, default=0)
    supported_count = Column(Integer, default=0)
    progressed_count = Column(Integer, default=0)
    is_suppressed = Column(Boolean, default=False)
    as_of = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    actor_id = Column(String, nullable=False)
    actor_role = Column(String, nullable=False)
    actor_district = Column(String, nullable=True)
    action = Column(String, nullable=False)
    target_entity = Column(String, nullable=False)
    target_id = Column(String, nullable=False)
    payload_hash = Column(String, nullable=False)
    prev_hash = Column(String, nullable=True)
    record_hash = Column(String, nullable=True)

class DirectMessage(Base):
    __tablename__ = "direct_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    sender_id = Column(String, nullable=False)        # username or athlete_id
    sender_name = Column(String, nullable=False)
    sender_role = Column(String, nullable=False)      # ATHLETE, COACH, TRAINER, DISTRICT_OFFICER, etc.
    recipient_id = Column(String, nullable=False)     # username or athlete_id
    recipient_name = Column(String, nullable=False)
    recipient_role = Column(String, nullable=False)
    athlete_context_id = Column(String, nullable=True) # if conversation is about a specific athlete
    message_text = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_read = Column(Boolean, default=False)

