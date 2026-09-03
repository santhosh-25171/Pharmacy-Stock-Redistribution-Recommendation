"""
Pydantic Schemas for API validation and serialization.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    user: "UserOut"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str
    role: str
    assigned_pharmacy_id: Optional[str] = None
    is_active: bool

# --- Pharmacy Schemas ---
class PharmacyOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    pharmacy_id: str
    pharmacy_name: str
    city: str
    latitude: float
    longitude: float
    storage_capacity: int
    operating_status: str

class PharmacyDetailOut(PharmacyOut):
    total_batches: int = 0
    total_stock_value: float = 0.0
    near_expiry_count: int = 0
    near_expiry_value: float = 0.0
    critical_risk_count: int = 0
    incoming_transfers_count: int = 0
    outgoing_transfers_count: int = 0

# --- Medicine Schemas ---
class MedicineOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    medicine_id: str
    name: str
    category: str
    unit_price: float
    is_critical: bool
    storage_type: str

# --- Inventory Schemas ---
class InventoryBatchOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventory_id: str
    medicine_id: str
    medicine_name: str
    medicine_category: str
    batch_id: str
    pharmacy_id: str
    pharmacy_name: Optional[str] = None
    quantity: int
    unit_price: float
    total_value: float
    expiry_date: str
    days_to_expiry: int
    received_date: str
    stock_status: str
    risk_level: str
    daily_demand: float = 0.0
    days_to_consume: float = 0.0
    excess_quantity: int = 0
    recommended_action: str
    edge_case_tag: Optional[str] = "NONE"

# --- Recommendation Schemas ---
class EvidenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = None
    evidence_bullet: str
    metric_name: Optional[str] = None
    metric_value: Optional[str] = None

class OverrideReasonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    reason_category: str
    custom_reason: Optional[str] = None
    overridden_quantity: Optional[int] = None
    user_id: int
    created_at: datetime

class RecommendationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    recommendation_id: str
    inventory_id: str
    batch_id: str
    medicine_id: str
    medicine_name: str
    source_pharmacy_id: str
    source_pharmacy_name: str
    destination_pharmacy_id: str
    destination_pharmacy_name: str
    recommended_quantity: int
    unit_price: float
    potential_value_saved: float
    days_to_expiry: int
    distance_km: float
    estimated_transit_days: int
    risk_level: str
    confidence_score: float
    status: str
    is_high_impact: bool
    created_at: datetime
    evidence: List[EvidenceOut] = []
    override: Optional[OverrideReasonOut] = None

class ApproveRequest(BaseModel):
    notes: Optional[str] = None
    confirmed_high_impact: bool = False

class RejectRequest(BaseModel):
    reason_category: str
    custom_reason: Optional[str] = None

class OverrideRequest(BaseModel):
    reason_category: str
    custom_reason: Optional[str] = None
    overridden_quantity: int

class GenerateRecommendationsRequest(BaseModel):
    force_regenerate: bool = False

# --- Analytics Schemas ---
class AnalyticsDashboardOut(BaseModel):
    total_inventory_value: float
    near_expiry_stock_value: float
    high_risk_batches_count: int
    potential_value_saved: float
    value_successfully_transferred: float
    value_used_before_expiry: float
    stock_lost_to_expiry: float
    total_recommendations: int
    pending_recommendations: int
    approved_recommendations: int
    rejected_recommendations: int
    overridden_recommendations: int
    approval_rate_pct: float
    rejection_rate_pct: float
    override_rate_pct: float
    risk_distribution: Dict[str, int]
    near_expiry_by_pharmacy: List[Dict[str, Any]]
    value_saved_by_category: List[Dict[str, Any]]
    recommendations_by_status: Dict[str, int]

# --- Evaluation & Baseline Schemas ---
class ScenarioOut(BaseModel):
    scenario_id: str
    demand_multiplier: float
    baseline_value_used: float
    baseline_value_lost: float
    proposed_value_used_local: float
    proposed_value_transferred: float
    proposed_total_protected: float
    proposed_value_lost: float
    value_improvement: float
    improvement_pct: float
    recommendations_count: int
    accepted_count: int
    rejected_count: int
    overridden_count: int
    avg_transfer_distance_km: float
    avg_remaining_shelf_life_days: float

class EvaluationOut(BaseModel):
    num_scenarios: int
    summary: Dict[str, Any]
    scenarios: List[ScenarioOut]
    ml_metrics: Optional[Dict[str, Any]] = None

# --- Audit Log Schemas ---
class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: Optional[int] = None
    user_email: str
    user_role: str
    recommendation_id: Optional[str] = None
    action: str
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    quantity: Optional[int] = None
    source_pharmacy_id: Optional[str] = None
    destination_pharmacy_id: Optional[str] = None
    reason: Optional[str] = None
    timestamp: datetime

# --- Edge Case Schemas ---
class EdgeCaseOut(BaseModel):
    case_number: int
    title: str
    description: str
    batch_tag: str
    expected_result: str
    actual_system_behavior: str
    safety_rule_applied: str
    is_blocked: bool
