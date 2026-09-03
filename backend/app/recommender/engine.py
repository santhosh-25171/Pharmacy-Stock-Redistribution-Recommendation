"""
Explainable Expiry-Aware Recommendation Engine.
Orchestrates candidate destination discovery, ranking, quantity optimization,
human-in-the-loop impact evaluation, and factual evidence generation.
"""

import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models import (
    InventoryBatch, Pharmacy, Medicine, DemandForecast,
    TransferRecommendation, RecommendationEvidence
)
from backend.app.recommender.risk_scorer import analyze_batch_risk
from backend.app.recommender.feasibility import verify_transfer_feasibility
from backend.app.utils.distance import haversine_distance, estimate_transit_days

HIGH_IMPACT_VALUE_THRESHOLD = 2000.0 # INR
HIGH_IMPACT_QTY_THRESHOLD = 50
HIGH_IMPACT_DTE_THRESHOLD = 14

def generate_recommendations_for_db(db: Session, force_regenerate: bool = False) -> List[TransferRecommendation]:
    """
    Generates and persists transfer recommendations for all risky inventory batches in the database.
    """
    if not force_regenerate:
        existing_recs = db.query(TransferRecommendation).all()
        if len(existing_recs) > 0:
            return existing_recs

    # Clear existing if force_regenerate
    db.query(RecommendationEvidence).delete()
    db.query(TransferRecommendation).delete()
    db.commit()

    # Load lookup datasets
    pharmacies = {p.pharmacy_id: p for p in db.query(Pharmacy).all()}
    medicines = {m.medicine_id: m for m in db.query(Medicine).all()}
    
    demand_records = db.query(DemandForecast).all()
    demand_map = {(d.pharmacy_id, d.medicine_id): d for d in demand_records}

    # Query inventory batches that have potential risk (e.g. status NEAR_EXPIRY or AVAILABLE)
    batches = db.query(InventoryBatch).all()

    created_recommendations = []

    for batch in batches:
        p_src = pharmacies.get(batch.pharmacy_id)
        med = medicines.get(batch.medicine_id)
        if not p_src or not med:
            continue

        demand_src = demand_map.get((batch.pharmacy_id, batch.medicine_id))
        daily_demand_src = demand_src.daily_demand if demand_src else 1.0

        # Step 1: Analyze Risk & Excess
        risk_profile = analyze_batch_risk(
            quantity=batch.quantity,
            unit_price=batch.unit_price,
            expiry_date_str=batch.expiry_date,
            daily_demand=daily_demand_src
        )

        dte = risk_profile["days_to_expiry"]
        excess_qty = risk_profile["excess_quantity"]
        risk_level = risk_profile["risk_level"]

        # Only generate recommendation if there is excess stock and valid shelf-life
        if excess_qty < 5 or dte < 4 or not risk_profile["is_valid_date"]:
            continue

        # Step 2: Search Candidate Destinations
        best_candidate = None
        best_score = -1.0

        for p_dest_id, p_dest in pharmacies.items():
            if p_dest_id == batch.pharmacy_id or p_dest.operating_status != "ACTIVE":
                continue

            demand_dest = demand_map.get((p_dest_id, batch.medicine_id))
            daily_demand_dest = demand_dest.daily_demand if demand_dest else 0.0

            if daily_demand_dest < 0.8:
                continue

            # Calculate distance and transit time
            dist_km = haversine_distance(p_src.latitude, p_src.longitude, p_dest.latitude, p_dest.longitude)
            transit_days = estimate_transit_days(dist_km)

            # Check consumable window at destination before batch expires
            remaining_shelf_life = dte - transit_days
            dest_consumable = int(daily_demand_dest * max(0, remaining_shelf_life))
            
            # Candidate transfer quantity capped by excess, destination demand velocity, and capacity
            candidate_qty = min(excess_qty, dest_consumable, int(p_dest.storage_capacity * 0.15))

            if candidate_qty < 5:
                continue

            # Check feasibility
            is_feasible, reason, details = verify_transfer_feasibility(
                days_to_expiry=dte,
                estimated_transit_days=transit_days,
                source_status=p_src.operating_status,
                destination_status=p_dest.operating_status,
                source_excess_qty=excess_qty,
                candidate_transfer_qty=candidate_qty,
                destination_capacity=p_dest.storage_capacity,
                destination_current_utilization=int(p_dest.storage_capacity * 0.6), # ~60% baseline utilization
                destination_daily_demand=daily_demand_dest,
                edge_case_tag=batch.edge_case_tag
            )

            if not is_feasible:
                continue

            # Explainable Ranking Score
            score = (daily_demand_dest * 12.0) + (remaining_shelf_life * 2.5) - (dist_km * 0.35)
            if med.is_critical:
                score += 20.0

            if score > best_score:
                best_score = score
                best_candidate = {
                    "destination": p_dest,
                    "quantity": candidate_qty,
                    "distance_km": dist_km,
                    "transit_days": transit_days,
                    "dest_demand": daily_demand_dest,
                    "remaining_shelf_life": remaining_shelf_life,
                    "dest_consumable": dest_consumable,
                    "score": round(score, 2)
                }

        if not best_candidate:
            continue

        # Step 3: Formulate Recommendation
        dest_pharm = best_candidate["destination"]
        rec_qty = best_candidate["quantity"]
        val_saved = round(rec_qty * batch.unit_price, 2)
        rec_id = f"REC-{uuid.uuid4().hex[:8].upper()}"

        # High Impact check
        is_high_impact = (
            val_saved >= HIGH_IMPACT_VALUE_THRESHOLD or
            rec_qty >= HIGH_IMPACT_QTY_THRESHOLD or
            dte <= HIGH_IMPACT_DTE_THRESHOLD or
            med.is_critical
        )

        rec = TransferRecommendation(
            recommendation_id=rec_id,
            inventory_id=batch.inventory_id,
            batch_id=batch.batch_id,
            medicine_id=batch.medicine_id,
            medicine_name=batch.medicine_name,
            source_pharmacy_id=p_src.pharmacy_id,
            destination_pharmacy_id=dest_pharm.pharmacy_id,
            source_pharmacy_name=p_src.pharmacy_name,
            destination_pharmacy_name=dest_pharm.pharmacy_name,
            recommended_quantity=rec_qty,
            unit_price=batch.unit_price,
            potential_value_saved=val_saved,
            days_to_expiry=dte,
            distance_km=best_candidate["distance_km"],
            estimated_transit_days=best_candidate["transit_days"],
            risk_level=risk_level,
            confidence_score=min(0.98, max(0.65, round(best_score / 150.0, 2))),
            status="PENDING",
            is_high_impact=is_high_impact,
            created_at=datetime.utcnow()
        )

        db.add(rec)
        db.flush()

        # Step 4: Generate Transparent, Factual Evidence Bullets
        evidence_items = [
            RecommendationEvidence(
                recommendation_id=rec_id,
                evidence_bullet=f"{dte} days remaining before expiry ({batch.expiry_date})",
                metric_name="DAYS_TO_EXPIRY",
                metric_value=str(dte)
            ),
            RecommendationEvidence(
                recommendation_id=rec_id,
                evidence_bullet=f"Source pharmacy has low velocity ({daily_demand_src:.1f} units/day) with {excess_qty} excess units",
                metric_name="SOURCE_EXCESS",
                metric_value=str(excess_qty)
            ),
            RecommendationEvidence(
                recommendation_id=rec_id,
                evidence_bullet=f"Destination ({dest_pharm.pharmacy_name}) has robust demand ({best_candidate['dest_demand']:.1f} units/day)",
                metric_name="DESTINATION_DEMAND",
                metric_value=f"{best_candidate['dest_demand']:.1f}/day"
            ),
            RecommendationEvidence(
                recommendation_id=rec_id,
                evidence_bullet=f"Destination is {best_candidate['distance_km']} km away with estimated transit of {best_candidate['transit_days']} day(s)",
                metric_name="TRANSIT_DISTANCE",
                metric_value=f"{best_candidate['distance_km']} km"
            ),
            RecommendationEvidence(
                recommendation_id=rec_id,
                evidence_bullet=f"Destination can consume ~{best_candidate['dest_consumable']} units in the {best_candidate['remaining_shelf_life']} days remaining post-transit",
                metric_name="DESTINATION_CAPACITY_WINDOW",
                metric_value=f"{best_candidate['dest_consumable']} units"
            ),
            RecommendationEvidence(
                recommendation_id=rec_id,
                evidence_bullet=f"Protects ₹{val_saved:,.2f} in medication stock value from expiration waste",
                metric_name="VALUE_PROTECTED",
                metric_value=f"₹{val_saved:,.2f}"
            )
        ]

        if is_high_impact:
            impact_reason = []
            if val_saved >= HIGH_IMPACT_VALUE_THRESHOLD:
                impact_reason.append(f"High stock value (≥ ₹{HIGH_IMPACT_VALUE_THRESHOLD:,.0f})")
            if rec_qty >= HIGH_IMPACT_QTY_THRESHOLD:
                impact_reason.append(f"Large volume transfer (≥ {HIGH_IMPACT_QTY_THRESHOLD} units)")
            if dte <= HIGH_IMPACT_DTE_THRESHOLD:
                impact_reason.append(f"Urgent expiry window (≤ {HIGH_IMPACT_DTE_THRESHOLD} days)")
            if med.is_critical:
                impact_reason.append("Critical life-saving medicine")

            evidence_items.append(
                RecommendationEvidence(
                    recommendation_id=rec_id,
                    evidence_bullet=f"HUMAN CONFIRMATION REQUIRED: {', '.join(impact_reason)}",
                    metric_name="HIGH_IMPACT_FLAG",
                    metric_value="TRUE"
                )
            )

        for ev in evidence_items:
            db.add(ev)

        created_recommendations.append(rec)

    db.commit()
    return created_recommendations
