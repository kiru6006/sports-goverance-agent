import json
import datetime
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, Base, engine
from app.models.entities import (
    User, Sport, Athlete, Trainer, Institution, Affiliation, Achievement, JourneyEvent, Facility, PipelineSnapshot
)
from app.core.crypto import encrypt_pii

def seed_registry_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Re-verify and seed Sports
    if db.query(Sport).count() == 0:
        sports = [
            Sport(code="BOX", name="Boxing", category="INDIVIDUAL", is_olympic=True, is_national=True, federation="Boxing Federation of India"),
            Sport(code="WRE", name="Wrestling", category="INDIVIDUAL", is_olympic=True, is_national=True, federation="Wrestling Federation of India"),
            Sport(code="ATH", name="Athletics", category="INDIVIDUAL", is_olympic=True, is_national=True, federation="Athletics Federation of India"),
            Sport(code="KAB", name="Kabaddi", category="TEAM", is_olympic=False, is_national=True, federation="Amateur Kabaddi Federation of India"),
            Sport(code="BAD", name="Badminton", category="INDIVIDUAL", is_olympic=True, is_national=True, federation="Badminton Association of India")
        ]
        db.add_all(sports)
        db.commit()

    # Seed Trainers
    if db.query(Trainer).count() == 0:
        trainers = [
            Trainer(
                encrypted_name=encrypt_pii("Coach Ramesh Kumar"),
                state_id="MH",
                district_id="MH-PUN",
                sports_json=json.dumps(["Boxing"]),
                certifications_json=json.dumps(["SAI NIS Diploma (Boxing)", "AIBA 2-Star"]),
                verification_status="VERIFIED"
            ),
            Trainer(
                encrypted_name=encrypt_pii("Coach Sunita Malik"),
                state_id="HR",
                district_id="HR-SON",
                sports_json=json.dumps(["Wrestling"]),
                certifications_json=json.dumps(["SAI NIS Diploma (Wrestling)"]),
                verification_status="VERIFIED"
            )
        ]
        db.add_all(trainers)
        db.commit()

    # Seed Institutions
    if db.query(Institution).count() == 0:
        institutions = [
            Institution(
                name="Shiv Chhatrapati Sports Complex Academy",
                type="academy",
                state_id="MH",
                district_id="MH-PUN",
                sports_facilities_json=json.dumps(["Boxing Ring", "Athletic Track", "Gymnasium"])
            ),
            Institution(
                name="Sonipat Regional Sports Training Centre",
                type="academy",
                state_id="HR",
                district_id="HR-SON",
                sports_facilities_json=json.dumps(["Wrestling Hall", "Multipurpose Hall"])
            )
        ]
        db.add_all(institutions)
        db.commit()

    # Seed Facilities
    if db.query(Facility).count() == 0:
        facilities = [
            Facility(
                name="Balewadi Boxing & Athletic Arena",
                type="STADIUM",
                state_id="MH",
                district_id="MH-PUN",
                latitude=18.5793,
                longitude=73.7667,
                sports_json=json.dumps(["Boxing", "Athletics"])
            ),
            Facility(
                name="Sonipat District Sports Ground",
                type="GROUND",
                state_id="HR",
                district_id="HR-SON",
                latitude=28.9931,
                longitude=77.0151,
                sports_json=json.dumps(["Wrestling", "Kabaddi"])
            )
        ]
        db.add_all(facilities)
        db.commit()

    # Seed detailed Athlete achievements and journey events if missing
    pune_dso = db.query(User).filter(User.username == "pune_dso").first()
    pune_coach = db.query(User).filter(User.username == "pune_coach").first()
    box_sport = db.query(Sport).filter(Sport.code == "BOX").first()
    ath1 = db.query(Athlete).filter(Athlete.kid == "KID-MH-2024-0012").first()
    
    if ath1 and db.query(Achievement).filter(Achievement.athlete_id == ath1.id).count() == 0:
        # Link coach
        if pune_coach:
            ath1.coach_id = pune_coach.id
        
        ach = Achievement(
            athlete_id=ath1.id,
            sport_id=box_sport.id,
            event="State Youth Boxing Championship 54kg",
            level="state",
            result="Gold",
            event_date=datetime.date(2025, 8, 15)
        )
        db.add(ach)

        # Journey Events (Append-only timeline)
        events = [
            JourneyEvent(
                athlete_id=ath1.id,
                event_type="training_start",
                event_date=datetime.date(2023, 6, 1),
                notes="Joined Balewadi Boxing Academy under Coach Ramesh"
            ),
            JourneyEvent(
                athlete_id=ath1.id,
                event_type="competition",
                event_date=datetime.date(2025, 8, 15),
                notes="Secured Gold Medal at Maharashtra Youth Championship"
            )
        ]
        db.add_all(events)
        db.commit()

    db.close()

if __name__ == "__main__":
    seed_registry_data()
