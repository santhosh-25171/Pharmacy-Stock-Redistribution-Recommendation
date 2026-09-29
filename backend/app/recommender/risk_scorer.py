"""
Risk Scoring and Expiry Analysis Module.
Calculates Days-to-Expiry (DTE), estimated local consumption, excess stock, and risk category.
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any, Tuple, Optional

# Default deterministic reference date for synthetic benchmark evaluations
DEFAULT_REFERENCE_DATE_STR = "2026-08-14"

def get_reference_date() -> datetime:
    """
    Returns the active reference date for expiry calculation.
    
    Why: Synthetic datasets are generated around a benchmark reference epoch (2026-08-14).
    Allowing DEMO_REFERENCE_DATE environment variable configuration enables reproducible
    evaluation runs while simultaneously supporting live calendar dates in production.
    """
    ref_env = os.getenv("DEMO_REFERENCE_DATE", DEFAULT_REFERENCE_DATE_STR).strip()
    if ref_env.upper() in ["CURRENT", "CURRENT_DATE", "LIVE"]:
        now = datetime.now(timezone.utc)
        return datetime(now.year, now.month, now.day)
    try:
        return datetime.strptime(ref_env, "%Y-%m-%d")
    except Exception:
        return datetime(2026, 8, 14)

def get_reference_date_info() -> Dict[str, Any]:
    """Exposes reference date metadata for health monitoring and UI display."""
    ref_env = os.getenv("DEMO_REFERENCE_DATE", DEFAULT_REFERENCE_DATE_STR).strip()
    is_live = ref_env.upper() in ["CURRENT", "CURRENT_DATE", "LIVE"]
    ref_dt = get_reference_date()
    return {
        "reference_date": ref_dt.strftime("%Y-%m-%d"),
        "mode": "LIVE_CURRENT" if is_live else "FIXED_DEMO",
        "description": "Live calendar date" if is_live else "Deterministic synthetic benchmark reference date"
    }

REFERENCE_DATE = get_reference_date()

def parse_expiry_date(expiry_date_str: str, reference_date: Optional[datetime] = None) -> Tuple[bool, int, datetime]:
    """
    Parses expiry date string and computes integer days remaining (DTE).
    
    Why: Defensive string parsing prevents format errors (e.g., malformed legacy barcodes
    or corrupted CSV rows) from terminating the batch recommendation engine.
    """
    if not expiry_date_str or expiry_date_str == "INVALID_DATE":
        return False, -999, None
    try:
        dt = datetime.strptime(expiry_date_str.strip(), "%Y-%m-%d")
        ref_dt = reference_date or get_reference_date()
        dte = (dt - ref_dt).days
        return True, dte, dt
    except Exception:
        return False, -999, None

def calculate_risk_level(days_to_expiry: int, is_valid_date: bool = True) -> str:
    """
    Categorizes clinical risk based on remaining days to expiry:
    
    Why these clinical brackets:
    - Invalid date -> CRITICAL: Unknown shelf-life is treated with maximum caution.
    - <= 0 days -> EXPIRED: Requires immediate biological waste removal.
    - 1 to 7 days -> CRITICAL: Urgent intervention window; immediate transfer or dispensing.
    - 8 to 30 days -> HIGH: Primary target window for inter-branch redistribution.
    - 31 to 60 days -> MEDIUM: Monitored for proactive velocity matching.
    - > 60 days -> LOW: Routine inventory under standard FIFO.
    """
    if not is_valid_date:
        return "CRITICAL"
    if days_to_expiry <= 0:
        return "EXPIRED"
    elif days_to_expiry <= 7:
        return "CRITICAL"
    elif days_to_expiry <= 30:
        return "HIGH"
    elif days_to_expiry <= 60:
        return "MEDIUM"
    else:
        return "LOW"

def analyze_batch_risk(
    quantity: int,
    unit_price: float,
    expiry_date_str: str,
    daily_demand: float,
    safety_stock_days: int = 3
) -> Dict[str, Any]:
    """
    Generates comprehensive risk and consumption profile for an inventory batch.
    
    Why: Before any redistribution recommendation is made, the engine must distinguish
    between 'total stock' and 'excess stock'. If a branch has 10 units but dispenses 2 units/day
    with 10 days to expiry, all 10 will be consumed locally. Only stock exceeding projected
    local consumption plus a mandatory safety buffer constitutes redistributable excess.
    """
    is_valid, dte, _ = parse_expiry_date(expiry_date_str)
    
    # Handle corrupted or unparseable expiry dates safely
    if not is_valid:
        return {
            "is_valid_date": False,
            "days_to_expiry": -999,
            "risk_level": "CRITICAL",
            "stock_status": "INVALID_EXPIRY",
            "daily_demand": daily_demand,
            "days_to_consume": 0.0,
            "excess_quantity": 0,
            "safety_stock_required": 0,
            "total_value": round(quantity * unit_price, 2),
            "at_risk_value": round(quantity * unit_price, 2),
            "recommended_action": "QUARANTINE_INVALID_DATE"
        }

    # Handle already expired stock safely
    if dte <= 0:
        return {
            "is_valid_date": True,
            "days_to_expiry": dte,
            "risk_level": "EXPIRED",
            "stock_status": "EXPIRED",
            "daily_demand": daily_demand,
            "days_to_consume": 0.0,
            "excess_quantity": 0,
            "safety_stock_required": 0,
            "total_value": round(quantity * unit_price, 2),
            "at_risk_value": round(quantity * unit_price, 2),
            "recommended_action": "DISPOSE_EXPIRED_BATCH"
        }

    risk_level = calculate_risk_level(dte, True)
    safe_daily_demand = max(0.1, daily_demand)
    
    # Protect the source pharmacy's safety-stock requirement
    # before calculating the quantity available for transfer.
    safety_stock_required = int(safe_daily_demand * safety_stock_days)
    
    # Days needed to consume current stock at current local dispensing velocity
    days_to_consume = round(quantity / safe_daily_demand, 1)
    
    # Projected units consumed locally before the expiry cutoff
    consumable_before_expiry = int(safe_daily_demand * dte)
    
    # Excess quantity: Only stock that will expire unconsumed if kept locally
    # minus the reserved safety buffer is marked for transfer.
    excess_quantity = max(0, quantity - consumable_before_expiry - safety_stock_required)
    
    total_val = round(quantity * unit_price, 2)
    at_risk_val = round(min(quantity, max(0, quantity - consumable_before_expiry)) * unit_price, 2)

    # Action suggestion based on clinical risk and excess availability
    if excess_quantity > 5 and dte > 3:
        recommended_action = "REDISTRIBUTE_EXCESS"
    elif risk_level in ["CRITICAL", "HIGH"] and excess_quantity > 0:
        recommended_action = "EXPEDITE_LOCAL_DISPENSING"
    elif risk_level == "EXPIRED":
        recommended_action = "DISPOSE_EXPIRED_BATCH"
    else:
        recommended_action = "RETAIN_LOCAL_STOCK"

    return {
        "is_valid_date": True,
        "days_to_expiry": dte,
        "risk_level": risk_level,
        "stock_status": "EXPIRED" if dte <= 0 else ("NEAR_EXPIRY" if dte <= 30 else "AVAILABLE"),
        "daily_demand": round(daily_demand, 2),
        "days_to_consume": days_to_consume,
        "excess_quantity": excess_quantity,
        "safety_stock_required": safety_stock_required,
        "total_value": total_val,
        "at_risk_value": at_risk_val,
        "recommended_action": recommended_action
    }
