# Comprehensive Testing & Verification Suite

This document provides technical documentation of the test pyramid, test execution procedures, and categorized test catalog for PharmaShift Review #3.

---

## 1. Test Pyramid & Verification Architecture

PharmaShift employs a multi-tiered test strategy to validate safety, clinical constraint satisfaction, and operational resilience:

```
                  ┌───────────────────────────────┐
                  │    End-to-End Demonstration   │  (Interactive 17-Step Review Flow)
                  ├───────────────────────────────┤
                  │   Frontend / Build Validation │  (Vite production compile, 0 errors)
                  ├───────────────────────────────┤
                  │           API Tests           │  (FastAPI TestClient endpoint assertions)
                  ├───────────────────────────────┤
                  │       Integration Tests       │  (DB ORM relationships, ML model inference)
                  ├───────────────────────────────┤
                  │          Unit Tests           │  (DTE math, risk levels, feasibility rules)
                  └───────────────────────────────┘
```

1. **Unit Tests**: Validate mathematical logic, Haversine formulas, date parsing, safety stock calculations, and individual feasibility rules in complete isolation.
2. **Integration Tests**: Verify interactions between SQLAlchemy models, SQLite/PostgreSQL databases, and scikit-learn ML model artifacts (`demand_model.joblib`).
3. **API Tests**: Execute HTTP requests against FastAPI routers via `fastapi.testclient.TestClient`, validating headers, status codes, JWT auth tokens, and response schemas.
4. **Frontend / Build Validation**: Asserts that all React 18 JSX components, Tailwind classes, and Vite asset bundles compile cleanly without syntax errors or broken dependencies.
5. **End-to-End Demonstration**: A structured 17-step operational walkthrough validating the user journey from Login to Recommendation Approval and Audit Trail logging.

---

## 2. Test Execution Summary

- **Framework**: `pytest 9.1.1` with `fastapi.testclient.TestClient`
- **Python Environment**: `Python 3.13.7` (Windows 64-bit)
- **Database Engine**: In-Memory / File SQLite (`test_pharmacy.db`) seeded with 5,193 synthetic batches across 18 pharmacies
- **Total Tests Executed**: **49**
- **Passing Tests**: **49 (100% Pass Rate)**
- **Failed Tests**: **0**
- **Execution Runtime**: **50.03 seconds**

---

## 3. Granular Test Catalog by Category

### Category 1: Authentication Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_api_auth_success` | Valid email `admin@pharmacy.io` and password `Admin@123` | `POST /api/auth/login` | HTTP 200, JWT token returned, `user.role == "ADMIN"` | HTTP 200, valid JWT issued | **PASS** |
| `test_api_auth_invalid` | Email `admin@pharmacy.io` with wrong password `WrongPassword` | `POST /api/auth/login` | HTTP 401 Unauthorized | HTTP 401 Unauthorized | **PASS** |
| `test_auth_inactive_user_blocked` | User with `is_active=False` attempting login | `POST /api/auth/login` | HTTP 400 Bad Request (`"Inactive user account"`) | HTTP 400 Bad Request | **PASS** |
| `test_auth_me_valid_and_invalid_token` | Valid Bearer token vs. `Bearer forged.invalid.token` | `GET /api/auth/me` | HTTP 200 for valid token; HTTP 401 for forged token | 200 (valid) / 401 (forged) | **PASS** |

---

### Category 2: Authorization & Role-Based Access Control (RBAC) Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_api_audit_logs_rbac` | Pharmacist credentials vs. Admin credentials | `GET /api/audit-logs` | Pharmacist receives HTTP 403 Forbidden; Admin receives HTTP 200 | Pharmacist 403 / Admin 200 | **PASS** |
| `test_non_admin_seed_endpoint_forbidden` | Pharmacist token attempting database reset | `POST /api/seed` | HTTP 403 Forbidden (`require_roles(["ADMIN"])`) | HTTP 403 Forbidden | **PASS** |
| `test_unauthorized_seed_endpoint_blocked` | Unauthenticated request (no JWT token) | `POST /api/seed` | HTTP 401 Unauthorized | HTTP 401 Unauthorized | **PASS** |
| `test_authorized_admin_seed_endpoint_success` | Admin token | `POST /api/seed` | HTTP 200, `{"status": "success"}` | HTTP 200 Success | **PASS** |
| `test_rbac_pharmacist_branch_scoping_inventory` | Pharmacist assigned to `PHARM-001` | `GET /api/inventory` | Batches returned belong strictly to `PHARM-001` | 100% of batches match `PHARM-001` | **PASS** |
| `test_rbac_pharmacist_cannot_approve_other_branch_transfer` | Pharmacist (`PHARM-001`) approving transfer from `PHARM-002` | `POST /api/recommendations/{id}/approve` | HTTP 403 Forbidden | HTTP 403 Forbidden | **PASS** |

---

### Category 3: Inventory Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_api_inventory_listing` | `limit=10`, Admin token | `GET /api/inventory` | HTTP 200, list of 10 batches with DTE, risk level | HTTP 200, 10 records returned | **PASS** |
| `test_inventory_batch_detail_found_and_not_found` | Valid batch ID vs. `INV-DOES-NOT-EXIST` | `GET /api/inventory/{id}` | HTTP 200 with batch data for valid; HTTP 404 for invalid | 200 (valid) / 404 (invalid) | **PASS** |
| `test_inventory_filters_search_and_category` | `category=Cardiology&limit=5` | `GET /api/inventory` | HTTP 200, all returned batches have `medicine_category == "Cardiology"` | 100% match Cardiology | **PASS** |

---

### Category 4: Pharmacy Network Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_pharmacies_list_and_detail` | No params for list; `PHARM-001` for detail; `PHARM-99999` for missing | `GET /api/pharmacies`, `GET /api/pharmacies/{id}` | HTTP 200 with branches; HTTP 200 with storage capacity; HTTP 404 for missing | 200 (list) / 200 (detail) / 404 (missing) | **PASS** |

---

### Category 5: Demand & Machine Learning Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_ml_demand_service` | Standard 9-feature demand vector | `predict_demand(...)`, `get_ml_metrics()` | Returns predicted daily demand $> 0$; $R^2 > 0.60$ | Predicted demand 2.8 units/day; $R^2 = 0.7523$ | **PASS** |
| `test_ml_demand_prediction_integration` | Real Pharmacy and Medicine ORM objects | `get_predicted_demand_with_source(...)` | Value $> 0$, source in `['ML_PREDICTION', 'STORED_FORECAST']` | Predicted value returned with source tracked | **PASS** |
| `test_ml_demand_fallback_behavior` | Objects with missing demand forecast records | `get_predicted_demand_with_source(...)` | Graceful fallback to `HEURISTIC_FALLBACK`, no exception | Fallback value computed without crash | **PASS** |
| `test_medicines_catalog` | Default request | `GET /api/medicines` | HTTP 200, catalog of medicines with unit prices | HTTP 200, medicines catalog returned | **PASS** |

---

### Category 6: Expiry-Risk Classification Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_expiry_parsing_valid` | Date string `"2026-08-24"` against benchmark `2026-08-14` | `parse_expiry_date("2026-08-24")` | `(True, 10, datetime_obj)` | `is_valid=True, dte=10` | **PASS** |
| `test_expiry_parsing_invalid` | Malformed string `"INVALID_DATE"` | `parse_expiry_date("INVALID_DATE")` | `(False, -999, None)` | `is_valid=False, dte=-999` | **PASS** |
| `test_risk_classification_levels` | DTE values: `0, -5, 5, 20, 45, 90` | `calculate_risk_level(dte)` | Matches `EXPIRED, EXPIRED, CRITICAL, HIGH, MEDIUM, LOW` | Exact clinical match | **PASS** |
| `test_configurable_reference_date` | `DEMO_REFERENCE_DATE="2026-08-20"` | `parse_expiry_date("2026-08-24")` | DTE recalculates dynamically to $24 - 20 = 4$ days | `dte == 4` | **PASS** |

---

### Category 7: Safety-Stock Retention Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_excess_stock_calculation` | 100 units, daily demand 2.0, 10 days to expiry | `analyze_batch_risk(...)` | Consumable = 20, Safety stock = 6, Excess = 74 | `excess_quantity == 74` | **PASS** |
| `test_safety_stock_below_buffer_yields_zero_excess` | 6 units, daily demand 2.0 (needs 6 units safety buffer) | `analyze_batch_risk(...)` | Excess = 0, recommended action = `RETAIN_LOCAL_STOCK` | `excess_quantity == 0` | **PASS** |

---

### Category 8: Recommendation-Engine Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_api_recommendations_list` | Filter `status=PENDING` | `GET /api/recommendations` | HTTP 200, list of recommendations with evidence bullets | HTTP 200, recommendations populated | **PASS** |
| `test_recommendation_uses_ml_predicted_demand` | First recommendation record | `TransferRecommendation` inspection | `predicted_demand > 0`, `recommendation_score >= 65.0` | `predicted_demand` present, score 88.5/100 | **PASS** |
| `test_recommendation_score_and_explainable_evidence` | Generated recommendation evidence items | `RecommendationEvidence` query | Evidence contains `SOURCE_EXCESS`, `PREDICTED_DEMAND`, `RECOMMENDATION_SCORE` | All required metrics present | **PASS** |

---

### Category 9: Destination-Ranking Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_distance_and_transit` | Coordinates for Central Bangalore and Indiranagar | `haversine_distance(...)`, `estimate_transit_days(...)` | Distance $\approx 5.1$ km, transit = 1 day | Distance 5.12 km, 1 transit day | **PASS** |
| `test_destination_ranking_critical_medicine_boost` | Formula calculation comparing standard vs critical drug | `score` formula | Critical medicine receives +20 point bonus | Exact +20 point boost verified | **PASS** |

---

### Category 10: Transfer-Feasibility Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_feasibility_transit_exceeds_shelf_life` | DTE = 3 days, transit = 2 days (leaves only 1 day cushion) | `verify_transfer_feasibility(...)` | `is_feasible == False`, rule: `TRANSIT_EXCEEDS_SHELF_LIFE` | `False`, shelf-life failure | **PASS** |
| `test_feasibility_destination_closed` | Destination status `"CLOSED"` | `verify_transfer_feasibility(...)` | `is_feasible == False`, rule: `DESTINATION_NOT_ACTIVE` | `False`, destination closed | **PASS** |
| `test_feasibility_no_destination_demand` | Destination daily demand = 0.1 units/day | `verify_transfer_feasibility(...)` | `is_feasible == False`, rule: `NO_DESTINATION_DEMAND` | `False`, negligible demand | **PASS** |
| `test_feasibility_already_expired_batch` | DTE = -2 days | `verify_transfer_feasibility(...)` | `is_feasible == False`, rule: `EXPIRED_BATCH` | `False`, expired batch blocked | **PASS** |
| `test_feasibility_source_not_active_blocked` | Source status `"MAINTENANCE"` | `verify_transfer_feasibility(...)` | `is_feasible == False`, rule: `SOURCE_NOT_ACTIVE` | `False`, maintenance blocked | **PASS** |
| `test_feasibility_destination_capacity_exceeded` | Transfer qty 4,500 units against available 1,000 units | `verify_transfer_feasibility(...)` | `is_feasible == False`, rule: `CAPACITY_EXCEEDED` | `False`, capacity exceeded | **PASS** |
| `test_feasibility_success_case` | DTE = 25d, transit = 1d, excess = 80, candidate = 50 | `verify_transfer_feasibility(...)` | `is_feasible == True`, rule: `PASSED` | `True`, transfer feasible | **PASS** |

---

### Category 11: API Validation Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_api_validation_override_negative_quantity` | Overridden quantity = `-5` | `POST /api/recommendations/{id}/override` | HTTP 400 Bad Request (`"must be greater than zero"`) | HTTP 400 Bad Request | **PASS** |
| `test_api_validation_rejection_missing_reason_category` | Empty reason category `""` | `POST /api/recommendations/{id}/reject` | HTTP 400 Bad Request (`"reason category is mandatory"`) | HTTP 400 Bad Request | **PASS** |

---

### Category 12: Database Integrity Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_database_models_relationships` | Active session query | SQLAlchemy ORM navigation | `Pharmacy.inventory_batches` populated; `Recommendation.evidence` intact | All foreign key relations traversed | **PASS** |

---

### Category 13: Audit Trail Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_api_approval_workflow` | High-impact confirmation flag + notes | `POST /api/recommendations/{id}/approve` | Status transitions to `APPROVED`, audit log generated | HTTP 200, Audit entry created | **PASS** |
| `test_api_rejection_workflow` | Structured reason category + custom text | `POST /api/recommendations/{id}/reject` | Status transitions to `REJECTED`, audit log generated | HTTP 200, Audit entry created | **PASS** |
| `test_api_override_workflow` | Overridden quantity = 25 units | `POST /api/recommendations/{id}/override` | Status transitions to `OVERRIDDEN`, quantity & value recalculated | HTTP 200, Audit entry created | **PASS** |
| `test_audit_log_filtering_by_action` | Query `action=SEEDED` | `GET /api/audit-logs` | HTTP 200, all returned entries have `action == "SEEDED"` | 100% of logs match filter | **PASS** |

---

### Category 14: Analytics & Simulation Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_api_analytics_dashboard` | Standard request | `GET /api/analytics` | HTTP 200, KPIs calculated (`total_inventory_value > 0`, risk dist) | HTTP 200, metrics populated | **PASS** |
| `test_evaluation_simulation_endpoint` | Standard request | `GET /api/evaluation` | HTTP 200, `num_scenarios == 30`, summary metrics populated | HTTP 200, 30 scenarios loaded | **PASS** |

---

### Category 15: Operational Edge-Case Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_edge_cases_endpoint_all_8_scenarios` | Standard request | `GET /api/edge-cases` | HTTP 200, array of 8 distinct operational edge cases with tags | HTTP 200, 8 edge cases verified | **PASS** |

---

### Category 16: Error-Handling Tests

| Test Function | Input | Function / API | Expected Result | Actual Result | Status |
|---|---|---|---|---|---|
| `test_error_handling_recommendation_not_found` | Non-existent ID `REC-DOESNOTEXIST` | `GET /api/recommendations/{id}`, `POST /api/recommendations/{id}/approve` | HTTP 404 Not Found | HTTP 404 Not Found | **PASS** |
| `test_system_health_subsystems` | Standard health request | `GET /health` | HTTP 200, status in `['healthy', 'degraded']`, DB connected, ML status reported | HTTP 200 Healthy | **PASS** |
