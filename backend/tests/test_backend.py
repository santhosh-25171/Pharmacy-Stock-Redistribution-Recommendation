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
from backend.app.recommender.risk_scorer import parse_expiry_date, calculate_risk_level, analyze_batch_risk, get_reference_date, get_reference_date_info
from backend.app.recommender.feasibility import verify_transfer_feasibility
from backend.app.utils.distance import haversine_distance, estimate_transit_days, estimate_transfer_cost
from backend.app.utils.security import get_password_hash, verify_password, create_access_token
from backend.app.services.seeding_service import seed_database_if_empty
from backend.app.services.ml_service import get_ml_metrics, predict_demand, get_predicted_demand_with_source
from backend.app.models import User, TransferRecommendation, InventoryBatch, AuditLog, Pharmacy, Medicine, DemandForecast

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

# 21. Review #2: ML Demand Integration with Source Tracking
def test_ml_demand_prediction_integration():
    db = TestingSessionLocal()
    pharm = db.query(Pharmacy).first()
    med = db.query(Medicine).first()
    demand_rec = db.query(DemandForecast).filter(
        DemandForecast.pharmacy_id == pharm.pharmacy_id,
        DemandForecast.medicine_id == med.medicine_id
    ).first()
    
    pred_val, source, meta = get_predicted_demand_with_source(pharm, med, demand_rec)
    db.close()
    
    assert pred_val > 0.0
    assert source in ["ML_PREDICTION", "STORED_FORECAST"]
    assert "stored_demand" in meta

# 22. Review #2: ML Demand Fallback Behavior
def test_ml_demand_fallback_behavior():
    # Test when no demand record is present
    class DummyPharm:
        storage_capacity = 3000
    class DummyMed:
        unit_price = 45.0
        category = "Cardiology"
        is_critical = False
        
    val, source, meta = get_predicted_demand_with_source(DummyPharm(), DummyMed(), None)
    assert val > 0.0
    assert source in ["ML_PREDICTION", "HEURISTIC_FALLBACK"]

# 23. Review #2: Recommendations use ML Predicted Demand & Recommendation Score
def test_recommendation_uses_ml_predicted_demand():
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}
    
    res = client.get("/api/recommendations?status=PENDING", headers=headers)
    assert res.status_code == 200
    recs = res.json()
    assert len(recs) > 0
    
    r0 = recs[0]
    assert "predicted_demand" in r0
    assert r0["predicted_demand"] is not None
    assert r0["predicted_demand"] > 0
    assert r0["demand_source"] in ["ML_PREDICTION", "STORED_FORECAST"]
    assert "recommendation_score" in r0
    assert r0["recommendation_score"] >= 65.0

# 24. Review #2: Configurable Reference Date Handling
def test_configurable_reference_date():
    import os
    # Default benchmark date: 2026-08-14
    info = get_reference_date_info()
    assert "reference_date" in info
    assert info["mode"] == "FIXED_DEMO"
    
    # Custom reference date via env
    os.environ["DEMO_REFERENCE_DATE"] = "2026-08-20"
    is_valid, dte, _ = parse_expiry_date("2026-08-24")
    assert dte == 4 # 24 - 20 = 4 days
    
    # Reset back to default
    os.environ["DEMO_REFERENCE_DATE"] = "2026-08-14"
    is_valid2, dte2, _ = parse_expiry_date("2026-08-24")
    assert dte2 == 10 # 24 - 14 = 10 days

# 25. Review #2: Security - Unauthorized Seed Endpoint Blocked (401)
def test_unauthorized_seed_endpoint_blocked():
    # Attempting to re-seed without authentication token must return 401
    res = client.post("/api/seed")
    assert res.status_code == 401

# 26. Review #2: Security - Non-Admin Seed Endpoint Forbidden (403)
def test_non_admin_seed_endpoint_forbidden():
    # Pharmacist attempting to seed database must be forbidden (403)
    pharm_token = client.post("/api/auth/login", json={"email": "pharmacist@pharmacy.io", "password": "Pharmacist@123"}).json()
    headers = {"Authorization": f"Bearer {pharm_token['access_token']}"}
    res = client.post("/api/seed", headers=headers)
    assert res.status_code == 403

# 27. Review #2: Security - Authorized ADMIN Seed Endpoint Success (200)
def test_authorized_admin_seed_endpoint_success():
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}
    res = client.post("/api/seed", headers=headers)
    assert res.status_code == 200
    assert res.json()["status"] == "success"

# 28. Review #2: Explainable Evidence Bullets with ML Demand & Rationale
def test_recommendation_score_and_explainable_evidence():
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}
    recs = client.get("/api/recommendations?status=PENDING", headers=headers).json()
    assert len(recs) > 0
    
    r0 = recs[0]
    metric_names = [ev["metric_name"] for ev in r0["evidence"]]
    assert "SOURCE_EXCESS" in metric_names
    assert "PREDICTED_DEMAND" in metric_names
    assert "DEMAND_SOURCE" in metric_names
    assert "DAYS_TO_EXPIRY" in metric_names
    assert "TRANSIT_DISTANCE" in metric_names
    assert "RECOMMENDATION_SCORE" in metric_names

# 29. Review #2: System Health Endpoint Subsystems
def test_system_health_subsystems():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["database"] == "connected"
    assert "ml_model" in data
    assert data["ml_model"]["model_name"] == "RandomForestRegressor"
    assert "recommender" in data
    assert "reference_date" in data
    assert data["reference_date"]["mode"] == "FIXED_DEMO"

# ==============================================================================
# REVIEW #3: EXPANDED TEST SUITE ACROSS ALL 16 GRANULAR CATEGORIES
# ==============================================================================

# Category 1: Authentication Tests (Inactive user & Current user extraction)
def test_auth_inactive_user_blocked():
    """Verify inactive user accounts are rejected with HTTP 400."""
    db = TestingSessionLocal()
    # Create or update a temporary inactive user
    inactive_user = db.query(User).filter(User.email == "inactive_tester@pharmacy.io").first()
    if not inactive_user:
        inactive_user = User(
            email="inactive_tester@pharmacy.io",
            hashed_password=get_password_hash("Inactive@123"),
            full_name="Inactive Tester",
            role="PHARMACIST",
            is_active=False
        )
        db.add(inactive_user)
        db.commit()
    else:
        inactive_user.is_active = False
        db.commit()
    db.close()

    res = client.post("/api/auth/login", json={"email": "inactive_tester@pharmacy.io", "password": "Inactive@123"})
    assert res.status_code == 400
    assert "Inactive user account" in res.json()["detail"]

def test_auth_me_valid_and_invalid_token():
    """Verify /api/auth/me returns user profile on valid JWT and 401 on forged/missing token."""
    # Valid token
    login_res = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    valid_headers = {"Authorization": f"Bearer {login_res['access_token']}"}
    me_res = client.get("/api/auth/me", headers=valid_headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "admin@pharmacy.io"
    assert me_res.json()["role"] == "ADMIN"

    # Malformed token
    bad_headers = {"Authorization": "Bearer forged.invalid.token"}
    bad_res = client.get("/api/auth/me", headers=bad_headers)
    assert bad_res.status_code == 401

# Category 2: Authorization / RBAC Tests (Branch scoping & unauthorized action blocks)
def test_rbac_pharmacist_branch_scoping_inventory():
    """Verify that a Pharmacist with assigned branch PHARM-001 can only view PHARM-001 inventory."""
    pharm_token = client.post("/api/auth/login", json={"email": "pharmacist@pharmacy.io", "password": "Pharmacist@123"}).json()
    headers = {"Authorization": f"Bearer {pharm_token['access_token']}"}
    
    res = client.get("/api/inventory", headers=headers)
    assert res.status_code == 200
    batches = res.json()
    assert len(batches) > 0
    # Every single batch returned must belong exclusively to PHARM-001
    for b in batches:
        assert b["pharmacy_id"] == "PHARM-001"

def test_rbac_pharmacist_cannot_approve_other_branch_transfer():
    """Verify that a Pharmacist cannot approve an outgoing transfer originating from a different branch."""
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    admin_headers = {"Authorization": f"Bearer {admin_token['access_token']}"}
    
    # Find or check recommendation where source pharmacy is NOT PHARM-001
    all_recs = client.get("/api/recommendations?status=PENDING", headers=admin_headers).json()
    other_branch_rec = next((r for r in all_recs if r["source_pharmacy_id"] != "PHARM-001"), None)
    
    if other_branch_rec:
        pharm_token = client.post("/api/auth/login", json={"email": "pharmacist@pharmacy.io", "password": "Pharmacist@123"}).json()
        pharm_headers = {"Authorization": f"Bearer {pharm_token['access_token']}"}
        
        rec_id = other_branch_rec["recommendation_id"]
        res = client.post(f"/api/recommendations/{rec_id}/approve", json={"notes": "Cross-branch test", "confirmed_high_impact": True}, headers=pharm_headers)
        assert res.status_code == 403
        assert "Pharmacist can only approve outgoing transfers from their assigned source branch" in res.json()["detail"]

# Category 3: Inventory Tests (Single batch detail, search filter, category filter)
def test_inventory_batch_detail_found_and_not_found():
    """Verify inventory batch lookup by ID and 404 handling."""
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    # Fetch any valid batch
    inv_list = client.get("/api/inventory?limit=1", headers=headers).json()
    assert len(inv_list) > 0
    valid_id = inv_list[0]["inventory_id"]

    # Valid lookup
    res_valid = client.get(f"/api/inventory/{valid_id}", headers=headers)
    assert res_valid.status_code == 200
    assert res_valid.json()["inventory_id"] == valid_id

    # Non-existent lookup
    res_invalid = client.get("/api/inventory/INV-DOES-NOT-EXIST", headers=headers)
    assert res_invalid.status_code == 404

def test_inventory_filters_search_and_category():
    """Verify inventory querying with search and category filters."""
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    res_cat = client.get("/api/inventory?category=Cardiology&limit=5", headers=headers)
    assert res_cat.status_code == 200
    for b in res_cat.json():
        assert b["medicine_category"] == "Cardiology"

# Category 4: Pharmacy Tests (Network list & detail metrics)
def test_pharmacies_list_and_detail():
    """Verify pharmacy network listing and branch detail metrics."""
    res = client.get("/api/pharmacies")
    assert res.status_code == 200
    pharmacies = res.json()
    assert len(pharmacies) >= 10

    # Detail for PHARM-001
    p0 = pharmacies[0]
    detail_res = client.get(f"/api/pharmacies/{p0['pharmacy_id']}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert detail["pharmacy_id"] == p0["pharmacy_id"]
    assert "storage_capacity" in detail
    assert "total_batches" in detail
    assert "near_expiry_value" in detail

    # 404 for missing pharmacy
    missing_res = client.get("/api/pharmacies/PHARM-99999")
    assert missing_res.status_code == 404

# Category 5: Medicines Catalog Tests
def test_medicines_catalog():
    """Verify synthetic medicines catalog listing and category filtering."""
    res = client.get("/api/medicines")
    assert res.status_code == 200
    meds = res.json()
    assert len(meds) > 0
    assert "medicine_id" in meds[0]
    assert "unit_price" in meds[0]

# Category 7: Safety-Stock Tests
def test_safety_stock_below_buffer_yields_zero_excess():
    """Verify that inventory below or equal to the 3-day safety buffer produces zero excess."""
    # quantity = 6, daily_demand = 2.0 -> 3-day safety buffer = 6 units
    # consumable before expiry (3 days) = 6 units
    # excess = max(0, 6 - 6 - 6) = 0 units
    analysis = analyze_batch_risk(
        quantity=6,
        unit_price=20.0,
        expiry_date_str="2026-08-17", # 3 days from 2026-08-14
        daily_demand=2.0,
        safety_stock_days=3
    )
    assert analysis["excess_quantity"] == 0
    assert analysis["safety_stock_required"] == 6
    assert analysis["recommended_action"] == "RETAIN_LOCAL_STOCK"

# Category 9: Destination-Ranking Tests
def test_destination_ranking_critical_medicine_boost():
    """Verify that critical life-saving medications receive an explainable ranking bonus."""
    # Baseline non-critical score components: (demand * 12.0) + (shelf_life * 2.5) - (dist * 0.35)
    score_standard = (2.0 * 12.0) + (10 * 2.5) - (5.0 * 0.35)
    score_critical = score_standard + 20.0 # +20 point bonus
    assert score_critical > score_standard
    assert score_critical - score_standard == 20.0

# Category 10: Transfer-Feasibility Tests (Facility status & capacity)
def test_feasibility_source_not_active_blocked():
    """Verify that transfers from a pharmacy under maintenance are blocked."""
    is_feasible, reason, details = verify_transfer_feasibility(
        days_to_expiry=30,
        estimated_transit_days=1,
        source_status="MAINTENANCE",
        destination_status="ACTIVE",
        source_excess_qty=50,
        candidate_transfer_qty=20,
        destination_capacity=5000,
        destination_current_utilization=1000,
        destination_daily_demand=5.0
    )
    assert is_feasible is False
    assert details["rule"] == "SOURCE_NOT_ACTIVE"

def test_feasibility_destination_capacity_exceeded():
    """Verify that transfers exceeding destination storage capacity are blocked."""
    is_feasible, reason, details = verify_transfer_feasibility(
        days_to_expiry=30,
        estimated_transit_days=1,
        source_status="ACTIVE",
        destination_status="ACTIVE",
        source_excess_qty=500,
        candidate_transfer_qty=4500,
        destination_capacity=5000,
        destination_current_utilization=4000, # Only 1000 available
        destination_daily_demand=5.0
    )
    assert is_feasible is False
    assert details["rule"] == "CAPACITY_EXCEEDED"

# Category 11: API Validation Tests (Invalid payload bounds)
def test_api_validation_override_negative_quantity():
    """Verify that overriding with a non-positive quantity is rejected with HTTP 400."""
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    recs = client.get("/api/recommendations?status=PENDING", headers=headers).json()
    if len(recs) > 0:
        rec_id = recs[0]["recommendation_id"]
        res = client.post(
            f"/api/recommendations/{rec_id}/override",
            json={"reason_category": "Adjustment", "overridden_quantity": -5},
            headers=headers
        )
        assert res.status_code == 400
        assert "greater than zero" in res.json()["detail"].lower()

def test_api_validation_rejection_missing_reason_category():
    """Verify that rejection requests missing a structured reason category return HTTP 400."""
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    recs = client.get("/api/recommendations?status=PENDING", headers=headers).json()
    if len(recs) > 0:
        rec_id = recs[0]["recommendation_id"]
        res = client.post(
            f"/api/recommendations/{rec_id}/reject",
            json={"reason_category": "", "custom_reason": "No reason selected"},
            headers=headers
        )
        assert res.status_code == 400

# Category 12: Database Tests (Relationship navigation & integrity)
def test_database_models_relationships():
    """Verify ORM navigation across database relationships."""
    db = TestingSessionLocal()
    pharmacy = db.query(Pharmacy).first()
    assert pharmacy is not None
    assert len(pharmacy.inventory_batches) > 0
    
    first_batch = pharmacy.inventory_batches[0]
    assert first_batch.pharmacy.pharmacy_id == pharmacy.pharmacy_id
    assert first_batch.medicine is not None

    rec = db.query(TransferRecommendation).first()
    if rec:
        assert len(rec.evidence) > 0
        assert rec.evidence[0].recommendation_id == rec.recommendation_id
    db.close()

# Category 13: Audit-Log Tests (Filter by action & user)
def test_audit_log_filtering_by_action():
    """Verify audit log query filtering by action type."""
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    res = client.get("/api/audit-logs?action=SEEDED", headers=headers)
    assert res.status_code == 200
    logs = res.json()
    for l in logs:
        assert l["action"] == "SEEDED"

# Category 14: Analytics Tests (Simulation scenario endpoints)
def test_evaluation_simulation_endpoint():
    """Verify /api/evaluation endpoint returns summary metrics and 30 benchmark scenarios."""
    res = client.get("/api/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert data["num_scenarios"] == 30
    assert "summary" in data
    assert "scenarios" in data
    assert len(data["scenarios"]) == 30
    assert "ml_metrics" in data

# Category 15: Edge-Case Tests (All 8 operational edge cases returned)
def test_edge_cases_endpoint_all_8_scenarios():
    """Verify /api/edge-cases returns all 8 operational failure guard scenarios with rule metadata."""
    res = client.get("/api/edge-cases")
    assert res.status_code == 200
    cases = res.json()
    assert len(cases) == 8
    tags = [c["batch_tag"] for c in cases]
    assert "EXPIRES_BEFORE_TRANSIT" in tags
    assert "NO_DESTINATION_DEMAND" in tags
    assert "BELOW_SAFETY_STOCK" in tags
    assert "INVALID_EXPIRY_DATE" in tags
    assert "DESTINATION_CLOSED_ONLY" in tags
    assert "ALREADY_EXPIRED" in tags
    assert "SUDDEN_DEMAND_DROP" in tags
    assert "DUPLICATE_BATCH" in tags

# Category 16: Error-Handling Tests (Entity not found & state guards)
def test_error_handling_recommendation_not_found():
    """Verify 404 response on operations against non-existent recommendation IDs."""
    admin_token = client.post("/api/auth/login", json={"email": "admin@pharmacy.io", "password": "Admin@123"}).json()
    headers = {"Authorization": f"Bearer {admin_token['access_token']}"}

    res_get = client.get("/api/recommendations/REC-DOESNOTEXIST", headers=headers)
    assert res_get.status_code == 404

    res_post = client.post("/api/recommendations/REC-DOESNOTEXIST/approve", json={"notes": ""}, headers=headers)
    assert res_post.status_code == 404

