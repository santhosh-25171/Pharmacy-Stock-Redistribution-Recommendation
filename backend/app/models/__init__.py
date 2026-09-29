"""
Database Models definitions.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
)
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="PHARMACIST") # ADMIN, MANAGER, PHARMACIST
    assigned_pharmacy_id = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    actions = relationship("TransferAction", back_populates="user")
    overrides = relationship("OverrideReason", back_populates="user")

class Pharmacy(Base):
    __tablename__ = "pharmacies"

    id = Column(Integer, primary_key=True, index=True)
    pharmacy_id = Column(String(50), unique=True, index=True, nullable=False)
    pharmacy_name = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    storage_capacity = Column(Integer, nullable=False, default=5000)
    operating_status = Column(String(50), nullable=False, default="ACTIVE") # ACTIVE, MAINTENANCE, CLOSED
    created_at = Column(DateTime, default=datetime.utcnow)

    inventory_batches = relationship("InventoryBatch", back_populates="pharmacy")

class Medicine(Base):
    __tablename__ = "medicines"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    unit_price = Column(Float, nullable=False)
    is_critical = Column(Boolean, default=False)
    storage_type = Column(String(100), default="Room Temperature")
    created_at = Column(DateTime, default=datetime.utcnow)

    inventory_batches = relationship("InventoryBatch", back_populates="medicine")

class InventoryBatch(Base):
    __tablename__ = "inventory_batches"

    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(String(50), unique=True, index=True, nullable=False)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    medicine_name = Column(String(255), nullable=False)
    medicine_category = Column(String(100), nullable=False)
    batch_id = Column(String(100), nullable=False, index=True)
    pharmacy_id = Column(String(50), ForeignKey("pharmacies.pharmacy_id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    expiry_date = Column(String(50), nullable=False, index=True)
    received_date = Column(String(50), nullable=False)
    stock_status = Column(String(50), nullable=False, default="AVAILABLE") # AVAILABLE, NEAR_EXPIRY, EXPIRED
    edge_case_tag = Column(String(100), default="NONE")
    created_at = Column(DateTime, default=datetime.utcnow)

    medicine = relationship("Medicine", back_populates="inventory_batches")
    pharmacy = relationship("Pharmacy", back_populates="inventory_batches")
    recommendations = relationship("TransferRecommendation", back_populates="inventory_batch")

class DemandForecast(Base):
    __tablename__ = "demand_forecasts"

    id = Column(Integer, primary_key=True, index=True)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False, index=True)
    pharmacy_id = Column(String(50), ForeignKey("pharmacies.pharmacy_id"), nullable=False, index=True)
    daily_demand = Column(Float, nullable=False, default=1.0)
    weekly_demand = Column(Float, nullable=False, default=7.0)
    monthly_demand = Column(Float, nullable=False, default=30.0)
    historical_demand = Column(Float, nullable=False, default=30.0)
    demand_trend = Column(String(50), default="STABLE") # STABLE, INCREASING, DECREASING, VOLATILE, ZERO
    ml_predicted_demand = Column(Float, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TransferRecommendation(Base):
    __tablename__ = "transfer_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(String(50), unique=True, index=True, nullable=False)
    inventory_id = Column(String(50), ForeignKey("inventory_batches.inventory_id"), nullable=False)
    batch_id = Column(String(100), nullable=False)
    medicine_id = Column(String(50), ForeignKey("medicines.medicine_id"), nullable=False)
    medicine_name = Column(String(255), nullable=False)
    source_pharmacy_id = Column(String(50), ForeignKey("pharmacies.pharmacy_id"), nullable=False, index=True)
    destination_pharmacy_id = Column(String(50), ForeignKey("pharmacies.pharmacy_id"), nullable=False, index=True)
    source_pharmacy_name = Column(String(255), nullable=False)
    destination_pharmacy_name = Column(String(255), nullable=False)
    
    recommended_quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    potential_value_saved = Column(Float, nullable=False)
    days_to_expiry = Column(Integer, nullable=False)
    distance_km = Column(Float, nullable=False)
    estimated_transit_days = Column(Integer, nullable=False)
    
    risk_level = Column(String(50), nullable=False) # CRITICAL, HIGH, MEDIUM, LOW
    confidence_score = Column(Float, nullable=False, default=0.85) # Preserved for backward compatibility
    recommendation_score = Column(Float, nullable=True) # Normalized 0-100 explainable ranking score
    predicted_demand = Column(Float, nullable=True) # ML predicted destination demand
    demand_source = Column(String(50), default="ML_PREDICTION") # ML_PREDICTION, STORED_FORECAST, HEURISTIC_FALLBACK
    status = Column(String(50), nullable=False, default="PENDING") # PENDING, APPROVED, REJECTED, OVERRIDDEN, COMPLETED, CANCELLED
    is_high_impact = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    inventory_batch = relationship("InventoryBatch", back_populates="recommendations")
    evidence = relationship("RecommendationEvidence", back_populates="recommendation", cascade="all, delete-orphan")
    actions = relationship("TransferAction", back_populates="recommendation")
    override = relationship("OverrideReason", back_populates="recommendation", uselist=False)

class RecommendationEvidence(Base):
    __tablename__ = "recommendation_evidence"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(String(50), ForeignKey("transfer_recommendations.recommendation_id"), nullable=False, index=True)
    evidence_bullet = Column(String(500), nullable=False)
    metric_name = Column(String(100), nullable=True)
    metric_value = Column(String(100), nullable=True)

    recommendation = relationship("TransferRecommendation", back_populates="evidence")

class TransferAction(Base):
    __tablename__ = "transfer_actions"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(String(50), ForeignKey("transfer_recommendations.recommendation_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action_type = Column(String(50), nullable=False) # APPROVED, REJECTED, OVERRIDDEN, COMPLETED, CANCELLED
    transferred_quantity = Column(Integer, nullable=False)
    action_timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    recommendation = relationship("TransferRecommendation", back_populates="actions")
    user = relationship("User", back_populates="actions")

class OverrideReason(Base):
    __tablename__ = "override_reasons"

    id = Column(Integer, primary_key=True, index=True)
    recommendation_id = Column(String(50), ForeignKey("transfer_recommendations.recommendation_id"), unique=True, nullable=False)
    reason_category = Column(String(150), nullable=False)
    custom_reason = Column(Text, nullable=True)
    overridden_quantity = Column(Integer, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    recommendation = relationship("TransferRecommendation", back_populates="override")
    user = relationship("User", back_populates="overrides")

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    user_email = Column(String(255), nullable=False)
    user_role = Column(String(50), nullable=False)
    recommendation_id = Column(String(50), nullable=True, index=True)
    action = Column(String(50), nullable=False) # GENERATED, VIEWED, APPROVED, REJECTED, OVERRIDDEN, COMPLETED, CANCELLED, SEEDED
    previous_state = Column(String(50), nullable=True)
    new_state = Column(String(50), nullable=True)
    quantity = Column(Integer, nullable=True)
    source_pharmacy_id = Column(String(50), nullable=True)
    destination_pharmacy_id = Column(String(50), nullable=True)
    reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
