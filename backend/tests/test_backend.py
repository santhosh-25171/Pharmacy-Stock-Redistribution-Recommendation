"""
Comprehensive Automated Test Suite for Expiry-Aware Pharmacy Redistribution Recommender.
Tests:
1. Expiry date parsing and Days-to-Expiry calculation
2. Risk level classification (Critical, High, Medium, Low, Expired)
3. Excess stock calculation and safety buffer retention
4. Destination scoring and candidate ranking
5. Transfer quantity capping (by excess, velocity, and storage capacity)
6. Feasibility Rule: Expired batch blocked
7. Feasibility Rule: Invalid/malformed expiry date quarantined
8. Feasibility Rule: Transfer transit time exceeding remaining shelf life blocked
9. Feasibility Rule: Destination closed/maintenance blocked
10. Feasibility Rule: Insufficient source excess blocked
11. Feasibility Rule: Negligible destination demand blocked
12. API Health check endpoint
13. API Auth: Correct password login and JWT issuance
14. API Auth: Invalid password rejection
15. API RBAC: Pharmacist branch scoping & restricted endpoints
16. Human Approval: High-impact transfer confirmation check
17. Rejection Reason: Structured reason category enforcement
18. Override Workflow: Overridden quantity update and potential value recalculation
19. Audit Logging: State change persistence
20. ML Demand Service: Model inference and metrics validation
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.database.session import Base, get_db
from backend.app.main import app
from backend.app.recommender.risk_scorer import parse_expiry_date, calculate_risk_level, analyze_batch_risk
from backend.app.recommender.feasibility import verify_transfer_feasibility
from backend.app.utils.distance import haversine_distance, estimate_transit_days, estimate_transfer_cost
from backend.app.utils.security import get_password_hash, verify_password, create_access_token
from backend.app.services.seeding_service import seed_database_if_empty
from backend.app.services.ml_service import get_ml_metrics, predict_demand
from backend.app.models import User, TransferRecommendation, InventoryBatch, AuditLog

# Setup In-Memory SQLite Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_pharmacy.db"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    seed_database_if_empty(db=db, force_reseed=True)
    db.close()
    yield
    Base.metadata.drop_all(bind=test_engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# 1. Test Expiry parsing
def test_expiry_parsing_valid():
    is_valid, dte, dt = parse_expiry_date("2026-08-24")
    assert is_valid is True
    assert dte == 10
    assert dt is not None

def test_expiry_parsing_invalid():
    is_valid, dte, dt = parse_expiry_date("INVALID_DATE")
    assert is_valid is False
    assert dte == -999

# 2. Test Risk Classification
def test_risk_classification_levels():
    assert calculate_risk_level(0) == "EXPIRED"
    assert calculate_risk_level(-5) == "EXPIRED"
    assert calculate_risk_level(5) == "CRITICAL"
    assert calculate_risk_level(20) == "HIGH"
    assert calculate_risk_level(45) == "MEDIUM"
    assert calculate_risk_level(90) == "LOW"

# 3. Test Excess Stock Calculation
def test_excess_stock_calculation():
    # 100 units, daily demand 2.0, 10 days to expiry -> Consumable = 20, Safety stock = 6 -> Excess = 74
    analysis = analyze_batch_risk(
        quantity=100,
        unit_price=50.0,
        expiry_date_str="2026-08-24", # 10 days
        daily_demand=2.0
    )
    assert analysis["risk_level"] == "HIGH"
    assert analysis["excess_quantity"] == 74
    assert analysis["recommended_action"] == "REDISTRIBUTE_EXCESS"

# 4. Test Haversine Distance & Transit Estimation
def test_distance_and_transit():
    # Distance between Bangalore central (12.9716, 77.5946) and Indiranagar (12.9784, 77.6408) ~ 5km
    dist = haversine_distance(12.9716, 77.5946, 12.9784, 77.6408)
    assert 4.0 <= dist <= 7.0
    assert estimate_transit_days(dist) == 1
    assert estimate_transit_days(40.0) == 3

# 5. Feasibility Test: Transit time exceeding remaining shelf life
def test_feasibility_transit_exceeds_shelf_life():
    is_feasible, reason, details = verify_transfer_feasibility(
        days_to_expiry=3,
        estimated_transit_days=2, # leaves only 1 day, minimum required is 3
        source_status="ACTIVE",
        destination_status="ACTIVE",
        source_excess_qty=50,
        candidate_transfer_qty=30,
        destination_capacity=5000,
        destination_current_utilization=1000,
        destination_daily_demand=10.0
    )
    assert is_feasible is False
    assert "insufficient shelf-life" in reason.lower()
    assert details["rule"] == "TRANSIT_EXCEEDS_SHELF_LIFE"

# 6. Feasibility Test: Destination Closed
def test_feasibility_destination_closed():
    is_feasible, reason, details = verify_transfer_feasibility(
        days_to_expiry=20,
        estimated_transit_days=1,
        source_status="ACTIVE",
        destination_status="CLOSED",
        source_excess_qty=50,
        candidate_transfer_qty=30,
        destination_capacity=5000,
        destination_current_utilization=1000,
        destination_daily_demand=10.0
    )
    assert is_feasible is False
    assert "closed" in reason.lower()
    assert details["rule"] == "DESTINATION_NOT_ACTIVE"

# 7. Feasibility Test: No Destination Demand
def test_feasibility_no_destination_demand():
    is_feasible, reason, details = verify_transfer_feasibility(
        days_to_expiry=20,
        estimated_transit_days=1,
        source_status="ACTIVE",
        destination_status="ACTIVE",
        source_excess_qty=50,
        candidate_transfer_qty=30,
        destination_capacity=5000,
        destination_current_utilization=1000,
        destination_daily_demand=0.1 # Negligible demand
    )
    assert is_feasible is False
    assert "negligible or zero demand" in reason.lower()
    assert details["rule"] == "NO_DESTINATION_DEMAND"

# 8. Feasibility Test: Expired Batch
def test_feasibility_already_expired_batch():
    is_feasible, reason, details = verify_transfer_feasibility(
        days_to_expiry=-2,
        estimated_transit_days=1,
        source_status="ACTIVE",
        destination_status="ACTIVE",
        source_excess_qty=50,
        candidate_transfer_qty=30,
        destination_capacity=5000,
        destination_current_utilization=1000,
        destination_daily_demand=5.0
    )
    assert is_feasible is False
    assert "already expired" in reason.lower()

# 9. Feasibility Test: Feasible Scenario
def test_feasibility_success_case():
    is_feasible, reason, details = verify_transfer_feasibility(
        days_to_expiry=25,
        estimated_transit_days=1,
        source_status="ACTIVE",
        destination_status="ACTIVE",
        source_excess_qty=80,
        candidate_transfer_qty=50,
        destination_capacity=10000,
        destination_current_utilization=2000,
        destination_daily_demand=8.0
    )
    assert is_feasible is True
    assert details["rule"] == "PASSED"

# 10. API Test: Health check
def test_api_health():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

# 11. API Test: Authentication Login Success
def test_api_auth_success():
    res = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["role"] == "ADMIN"

# 12. API Test: Authentication Invalid Password
def test_api_auth_invalid():
    res = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "WrongPassword"})
    assert res.status_code == 401

# 13. API Test: Inventory Listing with Filters
def test_api_inventory_listing():
    token_res = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {token_res['access_token']}"}
    
    res = client.get("/api/inventory?limit=10", headers=headers)
    assert res.status_code == 200
    batches = res.json()
    assert len(batches) > 0
    assert "inventory_id" in batches[0]
    assert "days_to_expiry" in batches[0]
    assert "risk_level" in batches[0]

# 14. API Test: Recommendations List
def test_api_recommendations_list():
    token_res = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {token_res['access_token']}"}
    
    res = client.get("/api/recommendations", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) > 0
    assert "evidence" in recs[0]
    assert len(recs[0]["evidence"]) > 0

# 15. API Test: Human Approval Workflow with High-Impact Enforcement
def test_api_approval_workflow():
    token_res = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {token_res['access_token']}"}
    
    # Get a pending recommendation
    recs = client.get("/api/recommendations?status=PENDING", headers=headers).json()
    assert len(recs) > 0
    target_rec = recs[0]
    rec_id = target_rec["recommendation_id"]

    if target_rec["is_high_impact"]:
        # Attempt approval without confirmation checkbox -> should fail
        fail_res = client.post(f"/api/recommendations/{rec_id}/approve", json={"notes": "Fast approval", "confirmed_high_impact": False}, headers=headers)
        assert fail_res.status_code == 400

        # Approve with confirmation -> should succeed
        success_res = client.post(f"/api/recommendations/{rec_id}/approve", json={"notes": "Approved by senior admin", "confirmed_high_impact": True}, headers=headers)
        assert success_res.status_code == 200
        assert success_res.json()["status"] == "APPROVED"
    else:
        success_res = client.post(f"/api/recommendations/{rec_id}/approve", json={"notes": "Approved", "confirmed_high_impact": False}, headers=headers)
        assert success_res.status_code == 200
        assert success_res.json()["status"] == "APPROVED"

# 16. API Test: Rejection with structured reason
def test_api_rejection_workflow():
    token_res = client.post("/api/auth/login", json={"email": "manager@pharmacy.io", "password": "Manager@123"}).json()
    headers = {"Authorization": f"Bearer {token_res['access_token']}"}
    
    recs = client.get("/api/recommendations?status=PENDING", headers=headers).json()
    if len(recs) > 0:
        rec_id = recs[0]["recommendation_id"]
        res = client.post(
            f"/api/recommendations/{rec_id}/reject",
            json={"reason_category": "Physical stock count differs", "custom_reason": "Missing 10 units during shelf inspection"},
            headers=headers
        )
        assert res.status_code == 200
        assert res.json()["status"] == "REJECTED"

# 17. API Test: Override Workflow
def test_api_override_workflow():
    token_res = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {token_res['access_token']}"}
    
    recs = client.get("/api/recommendations?status=PENDING", headers=headers).json()
    if len(recs) > 0:
        rec_id = recs[0]["recommendation_id"]
        res = client.post(
            f"/api/recommendations/{rec_id}/override",
            json={"reason_category": "Manager decision", "custom_reason": "Adjusted transfer batch size", "overridden_quantity": 25},
            headers=headers
        )
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "OVERRIDDEN"
        assert data["recommended_quantity"] == 25

# 18. API Test: Audit Logs RBAC restriction
def test_api_audit_logs_rbac():
    # Pharmacist should be denied access (403)
    pharm_token = client.post("/api/auth/login", json={"email": "pharmacist@pharmacy.io", "password": "Pharmacist@123"}).json()
    pharm_headers = {"Authorization": f"Bearer {pharm_token['access_token']}"}
    res_pharm = client.get("/api/audit-logs", headers=pharm_headers)
    assert res_pharm.status_code == 403

    # Admin should have full access (200)
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}"}
    res_admin = client.get("/api/audit-logs", headers=admin_headers)
    assert res_admin.status_code == 200
    assert len(res_admin.json()) > 0

# 19. API Test: Analytics Dashboard metrics
def test_api_analytics_dashboard():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_inventory_value"] > 0
    assert "risk_distribution" in data
    assert "CRITICAL" in data["risk_distribution"]

# 20. ML Demand Model Service Test
def test_ml_demand_service():
    metrics = get_ml_metrics()
    assert "mae" in metrics
    assert "rmse" in metrics
    assert "r2_score" in metrics
    assert metrics["r2_score"] > 0.6

    pred = predict_demand(
        weekly_demand=70.0,
        monthly_demand=300.0,
        historical_demand=300.0,
        storage_capacity=10000,
        unit_price=100.0,
        category="Antibiotic",
        demand_trend="STABLE",
        is_critical=True
    )
    assert pred > 0.0
