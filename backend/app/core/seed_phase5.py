import json
import datetime
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, Base, engine
from app.models.entities import StateAdapterManifest

STATE_MANIFESTS = [
    {
        "state_id": "MH",
        "state_name": "Maharashtra",
        "version": "1.2.0",
        "primary_language": "mr",
        "supported_languages": ["en", "mr", "hi"],
        "priority_sports": ["Boxing", "Wrestling", "Athletics", "Kabaddi", "Badminton"],
        "state_policies": [
            {
                "policy_code": "MH-SP-2024-C1",
                "title": "Chhatrapati Shivaji Maharaj State Sports Award Scheme",
                "age_cutoff": 25,
                "monthly_stipend_inr": 15000
            },
            {
                "policy_code": "MH-RUR-2025",
                "title": "Gramin Krida Vikas Yojana (Rural Sports Development)",
                "focus_districts": ["MH-PUN", "MH-NAG", "MH-KOL"]
            }
        ]
    },
    {
        "state_id": "HR",
        "state_name": "Haryana",
        "version": "1.1.0",
        "primary_language": "hi",
        "supported_languages": ["en", "hi"],
        "priority_sports": ["Wrestling", "Boxing", "Athletics", "Shooting"],
        "state_policies": [
            {
                "policy_code": "HR-OLY-CASH-2024",
                "title": "Haryana Cash Prize & Job Security for Olympic & Asian Medalists",
                "gold_medal_grant_inr": 60000000,
                "employment_group": "Group-A HCS/HPS"
            }
        ]
    }
]

def seed_state_manifests():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(StateAdapterManifest).count() == 0:
        for m in STATE_MANIFESTS:
            manifest = StateAdapterManifest(
                state_id=m["state_id"],
                state_name=m["state_name"],
                version=m["version"],
                primary_language=m["primary_language"],
                supported_languages_json=json.dumps(m["supported_languages"]),
                priority_sports_json=json.dumps(m["priority_sports"]),
                state_policies_json=json.dumps(m["state_policies"]),
                is_active=True
            )
            db.add(manifest)
        db.commit()
    db.close()

if __name__ == "__main__":
    seed_state_manifests()
