"""
Analytics Dashboard Router.
Aggregates real-time KPIs, near-expiry values, risk distributions, and transfer savings.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database.session import get_db
from backend.app.models import InventoryBatch, TransferRecommendation, Pharmacy, DemandForecast
from backend.app.schemas import AnalyticsDashboardOut
from backend.app.recommender.risk_scorer import analyze_batch_risk

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("", response_model=AnalyticsDashboardOut)
def get_analytics_dashboard(db: Session = Depends(get_db)):
    batches = db.query(InventoryBatch).all()
    pharmacies = {p.pharmacy_id: p.pharmacy_name for p in db.query(Pharmacy).all()}
    recs = db.query(TransferRecommendation).all()

    total_inv_val = 0.0
    near_exp_val = 0.0
    high_risk_count = 0
    risk_dist = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "EXPIRED": 0}
    
    pharm_risk_map = {p_id: {"pharmacy_id": p_id, "pharmacy_name": p_name, "near_expiry_value": 0.0, "near_expiry_batches": 0} for p_id, p_name in pharmacies.items()}
    cat_saved_map = {}

    for b in batches:
        b_val = b.quantity * b.unit_price
        total_inv_val += b_val

        risk = analyze_batch_risk(b.quantity, b.unit_price, b.expiry_date, 1.0)
        r_level = risk["risk_level"]
        risk_dist[r_level] = risk_dist.get(r_level, 0) + 1

        if r_level in ["CRITICAL", "HIGH"]:
            high_risk_count += 1
            near_exp_val += b_val
            if b.pharmacy_id in pharm_risk_map:
                pharm_risk_map[b.pharmacy_id]["near_expiry_value"] += b_val
                pharm_risk_map[b.pharmacy_id]["near_expiry_batches"] += 1

    # Recommendation status aggregates
    total_recs = len(recs)
    pending_recs = 0
    approved_recs = 0
    rejected_recs = 0
    overridden_recs = 0
    potential_saved = 0.0
    val_transferred = 0.0

    rec_status_dist = {"PENDING": 0, "APPROVED": 0, "REJECTED": 0, "OVERRIDDEN": 0}

    for r in recs:
        rec_status_dist[r.status] = rec_status_dist.get(r.status, 0) + 1
        potential_saved += r.potential_value_saved
        if r.status == "PENDING":
            pending_recs += 1
        elif r.status == "APPROVED":
            approved_recs += 1
            val_transferred += r.potential_value_saved
        elif r.status == "REJECTED":
            rejected_recs += 1
        elif r.status == "OVERRIDDEN":
            overridden_recs += 1
            val_transferred += r.potential_value_saved

        # Category breakdown
        cat_saved_map[r.medicine_name] = cat_saved_map.get(r.medicine_name, 0.0) + r.potential_value_saved

    decided_recs = approved_recs + rejected_recs + overridden_recs
    approval_rate = (approved_recs / max(1, decided_recs)) * 100.0 if decided_recs > 0 else 0.0
    rejection_rate = (rejected_recs / max(1, decided_recs)) * 100.0 if decided_recs > 0 else 0.0
    override_rate = (overridden_recs / max(1, decided_recs)) * 100.0 if decided_recs > 0 else 0.0

    # Stock lost to expiry (calculated from expired batches)
    stock_lost = sum(b.quantity * b.unit_price for b in batches if b.stock_status == "EXPIRED" or b.edge_case_tag == "ALREADY_EXPIRED")
    # Value used locally before expiry (~65% of near expiry inventory that is consumed through daily velocity)
    value_used_locally = max(0.0, total_inv_val - near_exp_val + (near_exp_val * 0.45))

    near_expiry_by_pharmacy = sorted(
        [v for v in pharm_risk_map.values() if v["near_expiry_batches"] > 0],
        key=lambda x: x["near_expiry_value"],
        reverse=True
    )[:10]

    value_saved_by_category = [
        {"category": k, "value_saved": round(v, 2)}
        for k, v in sorted(cat_saved_map.items(), key=lambda x: x[1], reverse=True)[:8]
    ]

    return AnalyticsDashboardOut(
        total_inventory_value=round(total_inv_val, 2),
        near_expiry_stock_value=round(near_exp_val, 2),
        high_risk_batches_count=high_risk_count,
        potential_value_saved=round(potential_saved, 2),
        value_successfully_transferred=round(val_transferred, 2),
        value_used_before_expiry=round(value_used_locally, 2),
        stock_lost_to_expiry=round(stock_lost, 2),
        total_recommendations=total_recs,
        pending_recommendations=pending_recs,
        approved_recommendations=approved_recs,
        rejected_recommendations=rejected_recs,
        overridden_recommendations=overridden_recs,
        approval_rate_pct=round(approval_rate, 1),
        rejection_rate_pct=round(rejection_rate, 1),
        override_rate_pct=round(override_rate, 1),
        risk_distribution=risk_dist,
        near_expiry_by_pharmacy=near_expiry_by_pharmacy,
        value_saved_by_category=value_saved_by_category,
        recommendations_by_status=rec_status_dist
    )
