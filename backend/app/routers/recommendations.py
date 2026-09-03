"""
Transfer Recommendations Router.
Handles explainable recommendations browsing, human-in-the-loop approvals,
rejections with structured reasons, and custom overrides.
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models import (
    TransferRecommendation, RecommendationEvidence, TransferAction,
    OverrideReason, InventoryBatch, User
)
from backend.app.schemas import (
    RecommendationOut, ApproveRequest, RejectRequest, OverrideRequest,
    GenerateRecommendationsRequest
)
from backend.app.recommender.engine import generate_recommendations_for_db
from backend.app.services.audit_service import log_audit_event
from backend.app.utils.security import get_current_user, require_roles

router = APIRouter(prefix="/api/recommendations", tags=["Recommendations"])

@router.get("", response_model=List[RecommendationOut])
def list_recommendations(
    status_filter: Optional[str] = Query(None, alias="status"),
    risk_level: Optional[str] = Query(None),
    pharmacy_id: Optional[str] = Query(None),
    is_high_impact: Optional[bool] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(TransferRecommendation)

    # Scoping for Pharmacist role: only show recommendations where their pharmacy is source or destination
    if current_user.role == "PHARMACIST" and current_user.assigned_pharmacy_id:
        p_id = current_user.assigned_pharmacy_id
        query = query.filter(
            (TransferRecommendation.source_pharmacy_id == p_id) |
            (TransferRecommendation.destination_pharmacy_id == p_id)
        )
    elif pharmacy_id:
        query = query.filter(
            (TransferRecommendation.source_pharmacy_id == pharmacy_id) |
            (TransferRecommendation.destination_pharmacy_id == pharmacy_id)
        )

    if status_filter:
        query = query.filter(TransferRecommendation.status == status_filter)
    if risk_level:
        query = query.filter(TransferRecommendation.risk_level == risk_level)
    if is_high_impact is not None:
        query = query.filter(TransferRecommendation.is_high_impact == is_high_impact)

    # Order by potential value saved desc
    recs = query.order_by(TransferRecommendation.potential_value_saved.desc()).all()
    return recs

@router.get("/{rec_id}", response_model=RecommendationOut)
def get_recommendation_detail(
    rec_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(TransferRecommendation).filter(TransferRecommendation.recommendation_id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    # Pharmacist access check
    if current_user.role == "PHARMACIST" and current_user.assigned_pharmacy_id:
        p_id = current_user.assigned_pharmacy_id
        if rec.source_pharmacy_id != p_id and rec.destination_pharmacy_id != p_id:
            raise HTTPException(status_code=403, detail="Access denied to recommendations outside assigned pharmacy")

    return rec

@router.post("/{rec_id}/approve", response_model=RecommendationOut)
def approve_recommendation(
    rec_id: str,
    req: ApproveRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(TransferRecommendation).filter(TransferRecommendation.recommendation_id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot approve recommendation in '{rec.status}' status")

    # High-impact transfers require explicit confirmation
    if rec.is_high_impact and not req.confirmed_high_impact:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="High-impact transfer requires explicit human confirmation checkbox."
        )

    # Check branch authorization if pharmacist
    if current_user.role == "PHARMACIST" and current_user.assigned_pharmacy_id:
        if rec.source_pharmacy_id != current_user.assigned_pharmacy_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Pharmacist can only approve outgoing transfers from their assigned source branch."
            )

    prev_state = rec.status
    rec.status = "APPROVED"
    rec.updated_at = datetime.utcnow()

    # Record Transfer Action
    action = TransferAction(
        recommendation_id=rec.recommendation_id,
        user_id=current_user.id,
        action_type="APPROVED",
        transferred_quantity=rec.recommended_quantity,
        action_timestamp=datetime.utcnow(),
        notes=req.notes
    )
    db.add(action)

    # Record Audit Log
    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="APPROVED",
        recommendation_id=rec.recommendation_id,
        previous_state=prev_state,
        new_state="APPROVED",
        quantity=rec.recommended_quantity,
        source_pharmacy_id=rec.source_pharmacy_id,
        destination_pharmacy_id=rec.destination_pharmacy_id,
        reason=req.notes or "Human approved transfer recommendation"
    )

    db.commit()
    db.refresh(rec)
    return rec

@router.post("/{rec_id}/reject", response_model=RecommendationOut)
def reject_recommendation(
    rec_id: str,
    req: RejectRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(TransferRecommendation).filter(TransferRecommendation.recommendation_id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot reject recommendation in '{rec.status}' status")

    if not req.reason_category:
        raise HTTPException(status_code=400, detail="Rejection reason category is mandatory.")

    prev_state = rec.status
    rec.status = "REJECTED"
    rec.updated_at = datetime.utcnow()

    # Record Transfer Action
    action = TransferAction(
        recommendation_id=rec.recommendation_id,
        user_id=current_user.id,
        action_type="REJECTED",
        transferred_quantity=0,
        action_timestamp=datetime.utcnow(),
        notes=f"[{req.reason_category}] {req.custom_reason or ''}"
    )
    db.add(action)

    # Record Audit Log
    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="REJECTED",
        recommendation_id=rec.recommendation_id,
        previous_state=prev_state,
        new_state="REJECTED",
        quantity=rec.recommended_quantity,
        source_pharmacy_id=rec.source_pharmacy_id,
        destination_pharmacy_id=rec.destination_pharmacy_id,
        reason=f"[{req.reason_category}] {req.custom_reason or ''}"
    )

    db.commit()
    db.refresh(rec)
    return rec

@router.post("/{rec_id}/override", response_model=RecommendationOut)
def override_recommendation(
    rec_id: str,
    req: OverrideRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(TransferRecommendation).filter(TransferRecommendation.recommendation_id == rec_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if rec.status != "PENDING":
        raise HTTPException(status_code=400, detail=f"Cannot override recommendation in '{rec.status}' status")

    if req.overridden_quantity <= 0:
        raise HTTPException(status_code=400, detail="Overridden quantity must be greater than zero.")

    prev_state = rec.status
    rec.status = "OVERRIDDEN"
    rec.recommended_quantity = req.overridden_quantity
    rec.potential_value_saved = round(req.overridden_quantity * rec.unit_price, 2)
    rec.updated_at = datetime.utcnow()

    # Save Override Record
    override = OverrideReason(
        recommendation_id=rec.recommendation_id,
        reason_category=req.reason_category,
        custom_reason=req.custom_reason,
        overridden_quantity=req.overridden_quantity,
        user_id=current_user.id,
        created_at=datetime.utcnow()
    )
    db.add(override)

    # Record Action
    action = TransferAction(
        recommendation_id=rec.recommendation_id,
        user_id=current_user.id,
        action_type="OVERRIDDEN",
        transferred_quantity=req.overridden_quantity,
        action_timestamp=datetime.utcnow(),
        notes=f"Overridden to {req.overridden_quantity} units. [{req.reason_category}] {req.custom_reason or ''}"
    )
    db.add(action)

    # Record Audit Log
    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="OVERRIDDEN",
        recommendation_id=rec.recommendation_id,
        previous_state=prev_state,
        new_state="OVERRIDDEN",
        quantity=req.overridden_quantity,
        source_pharmacy_id=rec.source_pharmacy_id,
        destination_pharmacy_id=rec.destination_pharmacy_id,
        reason=f"Quantity changed to {req.overridden_quantity}. [{req.reason_category}] {req.custom_reason or ''}"
    )

    db.commit()
    db.refresh(rec)
    return rec

@router.post("/generate", response_model=List[RecommendationOut])
def generate_recommendations(
    req: GenerateRecommendationsRequest,
    current_user: User = Depends(require_roles(["ADMIN", "MANAGER"])),
    db: Session = Depends(get_db)
):
    """Trigger engine to regenerate recommendations."""
    recs = generate_recommendations_for_db(db, force_regenerate=req.force_regenerate)
    log_audit_event(
        db=db,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action="GENERATED",
        reason=f"Manual recommendation re-generation triggered by {current_user.role}"
    )
    return recs
