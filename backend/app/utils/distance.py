"""
Geographic distance and transit estimation calculations.
"""

import math

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates the great-circle distance between two points on the Earth surface in kilometers."""
    R = 6371.0 # Earth's radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2.0)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 2)

def estimate_transit_days(distance_km: float) -> int:
    """
    Estimates realistic logistics transit duration:
    - Distance < 15 km: 1 day
    - Distance 15-35 km: 2 days
    - Distance > 35 km: 3 days
    """
    if distance_km < 15.0:
        return 1
    elif distance_km <= 35.0:
        return 2
    else:
        return 3

def estimate_transfer_cost(distance_km: float, quantity: int = 50) -> float:
    """Calculates courier cost based on distance and quantity."""
    base_cost = 50.0 # Base dispatch charge in INR
    distance_cost = distance_km * 4.5
    weight_cost = (quantity / 50.0) * 15.0
    return round(base_cost + distance_cost + weight_cost, 2)
