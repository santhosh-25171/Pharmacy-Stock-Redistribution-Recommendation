"""
Database Initialization and Synthetic Data Seeding Service.
Populates tables from synthetic CSVs and initializes default user roles.
"""

import os
import sys
import csv
from pathlib import Path
from datetime import datetime

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy.orm import Session
from backend.app.database.session import Base, engine, SessionLocal
from backend.app.models import (
    User, Pharmacy, Medicine, InventoryBatch, DemandForecast,
    TransferRecommendation, RecommendationEvidence, AuditLog
)
from backend.app.utils.security import get_password_hash
from backend.app.recommender.engine import generate_recommendations_for_db

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
DATA_DIR = os.path.join(BASE_DIR, "data")

def seed_default_users(db: Session):
    """Creates standard demo accounts for testing and evaluation."""
    users_data = [
        {
            "email": "admin@pharmacy.io",
            "password": "Admin@123",
            "full_name": "System Administrator",
            "role": "ADMIN",
            "assigned_pharmacy_id": None
        },
        {
            "email": "manager@pharmacy.io",
            "password": "Manager@123",
            "full_name": "Regional Supply Chain Manager",
            "role": "MANAGER",
            "assigned_pharmacy_id": None
        },
        {
            "email": "pharmacist@pharmacy.io",
            "password": "Pharmacist@123",
            "full_name": "Senior Pharmacist (Central Hub)",
            "role": "PHARMACIST",
            "assigned_pharmacy_id": "PHARM-001"
        },
        {
            "email": "pharmacist2@pharmacy.io",
            "password": "Pharmacist@123",
            "full_name": "Duty Pharmacist (Indiranagar)",
            "role": "PHARMACIST",
            "assigned_pharmacy_id": "PHARM-002"
        }
    ]

    for u_info in users_data:
        existing = db.query(User).filter(User.email == u_info["email"]).first()
        if not existing:
            user = User(
                email=u_info["email"],
                hashed_password=get_password_hash(u_info["password"]),
                full_name=u_info["full_name"],
                role=u_info["role"],
                assigned_pharmacy_id=u_info["assigned_pharmacy_id"],
                is_active=True
            )
            db.add(user)
    db.commit()

def seed_database_if_empty(db: Session = None, force_reseed: bool = False):
    """
    Initializes DB tables and seeds 5,000+ batches and metadata if not already populated.
    """
    close_after = False
    if db is None:
        db = SessionLocal()
        close_after = True

    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)

        # Seed Users
        seed_default_users(db)

        # Check if already seeded
        pharmacy_count = db.query(Pharmacy).count()
        if pharmacy_count > 0 and not force_reseed:
            print("[INFO] Database already seeded with records.")
            return

        print("[*] Seeding database from synthetic CSV files...")

        # 1. Seed Pharmacies
        pharm_path = os.path.join(DATA_DIR, "synthetic_pharmacies.csv")
        if os.path.exists(pharm_path):
            with open(pharm_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not db.query(Pharmacy).filter(Pharmacy.pharmacy_id == row["pharmacy_id"]).first():
                        db.add(Pharmacy(
                            pharmacy_id=row["pharmacy_id"],
                            pharmacy_name=row["pharmacy_name"],
                            city=row["city"],
                            latitude=float(row["latitude"]),
                            longitude=float(row["longitude"]),
                            storage_capacity=int(row["storage_capacity"]),
                            operating_status=row["operating_status"]
                        ))
            db.commit()
            print(f"[OK] Seeded pharmacies.")

        # 2. Seed Medicines
        med_path = os.path.join(DATA_DIR, "synthetic_medicines.csv")
        if os.path.exists(med_path):
            with open(med_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if not db.query(Medicine).filter(Medicine.medicine_id == row["medicine_id"]).first():
                        db.add(Medicine(
                            medicine_id=row["medicine_id"],
                            name=row["name"],
                            category=row["category"],
                            unit_price=float(row["unit_price"]),
                            is_critical=row["is_critical"].lower() in ["true", "1", "t"],
                            storage_type=row.get("storage_type", "Room Temperature")
                        ))
            db.commit()
            print(f"[OK] Seeded medicines.")

        # 3. Seed Demand Forecasts
        demand_path = os.path.join(DATA_DIR, "synthetic_demand.csv")
        if os.path.exists(demand_path):
            with open(demand_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                demand_objs = []
                for row in reader:
                    demand_objs.append(DemandForecast(
                        medicine_id=row["medicine_id"],
                        pharmacy_id=row["pharmacy_id"],
                        daily_demand=float(row["daily_demand"]),
                        weekly_demand=float(row["weekly_demand"]),
                        monthly_demand=float(row["monthly_demand"]),
                        historical_demand=float(row["historical_demand"]),
                        demand_trend=row["demand_trend"]
                    ))
                db.bulk_save_objects(demand_objs)
                db.commit()
                print(f"[OK] Seeded demand forecasts.")

        # 4. Seed Inventory Batches
        inv_path = os.path.join(DATA_DIR, "synthetic_inventory.csv")
        if os.path.exists(inv_path):
            with open(inv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                batch_objs = []
                for row in reader:
                    batch_objs.append(InventoryBatch(
                        inventory_id=row["inventory_id"],
                        medicine_id=row["medicine_id"],
                        medicine_name=row["medicine_name"],
                        medicine_category=row["medicine_category"],
                        batch_id=row["batch_id"],
                        pharmacy_id=row["pharmacy_id"],
                        quantity=int(row["quantity"]),
                        unit_price=float(row["unit_price"]),
                        expiry_date=row["expiry_date"],
                        received_date=row["received_date"],
                        stock_status=row["stock_status"],
                        edge_case_tag=row.get("edge_case_tag", "NONE")
                    ))
                db.bulk_save_objects(batch_objs)
                db.commit()
                print(f"[OK] Seeded {len(batch_objs)} inventory batches.")

        # 5. Generate Initial Recommendations
        print("[*] Generating initial recommendations in database...")
        recs = generate_recommendations_for_db(db, force_regenerate=True)
        print(f"[OK] Generated {len(recs)} initial recommendations.")

        # 6. Create Initial Audit Entry
        db.add(AuditLog(
            user_email="system@pharmacy.io",
            user_role="SYSTEM",
            action="SEEDED",
            reason="Initial synthetic inventory database population and recommendation engine run",
            timestamp=datetime.utcnow()
        ))
        db.commit()
        print("[OK] Database initialization and seeding complete.")

    finally:
        if close_after:
            db.close()
