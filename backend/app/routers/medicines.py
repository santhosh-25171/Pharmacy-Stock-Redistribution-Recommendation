"""
Medicines Catalog Router.
Lists synthetic medicines catalog with therapeutic categories and pricing.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import Medicine
from backend.app.schemas import MedicineOut

router = APIRouter(prefix="/api/medicines", tags=["Medicines"])

@router.get("", response_model=List[MedicineOut])
def list_medicines(
    category: Optional[str] = Query(None),
    is_critical: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    q = db.query(Medicine)
    if category:
        q = q.filter(Medicine.category == category)
    if is_critical is not None:
        q = q.filter(Medicine.is_critical == is_critical)
    return q.all()
