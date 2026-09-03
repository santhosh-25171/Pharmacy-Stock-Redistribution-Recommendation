"""
Risk Scoring and Expiry Analysis Module.
Calculates Days-to-Expiry (DTE), estimated local consumption, excess stock, and risk category.
"""

from datetime import datetime
from typing import Dict, Any, Tuple

REFERENCE_DATE = datetime(2026, 8, 14)

def parse_expiry_date(expiry_date_str: str) -> Tuple[bool, int, datetime]:
    """
    Parses expiry date string.
    Returns: (is_valid, days_to_expiry, parsed_datetime)
    """
    if not expiry_date_str or expiry_date_str == "INVALID_DATE":
        return False, -999, None
    try:
        dt = datetime.strptime(expiry_date_str.strip(), "%Y-%m-%d")
        dte = (dt - REFERENCE_DATE).days
        return True, dte, dt
    except Exception:
        return False, -999, None

def calculate_risk_level(days_to_expiry: int, is_valid_date: bool = True) -> str:
    """
    Categorizes risk based on remaining days to expiry:
    - Invalid date: CRITICAL (Safety block)
    - <= 0 days: EXPIRED
    - 1 to 7 days: CRITICAL
    - 8 to 30 days: HIGH
    - 31 to 60 days: MEDIUM
    - > 60 days: LOW
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
    Comprehensive risk and consumption profile for an inventory batch.
    """
    is_valid, dte, _ = parse_expiry_date(expiry_date_str)
    
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
    safety_stock_required = int(safe_daily_demand * safety_stock_days)
    
    # Days needed to consume current stock at current local velocity
    days_to_consume = round(quantity / safe_daily_demand, 1)
    
    # How much will reasonably be consumed before the expiry date
    consumable_before_expiry = int(safe_daily_demand * dte)
    
    # Excess quantity = stock that will expire unconsumed if kept locally
    excess_quantity = max(0, quantity - consumable_before_expiry - safety_stock_required)
    
    total_val = round(quantity * unit_price, 2)
    at_risk_val = round(min(quantity, max(0, quantity - consumable_before_expiry)) * unit_price, 2)

    # Action suggestion
    if excess_quantity > 5 and dte > 3:
        recommended_action = "REDISTRIBUTE_EXCESS"
    elif risk_level in ["CRITICAL", "HIGH"] and excess_quantity > 0:
        recommended_action = "EXPEDITE_LOCAL_DISPENSING"
    elif risk_level == "LOW":
        recommended_action = "NORMAL_STOCK"
    else:
        recommended_action = "MONITOR_DEMAND"

    return {
        "is_valid_date": True,
        "days_to_expiry": dte,
        "risk_level": risk_level,
        "stock_status": "NEAR_EXPIRY" if dte <= 30 else "AVAILABLE",
        "daily_demand": daily_demand,
        "days_to_consume": days_to_consume,
        "excess_quantity": excess_quantity,
        "safety_stock_required": safety_stock_required,
        "total_value": total_val,
        "at_risk_value": at_risk_val,
        "recommended_action": recommended_action
    }
