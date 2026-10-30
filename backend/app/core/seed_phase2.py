import json
import datetime
from sqlalchemy.orm import Session
from app.core.db import SessionLocal, Base, engine
from app.models.entities import (
    User, Sport, Athlete, Facility, Population, SupportRecord, EquipmentItem, EquipmentLoan, FacilityUtilisation
)

def seed_phase2_data():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed Population census estimates (Synthetic)
    if db.query(Population).count() == 0:
        pop_seeds = [
            Population(state_id="MH", district_id="MH-PUN", age_band="U-17", gender="ALL", population_count=450000),
            Population(state_id="MH", district_id="MH-NAG", age_band="U-17", gender="ALL", population_count=320000),
            Population(state_id="HR", district_id="HR-SON", age_band="U-17", gender="ALL", population_count=210000),
            Population(state_id="HR", district_id="HR-ROH", age_band="U-17", gender="ALL", population_count=190000),
        ]
        db.add_all(pop_seeds)
        db.commit()

    # Seed Support Records for existing athletes
    ath1 = db.query(Athlete).filter(Athlete.kid == "KID-MH-2024-0012").first()
    if ath1 and db.query(SupportRecord).filter(SupportRecord.athlete_id == ath1.id).count() == 0:
        sr = SupportRecord(
            athlete_id=ath1.id,
            support_type="equipment",
            status="ACTIVE",
            start_date=datetime.date(2024, 1, 1),
            notes="State grant for specialized boxing gloves and protective gear"
        )
        db.add(sr)
        db.commit()

    # Seed Equipment Items with QR code
    fac1 = db.query(Facility).filter(Facility.district_id == "MH-PUN").first()
    dso = db.query(User).filter(User.username == "pune_dso").first()
    
    if fac1 and db.query(EquipmentItem).count() == 0:
        eq1 = EquipmentItem(
            facility_id=fac1.id,
            item_name="Competition Boxing Gloves 10oz",
            item_type="GLOVES",
            condition="EXCELLENT",
            qr_code="QR-EQ-MH-PUN-001",
            status="ISSUED"
        )
        eq2 = EquipmentItem(
            facility_id=fac1.id,
            item_name="Heavy Punching Bag 150lb",
            item_type="WEIGHTS",
            condition="GOOD",
            qr_code="QR-EQ-MH-PUN-002",
            status="AVAILABLE"
        )
        db.add_all([eq1, eq2])
        db.commit()

        # Seed Overdue and Active Equipment Loans
        now = datetime.datetime.utcnow()
        loan1 = EquipmentLoan(
            item_id=eq1.id,
            borrower_type="ATHLETE",
            borrower_id=ath1.id if ath1 else "mock-athlete-id",
            issued_at=now - datetime.timedelta(days=45),
            due_at=now - datetime.timedelta(days=15),  # OVERDUE
            returned_at=None,
            condition_out="EXCELLENT",
            condition_in=None,
            issued_by=dso.id if dso else "admin"
        )
        db.add(loan1)
        db.commit()

    # Seed Facility Monthly Utilisation
    if fac1 and db.query(FacilityUtilisation).filter(FacilityUtilisation.facility_id == fac1.id).count() == 0:
        util = FacilityUtilisation(
            facility_id=fac1.id,
            period=datetime.date(2026, 2, 1),
            sessions=48,
            athlete_count=124,
            hours_used=180.0  # Out of 300 capacity = 60%
        )
        db.add(util)
        db.commit()

    db.close()

if __name__ == "__main__":
    seed_phase2_data()
