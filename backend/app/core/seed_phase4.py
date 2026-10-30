import json
import datetime
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, Base, engine
from app.models.entities import PolicyChunk

POLICY_DOCUMENTS = [
    {
        "source_document": "MYAS Khelo India Operational Guidelines 2024",
        "source_page": "Page 28",
        "source_clause": "Clause 4.2",
        "title": "Talent Identification Norms and National Selection Benchmarks",
        "text_content": (
            "Athletes in the 10 to 18 age band participating in Khelo India Youth Games or "
            "National School Games recognized by SGFI are eligible for talent assessment. "
            "Verification of age and school enrolment by the authorized District Sports Officer "
            "is mandatory prior to financial assistance or scholarship disbursement."
        ),
        "keywords": ["talent", "identification", "khelo india", "age", "10-18", "dso", "verification", "scholarship"]
    },
    {
        "source_document": "MYAS Khelo India Operational Guidelines 2024",
        "source_page": "Page 42",
        "source_clause": "Clause 8.1",
        "title": "Equipment Grant Allocation and Tracking Norms",
        "text_content": (
            "Sports science and performance equipment issued to accredited academies must maintain "
            "an append-only lending register with unique QR serialisation. Equipment on loan exceeding "
            "the return period by 14 days requires formal DSO audit review before replacement issuance."
        ),
        "keywords": ["equipment", "qr", "loan", "lending", "register", "overdue", "dso", "audit"]
    },
    {
        "source_document": "Ministry of Youth Affairs & Sports (MYAS) Circular 2023/SP-1",
        "source_page": "Page 4",
        "source_clause": "Section 2.3",
        "title": "Strict Minor Privacy Protection and DPDP Act Compliance",
        "text_content": (
            "In compliance with the Digital Personal Data Protection Act 2023, data fiduciaries "
            "processing minor athlete profiles (< 18 years) must obtain verifiable parental/guardian "
            "consent. Cross-district or unauthorized queries for minor records must return Not Found (404) "
            "without confirming existence. Direct plain text logging of minor identifiers is prohibited."
        ),
        "keywords": ["dpdp", "privacy", "minor", "consent", "guardian", "parental", "404", "pii"]
    },
    {
        "source_document": "Railway Sports Promotion Board (RSPB) Recruitment Norms 2025",
        "source_page": "Page 15",
        "source_clause": "Clause 5(b)",
        "title": "Direct Recruitment Under Sports Quota in Grade Pay 1900/2000",
        "text_content": (
            "Candidates representing the State or Country in Senior or Junior National Championships "
            "with minimum 3rd position medal finish in recognized individual Olympic or National sports "
            "are eligible for Junior Ticket Collector and Clerk appointments under sports quota."
        ),
        "keywords": ["railway", "recruitment", "sports quota", "job", "ticket collector", "clerk", "olympic"]
    },
    {
        "source_document": "Sports Authority of India (SAI) National Coaching Framework",
        "source_page": "Page 19",
        "source_clause": "Rule 11.4",
        "title": "Trainer Accreditation Validity and Institutional Placement",
        "text_content": (
            "All national sports academies and District Sports Complexes must employ coaches holding "
            "active certification from SAI or International Federations. Any trainer holding a REVOKED "
            "or EXPIRED certification is strictly ineligible for placement or state honorarium."
        ),
        "keywords": ["trainer", "coach", "certification", "sai", "revoked", "placement", "academy"]
    }
]

def seed_policy_chunks():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    if db.query(PolicyChunk).count() == 0:
        for doc in POLICY_DOCUMENTS:
            chunk = PolicyChunk(
                source_document=doc["source_document"],
                source_page=doc["source_page"],
                source_clause=doc["source_clause"],
                title=doc["title"],
                text_content=doc["text_content"],
                keywords_json=json.dumps(doc["keywords"])
            )
            db.add(chunk)
        db.commit()
    db.close()

if __name__ == "__main__":
    seed_policy_chunks()
