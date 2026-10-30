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
    role = Column(String, nullable=False)  # NATIONAL_ADMIN, STATE_OFFICER, DISTRICT_OFFICER, COACH
    state_id = Column(String, nullable=True)
    district_id = Column(String, nullable=True)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Sport(Base):
    __tablename__ = "sports"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)  # INDIVIDUAL, TEAM
    is_olympic = Column(Boolean, default=True)
    is_national = Column(Boolean, default=True)
    federation = Column(String, nullable=True)

class Athlete(Base):
    __tablename__ = "athletes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    kid = Column(String, index=True, nullable=True)
    encrypted_name = Column(String, nullable=False)
    encrypted_dob = Column(String, nullable=False)  # Stored encrypted, age band derived
    gender = Column(String, nullable=False)
    state_id = Column(String, index=True, nullable=False)
    district_id = Column(String, index=True, nullable=False)
    primary_sport_id = Column(String, ForeignKey("sports.id"), nullable=False)
    encrypted_guardian = Column(String, nullable=True)
    consent_status = Column(String, nullable=False, default="PENDING")  # PENDING, GRANTED, REVOKED
    verification_status = Column(String, nullable=False, default="SUBMITTED")  # SUBMITTED, UNDER_REVIEW, VERIFIED, REJECTED, NEEDS_INFO
    verifier_id = Column(String, ForeignKey("users.id"), nullable=True)
    coach_id = Column(String, ForeignKey("users.id"), nullable=True)
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    is_minor = Column(Boolean, default=False)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    achievements = relationship("Achievement", back_populates="athlete", cascade="all, delete-orphan")
    journey_events = relationship("JourneyEvent", back_populates="athlete", cascade="all, delete-orphan")
    affiliations = relationship("Affiliation", back_populates="athlete", cascade="all, delete-orphan")
    support_records = relationship("SupportRecord", back_populates="athlete", cascade="all, delete-orphan")

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
    support_type = Column(String, nullable=False)  # equipment, nutrition, training_grant, coaching, facility_access
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE, COMPLETED, TERMINATED
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    notes = Column(Text, nullable=True)

    athlete = relationship("Athlete", back_populates="support_records")

class EquipmentItem(Base):
    __tablename__ = "equipment_items"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    facility_id = Column(String, ForeignKey("facilities.id"), nullable=False)
    item_name = Column(String, nullable=False)
    item_type = Column(String, nullable=False)  # GLOVES, MAT, RING, SHOES, WEIGHTS
    condition = Column(String, nullable=False, default="GOOD")  # EXCELLENT, GOOD, WORN, DAMAGED
    qr_code = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="AVAILABLE")  # AVAILABLE, ISSUED, UNDER_MAINTENANCE

    loans = relationship("EquipmentLoan", back_populates="item")

class EquipmentLoan(Base):
    __tablename__ = "equipment_loans"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    item_id = Column(String, ForeignKey("equipment_items.id"), nullable=False)
    borrower_type = Column(String, nullable=False)  # ATHLETE, TRAINER, INSTITUTION
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
    type = Column(String, nullable=False)  # STADIUM, COMPLEX, GROUND, GYM
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
    period = Column(Date, nullable=False)  # First of month (YYYY-MM-01)
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
    level = Column(String, nullable=False)  # local, district, state, national, intl
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
