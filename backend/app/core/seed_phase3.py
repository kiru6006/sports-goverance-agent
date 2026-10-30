import json
import datetime
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, Base, engine
from app.models.entities import (
    User, Sport, Athlete, Facility, Trainer, Scheme, SchemeRule, Opportunity, TrainerCertification
)

def seed_phase3_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    admin = db.query(User).filter(User.username == "admin").first()
    mh_officer = db.query(User).filter(User.username == "mh_officer").first()

    # Seed Schemes with verify_with_ministry badge
    if db.query(Scheme).count() == 0:
        scheme1 = Scheme(
            code="KHELO-INDIA-TALENT-DEV",
            name="Khelo India Talent Development Scheme (Placeholder)",
            level="central",
            owner_body="Sports Authority of India (SAI)",
            is_placeholder=True,
            verify_with_ministry=True
        )
        scheme2 = Scheme(
            code="MH-YOUTH-SPORTS-SCHOLARSHIP",
            name="Maharashtra State Youth Sports Scholarship (Placeholder)",
            level="state",
            owner_body="Maharashtra Directorate of Sports",
            is_placeholder=True,
            verify_with_ministry=True
        )
        db.add_all([scheme1, scheme2])
        db.commit()

        # Seed approved and draft SchemeRules
        rule1_json = {
            "schema_version": "1.0",
            "required_fields": ["age", "verification_status", "highest_achievement_level"],
            "criteria": [
                {"field": "age", "operator": "between", "value": [10, 18], "reason_text": "Age must be between 10 and 18 years"},
                {"field": "verification_status", "operator": "eq", "value": "VERIFIED", "reason_text": "Athlete must be verified by District Sports Officer"},
                {"field": "highest_achievement_level", "operator": "in", "value": ["state", "national", "intl"], "reason_text": "Must hold at least State-level medal"}
            ]
        }

        # Seed Approved Rule (Maker: mh_officer, Approver: admin)
        s_rule1 = SchemeRule(
            scheme_id=scheme1.id,
            version="1.0.0",
            rule_json=json.dumps(rule1_json),
            effective_from=datetime.date(2024, 1, 1),
            effective_to=datetime.date(2028, 12, 31),
            source_document="MYAS Khelo India Operational Guidelines 2024",
            source_page="Clause 4.2, Page 28",
            source_clause="Talent Identification Norms §4.2",
            status="APPROVED",
            author_id=mh_officer.id if mh_officer else "mock-author",
            approver_id=admin.id if admin else "mock-admin",
            approved_at=datetime.datetime.utcnow()
        )

        # Seed Draft Rule (Unapproved - invisible to evaluation path)
        s_rule2_draft = SchemeRule(
            scheme_id=scheme2.id,
            version="0.1.0-draft",
            rule_json=json.dumps(rule1_json),
            effective_from=datetime.date(2026, 1, 1),
            effective_to=None,
            source_document="MH Sports Policy Draft Circular 2026",
            source_page="Page 12",
            source_clause="Section 3B",
            status="DRAFT",
            author_id=mh_officer.id if mh_officer else "mock-author",
            approver_id=None,
            approved_at=None
        )
        db.add_all([s_rule1, s_rule2_draft])
        db.commit()

        # Seed Opportunity
        opp = Opportunity(
            title="Sports Quota Junior Ticket Collector (Boxer/Wrestler)",
            type="job",
            employer="Central Railway, Mumbai Division",
            eligibility_rule_id=s_rule1.id,
            slots=5,
            state_scope="MH",
            district_scope=None,
            deadline=datetime.date(2026, 12, 31),
            status="OPEN"
        )
        db.add(opp)
        db.commit()

    # Seed Trainer Certifications
    trainer = db.query(Trainer).first()
    if trainer and db.query(TrainerCertification).filter(TrainerCertification.trainer_id == trainer.id).count() == 0:
        cert = TrainerCertification(
            trainer_id=trainer.id,
            course="AIBA 2-Star Elite Coaching Diploma",
            provider="International Boxing Association (IBA)",
            issued_on=datetime.date(2023, 1, 1),
            expires_on=datetime.date(2027, 1, 1),
            status="ACTIVE"
        )
        db.add(cert)
        db.commit()

    db.close()

if __name__ == "__main__":
    seed_phase3_data()
