"""
Pharmacies Router.
Provides network locations, storage capacity, operating status, and health metrics.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import Pharmacy, InventoryBatch, TransferRecommendation
from backend.app.schemas import PharmacyOut, PharmacyDetailOut
from backend.app.recommender.risk_scorer import analyze_batch_risk
from backend.app.utils.security import get_current_user

router = APIRouter(prefix="/api/pharmacies", tags=["Pharmacies"])

@router.get("", response_model=List[PharmacyOut])
def list_pharmacies(db: Session = Depends(get_db)):
    return db.query(Pharmacy).all()

@router.get("/{pharmacy_id}", response_model=PharmacyDetailOut)
def get_pharmacy_detail(pharmacy_id: str, db: Session = Depends(get_db)):
    p = db.query(Pharmacy).filter(Pharmacy.pharmacy_id == pharmacy_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Pharmacy not found")

    batches = db.query(InventoryBatch).filter(InventoryBatch.pharmacy_id == pharmacy_id).all()
    
    total_val = 0.0
    near_exp_count = 0
    near_exp_val = 0.0
    crit_count = 0

    for b in batches:
        b_val = b.quantity * b.unit_price
        total_val += b_val
        risk = analyze_batch_risk(b.quantity, b.unit_price, b.expiry_date, 1.0)
        if risk["risk_level"] in ["CRITICAL", "HIGH"]:
            near_exp_count += 1
            near_exp_val += b_val
        if risk["risk_level"] == "CRITICAL":
            crit_count += 1

    incoming_count = db.query(TransferRecommendation).filter(
        TransferRecommendation.destination_pharmacy_id == pharmacy_id,
        TransferRecommendation.status.in_(["PENDING", "APPROVED"])
    ).count()

    outgoing_count = db.query(TransferRecommendation).filter(
        TransferRecommendation.source_pharmacy_id == pharmacy_id,
        TransferRecommendation.status.in_(["PENDING", "APPROVED"])
    ).count()

    return PharmacyDetailOut(
        id=p.id,
        pharmacy_id=p.pharmacy_id,
        pharmacy_name=p.pharmacy_name,
        city=p.city,
        latitude=p.latitude,
        longitude=p.longitude,
        storage_capacity=p.storage_capacity,
        operating_status=p.operating_status,
        total_batches=len(batches),
        total_stock_value=round(total_val, 2),
        near_expiry_count=near_exp_count,
        near_expiry_value=round(near_exp_val, 2),
        critical_risk_count=crit_count,
        incoming_transfers_count=incoming_count,
        outgoing_transfers_count=outgoing_count
    )
