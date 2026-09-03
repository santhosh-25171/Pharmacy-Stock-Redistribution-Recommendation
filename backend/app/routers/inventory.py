"""
Inventory Batches Router.
Allows searching, filtering, and risk inspection of inventory across pharmacies.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import InventoryBatch, Pharmacy, DemandForecast, User
from backend.app.schemas import InventoryBatchOut
from backend.app.recommender.risk_scorer import analyze_batch_risk
from backend.app.utils.security import get_current_user

router = APIRouter(prefix="/api/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryBatchOut])
def get_inventory(
    pharmacy_id: Optional[str] = Query(None, description="Filter by pharmacy ID"),
    medicine_id: Optional[str] = Query(None, description="Filter by medicine ID"),
    category: Optional[str] = Query(None, description="Filter by medicine category"),
    risk_level: Optional[str] = Query(None, description="Filter by risk (CRITICAL, HIGH, MEDIUM, LOW, EXPIRED)"),
    stock_status: Optional[str] = Query(None, description="Filter by stock status"),
    search: Optional[str] = Query(None, description="Search medicine name or batch ID"),
    limit: int = Query(200, le=1000),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(InventoryBatch)

    # Pharmacist role scoping: If pharmacist has an assigned pharmacy, enforce filtering to assigned branch
    if current_user.role == "PHARMACIST" and current_user.assigned_pharmacy_id:
        query = query.filter(InventoryBatch.pharmacy_id == current_user.assigned_pharmacy_id)
    elif pharmacy_id:
        query = query.filter(InventoryBatch.pharmacy_id == pharmacy_id)

    if medicine_id:
        query = query.filter(InventoryBatch.medicine_id == medicine_id)
    if category:
        query = query.filter(InventoryBatch.medicine_category == category)
    if stock_status:
        query = query.filter(InventoryBatch.stock_status == stock_status)
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (InventoryBatch.medicine_name.ilike(search_pattern)) |
            (InventoryBatch.batch_id.ilike(search_pattern))
        )

    batches = query.offset(offset).limit(limit).all()

    # Pre-fetch pharmacies and demand
    pharmacy_names = {p.pharmacy_id: p.pharmacy_name for p in db.query(Pharmacy).all()}
    demand_records = db.query(DemandForecast).all()
    demand_map = {(d.pharmacy_id, d.medicine_id): d.daily_demand for d in demand_records}

    results = []
    for b in batches:
        daily_d = demand_map.get((b.pharmacy_id, b.medicine_id), 1.0)
        risk_info = analyze_batch_risk(
            quantity=b.quantity,
            unit_price=b.unit_price,
            expiry_date_str=b.expiry_date,
            daily_demand=daily_d
        )

        if risk_level and risk_info["risk_level"] != risk_level:
            continue

        results.append(InventoryBatchOut(
            id=b.id,
            inventory_id=b.inventory_id,
            medicine_id=b.medicine_id,
            medicine_name=b.medicine_name,
            medicine_category=b.medicine_category,
            batch_id=b.batch_id,
            pharmacy_id=b.pharmacy_id,
            pharmacy_name=pharmacy_names.get(b.pharmacy_id, b.pharmacy_id),
            quantity=b.quantity,
            unit_price=b.unit_price,
            total_value=risk_info["total_value"],
            expiry_date=b.expiry_date,
            days_to_expiry=risk_info["days_to_expiry"],
            received_date=b.received_date,
            stock_status=b.stock_status,
            risk_level=risk_info["risk_level"],
            daily_demand=risk_info["daily_demand"],
            days_to_consume=risk_info["days_to_consume"],
            excess_quantity=risk_info["excess_quantity"],
            recommended_action=risk_info["recommended_action"],
            edge_case_tag=b.edge_case_tag
        ))

    return results

@router.get("/{inventory_id}", response_model=InventoryBatchOut)
def get_inventory_batch_detail(
    inventory_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    b = db.query(InventoryBatch).filter(InventoryBatch.inventory_id == inventory_id).first()
    if not b:
        raise HTTPException(status_code=404, detail="Inventory batch not found")

    if current_user.role == "PHARMACIST" and current_user.assigned_pharmacy_id and b.pharmacy_id != current_user.assigned_pharmacy_id:
        raise HTTPException(status_code=403, detail="Access denied to other pharmacy inventory")

    pharmacy = db.query(Pharmacy).filter(Pharmacy.pharmacy_id == b.pharmacy_id).first()
    demand = db.query(DemandForecast).filter(
        DemandForecast.pharmacy_id == b.pharmacy_id,
        DemandForecast.medicine_id == b.medicine_id
    ).first()
    daily_d = demand.daily_demand if demand else 1.0

    risk_info = analyze_batch_risk(b.quantity, b.unit_price, b.expiry_date, daily_d)

    return InventoryBatchOut(
        id=b.id,
        inventory_id=b.inventory_id,
        medicine_id=b.medicine_id,
        medicine_name=b.medicine_name,
        medicine_category=b.medicine_category,
        batch_id=b.batch_id,
        pharmacy_id=b.pharmacy_id,
        pharmacy_name=pharmacy.pharmacy_name if pharmacy else b.pharmacy_id,
        quantity=b.quantity,
        unit_price=b.unit_price,
        total_value=risk_info["total_value"],
        expiry_date=b.expiry_date,
        days_to_expiry=risk_info["days_to_expiry"],
        received_date=b.received_date,
        stock_status=b.stock_status,
        risk_level=risk_info["risk_level"],
        daily_demand=risk_info["daily_demand"],
        days_to_consume=risk_info["days_to_consume"],
        excess_quantity=risk_info["excess_quantity"],
        recommended_action=risk_info["recommended_action"],
        edge_case_tag=b.edge_case_tag
    )
