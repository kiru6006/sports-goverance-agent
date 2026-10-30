from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.entities import Base, User, Sport, Athlete, PipelineSnapshot, AuditLog
from app.core.crypto import encrypt_pii

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check and add record_hash column to audit_logs if missing in SQLite
    try:
        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE audit_logs ADD COLUMN record_hash VARCHAR;"))
            conn.commit()
    except Exception:
        pass

    # Ensure all audit logs have an unbroken cryptographic chain
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.asc()).all()
    if logs:
        import hashlib
        current_prev = "GENESIS_HASH_0000000000000000"
        for entry in logs:
            entry.prev_hash = current_prev
            record_content = f"{current_prev}:{entry.actor_id}:{entry.action}:{entry.target_entity}:{entry.target_id}:{entry.payload_hash}"
            entry.record_hash = hashlib.sha256(record_content.encode()).hexdigest()
            current_prev = entry.record_hash
        db.commit()
    
    # Check if seed users exist
    if db.query(User).count() == 0:
        seed_users = [
            User(username="admin", role="NATIONAL_ADMIN", state_id=None, district_id=None, full_name="National Director"),
            User(username="mh_officer", role="STATE_OFFICER", state_id="MH", district_id=None, full_name="Maharashtra State Officer"),
            User(username="pune_dso", role="DISTRICT_OFFICER", state_id="MH", district_id="MH-PUN", full_name="Pune District Sports Officer"),
            User(username="nagpur_dso", role="DISTRICT_OFFICER", state_id="MH", district_id="MH-NAG", full_name="Nagpur District Sports Officer"),
            User(username="pune_coach", role="COACH", state_id="MH", district_id="MH-PUN", full_name="Balewadi Academy Head Coach"),
            User(username="hr_officer", role="STATE_OFFICER", state_id="HR", district_id=None, full_name="Haryana State Officer"),
            User(username="sonipat_dso", role="DISTRICT_OFFICER", state_id="HR", district_id="HR-SON", full_name="Sonipat District Sports Officer")
        ]
        db.add_all(seed_users)

        # Seed Sports
        sports = [
            Sport(code="BOX", name="Boxing", category="INDIVIDUAL", is_olympic=True, is_national=True),
            Sport(code="WRE", name="Wrestling", category="INDIVIDUAL", is_olympic=True, is_national=True),
            Sport(code="ATH", name="Athletics", category="INDIVIDUAL", is_olympic=True, is_national=True),
            Sport(code="KAB", name="Kabaddi", category="TEAM", is_olympic=False, is_national=True),
            Sport(code="BAD", name="Badminton", category="INDIVIDUAL", is_olympic=True, is_national=True)
        ]
        db.add_all(sports)
        db.commit()

        # Seed mock athletes
        box = db.query(Sport).filter(Sport.code == "BOX").first()
        ath1 = Athlete(
            kid="KID-MH-2024-0012",
            encrypted_name=encrypt_pii("Aarav Shinde"),
            encrypted_dob=encrypt_pii("2009-04-12"),
            gender="MALE",
            state_id="MH",
            district_id="MH-PUN",
            primary_sport_id=box.id,
            encrypted_guardian=encrypt_pii("Rajesh Shinde (Father)"),
            consent_status="GRANTED",
            verification_status="VERIFIED",
            is_minor=True,
            is_synthetic=True
        )
        ath2 = Athlete(
            kid="KID-MH-2023-0891",
            encrypted_name=encrypt_pii("Pooja Kulkarni"),
            encrypted_dob=encrypt_pii("2002-11-20"),
            gender="FEMALE",
            state_id="MH",
            district_id="MH-PUN",
            primary_sport_id=box.id,
            encrypted_guardian=None,
            consent_status="GRANTED",
            verification_status="VERIFIED",
            is_minor=False,
            is_synthetic=True
        )
        db.add_all([ath1, ath2])

        # Seed Pipeline Snapshots
        snap1 = PipelineSnapshot(
            state_id="MH",
            district_id="MH-PUN",
            sport_id=box.id,
            age_band="U-17",
            identified_count=18,
            verified_count=12,
            supported_count=6,
            progressed_count=2,
            is_suppressed=False
        )
        snap2 = PipelineSnapshot(
            state_id="MH",
            district_id="MH-NAG",
            sport_id=box.id,
            age_band="U-17",
            identified_count=3,
            verified_count=2,
            supported_count=1,
            progressed_count=0,
            is_suppressed=True  # Under small cell threshold
        )
        db.add_all([snap1, snap2])
        db.commit()

    db.close()
