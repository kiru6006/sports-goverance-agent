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
    coach_id = Column(String, ForeignKey("users.id"), nullable=True)  # Primary assigned coach
    verification_notes = Column(Text, nullable=True)
    verified_at = Column(DateTime, nullable=True)
    is_minor = Column(Boolean, default=False)
    is_synthetic = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    achievements = relationship("Achievement", back_populates="athlete", cascade="all, delete-orphan")
    journey_events = relationship("JourneyEvent", back_populates="athlete", cascade="all, delete-orphan")
    affiliations = relationship("Affiliation", back_populates="athlete", cascade="all, delete-orphan")

class Trainer(Base):
    __tablename__ = "trainers"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    encrypted_name = Column(String, nullable=False)
    state_id = Column(String, nullable=False)
    district_id = Column(String, nullable=False)
    sports_json = Column(Text, nullable=False)  # list of sport IDs
    certifications_json = Column(Text, nullable=False)  # list of certifications
    verification_status = Column(String, default="VERIFIED")
    is_synthetic = Column(Boolean, default=True)

class Institution(Base):
    __tablename__ = "institutions"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # school, college, academy, club
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
    result = Column(String, nullable=False)  # Gold, Silver, Bronze, Participant
    event_date = Column(Date, nullable=False)

    athlete = relationship("Athlete", back_populates="achievements")

class JourneyEvent(Base):
    __tablename__ = "journey_events"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    athlete_id = Column(String, ForeignKey("athletes.id"), nullable=False)
    event_type = Column(String, nullable=False)  # injury, break, transition, competition, training_start
    event_date = Column(Date, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)  # Append-only

    athlete = relationship("Athlete", back_populates="journey_events")

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
    is_synthetic = Column(Boolean, default=True)

class PipelineSnapshot(Base):
    __tablename__ = "pipeline_snapshots"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    state_id = Column(String, index=True, nullable=False)
    district_id = Column(String, index=True, nullable=False)
    sport_id = Column(String, ForeignKey("sports.id"), nullable=False)
    age_band = Column(String, nullable=False)  # U-10, U-14, U-17, U-19, Senior
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
