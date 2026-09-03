"""
Operational and Safety Feasibility Verifier.
Enforces all core safety rules before any stock redistribution recommendation can be generated.
"""

from typing import Dict, Any, Tuple

# Minimum days remaining required AFTER transit is complete
MIN_REMAINING_SHELF_LIFE_POST_TRANSIT = 3

def verify_transfer_feasibility(
    days_to_expiry: int,
    estimated_transit_days: int,
    source_status: str,
    destination_status: str,
    source_excess_qty: int,
    candidate_transfer_qty: int,
    destination_capacity: int,
    destination_current_utilization: int,
    destination_daily_demand: float,
    edge_case_tag: str = "NONE"
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Validates whether a transfer is operationally, clinically, and safely feasible.
    Returns: (is_feasible, failure_reason, diagnostic_details)
    """
    # 1. Check valid positive shelf life
    if days_to_expiry <= 0:
        return False, "Medicine is already expired and cannot be transferred.", {"rule": "EXPIRED_BATCH"}

    # 2. Check operational status
    if source_status != "ACTIVE":
        return False, f"Source pharmacy is not active (Status: {source_status}).", {"rule": "SOURCE_NOT_ACTIVE"}

    if destination_status != "ACTIVE":
        return False, f"Destination pharmacy is closed or under maintenance (Status: {destination_status}).", {"rule": "DESTINATION_NOT_ACTIVE"}

    # 3. Check Transit duration vs Remaining Shelf Life
    remaining_shelf_life_after_transit = days_to_expiry - estimated_transit_days
    if remaining_shelf_life_after_transit < MIN_REMAINING_SHELF_LIFE_POST_TRANSIT:
        return False, (
            f"Transfer time ({estimated_transit_days} days) leaves insufficient shelf-life "
            f"({remaining_shelf_life_after_transit} days remaining, minimum required: {MIN_REMAINING_SHELF_LIFE_POST_TRANSIT} days)."
        ), {"rule": "TRANSIT_EXCEEDS_SHELF_LIFE"}

    # 4. Check Source excess quantity
    if source_excess_qty <= 0 or candidate_transfer_qty <= 0:
        return False, "Source pharmacy does not have sufficient excess stock above safety buffer.", {"rule": "INSUFFICIENT_EXCESS"}

    # 5. Check Destination demand
    if destination_daily_demand < 0.5:
        return False, "Destination pharmacy has negligible or zero demand for this medicine.", {"rule": "NO_DESTINATION_DEMAND"}

    # 6. Check Destination storage capacity
    available_capacity = destination_capacity - destination_current_utilization
    if candidate_transfer_qty > available_capacity:
        return False, f"Destination pharmacy lacks storage capacity (Available: {available_capacity}, Required: {candidate_transfer_qty}).", {"rule": "CAPACITY_EXCEEDED"}

    # 7. Check Edge Case deliberate overrides
    if edge_case_tag == "INVALID_EXPIRY_DATE":
        return False, "Expiry date is missing or corrupted. Stock quarantined.", {"rule": "INVALID_EXPIRY_DATE"}

    if edge_case_tag == "ALREADY_EXPIRED":
        return False, "Medicine batch is expired. Safety violation.", {"rule": "ALREADY_EXPIRED"}

    return True, "Transfer is fully feasible and safe.", {
        "remaining_shelf_life_after_transit": remaining_shelf_life_after_transit,
        "available_capacity": available_capacity,
        "rule": "PASSED"
    }
