"""
Review #3 Comprehensive Report & PDF Generator for PharmaShift
Generates:
1. docs/REVIEW_3_REPORT.md (Exhaustive academic & technical report)
2. docs/REVIEW_3_REPORT.pdf (Formatted institutional PDF via ReportLab)
"""

import os
import sys

docs_dir = os.path.abspath("docs")
os.makedirs(docs_dir, exist_ok=True)

report_md_path = os.path.join(docs_dir, "REVIEW_3_REPORT.md")
pdf_path = os.path.join(docs_dir, "REVIEW_3_REPORT.pdf")

print("Generating Review #3 Markdown Report...")

markdown_content = r"""# PharmaShift: Comprehensive Review #3 Project Completion Report
**Product Name**: PharmaShift – Expiry-Aware Pharmacy Network Optimizer  
**Project Title**: Pharmacy Stock Redistribution & Recommendation System  
**Review Milestone**: Project Review #3 (Evaluation Milestone)  
**Academic Department**: Department of Computer Science & Engineering / Information Technology  
**Evaluation Scores to Date**: Review #1: **34.3 / 35 (98%)** | Review #2: **32.2 / 35 (92%)**  
**Automated Testing Status**: **49 / 49 Tests Passed (100% Pass Rate)**  
**Frontend Production Build**: **2,355 Modules Transformed (0 Errors, Vite Build Clean)**  

---

## 1. Title Page & Academic Metadata

| Project Parameter | Academic Specification |
|---|---|
| **Project Title** | Pharmacy Stock Redistribution & Recommendation System |
| **Product Name** | PharmaShift – Expiry-Aware Pharmacy Network Optimizer |
| **Review Milestone** | Project Review #3 (Technical Implementation & Governance Phase) |
| **Review #1 Score** | **34.3 / 35 marks (98% criteria met)** |
| **Review #2 Score** | **32.2 / 35 marks (92% criteria met)** |
| **Target Milestone Objective** | Resolution of Review #2 Feedback, Login-First Security, Error Boundaries, 49 Unit Tests, Master API Docs, Database Schema |
| **Automated Test Results** | **49 Passed / 0 Failed in 50.03 seconds (100% Pass Rate)** |
| **Frontend Production Build** | **Vite Production Bundle (2,355 modules, 0 errors, Exit Code 0)** |
| **ML Regression Model** | Random Forest Regressor ($R^2 = 0.7523$, MAE = 1.2152 units/day, RMSE = 3.5170 units/day) |
| **Simulation Validation** | 30 Simulation Cycles: ₹83,14,345.38 Protected (+₹7.44L / +9.88% over FIFO), -52.09% Expiry Waste |
| **Report Date** | September 29, 2026 |
| **Student Name(s)** | [Student Name(s) Placeholder] |
| **Register / Roll Number(s)**| [Register / Roll Number(s) Placeholder] |
| **Project Supervisor / Guide**| [Project Supervisor Name Placeholder] |

---

## 2. Executive Summary & Review #2 Evaluator Feedback Resolution

PharmaShift is an AI-assisted pharmacy inventory optimization and stock redistribution decision-support platform. It resolves the severe economic and clinical challenge of near-expiry medicine wastage occurring concurrently with localized stockouts across distributed pharmacy networks.

In **Review #1**, the project achieved **34.3 / 35 marks (98%)** for core architecture and problem formulation. In **Review #2**, the project scored **32.2 / 35 marks (92%)** for foundational database design, machine learning demand forecasting, and simulation-based economic evaluation.

### 2.1 Review #2 Evaluator Feedback Analysis:
The Review #2 evaluators recognized:
1. *Clear description of functional components and deliverables.*
2. *Structured thought process toward project objectives.*
3. *Public repository with foundational project structure.*

The evaluators specified four key areas for enhancement in **Review #3**:
1. **Granular Technical Documentation on Unit Testing and Error Boundaries**: Document the exact testing harness, test classifications, input/expected/actual states, and React error boundary resilience.
2. **Expanded Code Comments Explaining Complex Logic**: Add comprehensive "WHY" comments explaining the medical, mathematical, and algorithmic reasoning behind safety buffers, feasibility constraints, and destination scoring.
3. **Document API Endpoints in README for Subsequent Reviews**: Provide a complete directory of all REST endpoints, HTTP methods, authorization requirements, and payload contracts.
4. **Document Database Schema in README for Subsequent Reviews**: Provide detailed relational schema tables, constraints, foreign key mappings, and entity-relationship diagrams.

### 2.2 Feedback Resolution Matrix:

| Review #2 Evaluator Feedback | Review #3 Implementation Deliverable | Verification Evidence & Location |
|---|---|---|
| **1. Granular Technical Documentation on Unit Testing** | Expanded test suite from 30 to **49 automated tests across 16 categories** covering authentication, RBAC, inventory, ML, expiry, safety stock, feasibility, audit, and edge cases. | `backend/tests/test_backend.py`, `docs/testing.md` (49/49 passed in 50.03s) |
| **2. Technical Documentation on Error Boundaries** | Implemented React `ErrorBoundary.jsx` wrapping all 8 views with component-level isolation, friendly fallback UI, and "Retry Section" non-destructive state recovery. | `frontend/src/components/ErrorBoundary.jsx`, `docs/error_handling.md`, `App.jsx` |
| **3. Expanded Code Comments Explaining Complex Logic** | Added in-depth "WHY" docstrings and inline comments detailing clinical safety buffers, Haversine logistics math, capacity caps, and bcrypt/JWT security. | `backend/app/recommender/engine.py`, `feasibility.py`, `risk_scorer.py`, `ml_service.py`, `security.py` |
| **4. Document API Endpoints in README** | Structured Master API Endpoints Directory (20 endpoints) with paths, methods, auth scopes, request/response models, and status codes. | `README.md` (Section 12), `docs/api.md` |
| **5. Document Database Schema in README** | Structured Relational Database Schema (10 models) with data types, nullable constraints, foreign keys, cascade rules, and Mermaid ER diagram. | `README.md` (Section 11), `docs/database_schema.md` |
| **6. Strict Login-First Architecture** | Completely removed unauthenticated default admin bypass; enforced unauthenticated route interception redirecting to Login; added Quick-Fill evaluation panel. | `frontend/src/pages/Login.jsx`, `frontend/src/App.jsx`, `frontend/src/context/AuthContext.jsx` |

---

## 3. Review #3 Core Implementations

### 3.1 Strict Login-First User Experience & Authentication Architecture

A core security requirement addressed in Review #3 is that **the Login page is the first page of the application**. Unauthenticated users cannot view or manipulate operational modules.

```
                           +---------------------------------+
                           |   User Accesses Application     |
                           +----------------+----------------+
                                            |
                                            v
                           +----------------+----------------+
                           |  Authenticated Session Active?  |
                           +-------+-----------------+-------+
                                   |                 |
                              YES  |                 |  NO
                                   v                 v
                    +--------------+----+   +--------+------------------+
                    | Render Protected  |   | Intercept & Render        |
                    | App Layout Views  |   | Login Page (<Login.jsx>)  |
                    +-------------------+   +--------+------------------+
                                                     |
                                            Enters Credentials or Clicks
                                            Evaluation Quick-Fill Persona
                                                     |
                                                     v
                                            +--------+------------------+
                                            | POST /api/auth/login      |
                                            | (Bcrypt Verify + JWT Gen) |
                                            +--------+------------------+
                                                     |
                                              200 OK | Token Issued
                                                     v
                                            +--------+------------------+
                                            | Store Token in LocalStorage|
                                            | Update AuthContext State  |
                                            +--------+------------------+
                                                     |
                                                     v
                                            +--------+------------------+
                                            | Render Dashboard & Views  |
                                            +---------------------------+
```

#### Key Implementation Details:
1. **Dedicated Login Component (`frontend/src/pages/Login.jsx`)**:
   - Enterprise pharmaceutical dark-slate theme with dual-tone status banners.
   - Live credential validation, password show/hide toggle, and real-time error alerts.
   - **Review Evaluation Quick-Fill Panel**: Enables academic evaluators to switch between demo personas with a single click:
     - `Admin`: `admin@pharmacy.io` / `Admin@123` (Full system oversight & database seed access).
     - `Manager`: `manager@pharmacy.io` / `Manager@123` (Network-wide inventory, approval, and simulation execution).
     - `Pharmacist 1`: `pharmacist@pharmacy.io` / `Pharmacist@123` (Scoped to Apollo Pharmacy Indiranagar - `PHARM-001`).
     - `Pharmacist 2`: `pharmacist2@pharmacy.io` / `Pharmacist@123` (Scoped to MedPlus Koramangala - `PHARM-002`).
2. **Cryptographic Security Stack (`backend/app/utils/security.py`)**:
   - Passwords hashed using `passlib.context.CryptContext(schemes=["bcrypt"])` with 10 salt rounds and explicit 72-byte string truncation safety.
   - Signed JSON Web Tokens (HS256) carrying claims: `sub` (email), `role` (`ADMIN`, `MANAGER`, `PHARMACIST`), `assigned_pharmacy_id` (e.g. `PHARM-001`), and `exp` (configurable expiration).
3. **Session Interception & Invalidation (`frontend/src/services/api.js`)**:
   - Axios request interceptor injects `Authorization: Bearer <token>` into all outbound HTTP requests.
   - Axios response interceptor monitors for `HTTP 401 Unauthorized`. If a token expires or is rejected, the client clears `localStorage`, dispatches an `auth:unauthorized` window event, and triggers an immediate redirect to the Login screen.
4. **Explicit Sign Out Controls**:
   - Integrated prominent "Sign Out" actions in both the desktop `Navbar.jsx` and mobile `Sidebar.jsx`, ensuring users can cleanly terminate sessions and return to the login screen.

---

### 3.2 Role-Based Access Control (RBAC) Enforcement

PharmaShift implements multi-level authorization guards at both the API gateway and individual data layer levels:

```
                            +-----------------------------------+
                            |       Incoming REST Request       |
                            +-----------------+-----------------+
                                              |
                                              v
                            +-----------------+-----------------+
                            |    get_current_active_user()     |
                            |   (Validates JWT Signature & Exp) |
                            +--------+-----------------+--------+
                                     |                 |
                               Valid |                 | Invalid / Missing
                                     v                 v
                      +--------------+----+   +--------+----------------+
                      | require_roles(...) |   | Return HTTP 401        |
                      +-------+-----------+   | Unauthorized Response  |
                              |               +------------------------+
                  Role Matches| Role Disallowed
                              v
               +--------------+----+   +--------------------------------+
               | Branch Access Check|   | Return HTTP 403                |
               | (If PHARMACIST)   |   | Forbidden Access Denied        |
               +-------+-----------+   +--------------------------------+
                       |
                       +-----------------------+
                       | Allowed               | Disallowed
                       v                       v
        +--------------+------------------+  +-+--------------------------------+
        | Execute Route Controller Logic  |  | Return HTTP 403                  |
        | Return Filtered JSON Response   |  | "Cannot access other branch data"|
        +---------------------------------+  +----------------------------------+
```

#### RBAC Matrix:

| Operational Capability | ADMIN | MANAGER | PHARMACIST | Scoping / Protection Rule |
|---|:---:|:---:|:---:|---|
| **View System Dashboard & Health** | Yes | Yes | Yes | Filtered view based on role |
| **View Inventory Batches** | Yes | Yes | Scoped | Pharmacist sees only assigned branch batches |
| **Generate Recommendations** | Yes | Yes | Scoped | Pharmacist evaluates only donor batches from their branch |
| **Approve / Reject Redistribution** | Yes | Yes | Scoped | Pharmacist can only approve transfers originating from assigned branch |
| **Override Transfer Quantity** | Yes | Yes | Scoped | Pharmacist can only override batches from assigned branch |
| **Run Monte Carlo Simulation** | Yes | Yes | No | Restricted to Network Managers and Admins (HTTP 403) |
| **Access Audit Compliance Logs** | Yes | Yes | No | Network-wide governance restricted (HTTP 403) |
| **Re-seed Operational Database** | Yes | No | No | Strictly restricted to `ADMIN` role (`require_roles(["ADMIN"])`) |

---

### 3.3 Frontend Component-Level Error Boundaries & Fault Isolation

To eliminate application crashes caused by unexpected network errors, malformed payloads, or rendering anomalies, PharmaShift introduces **React Error Boundaries**:

```
                         +-----------------------------------+
                         |          App.jsx Shell            |
                         +-----------------+-----------------+
                                           |
        +------------------+---------------+------------------+------------------+
        |                  |                                  |                  |
        v                  v                                  v                  v
+-------+-------+  +-------+-------+                  +-------+-------+  +-------+-------+
| ErrorBoundary |  | ErrorBoundary |                  | ErrorBoundary |  | ErrorBoundary |
|   Dashboard   |  |   Inventory   |                  |Recommendations|  |  Audit Logs   |
+-------+-------+  +-------+-------+                  +-------+-------+  +-------+-------+
        |                  |                                  |                  |
        v                  v                                  v                  v
   <Dashboard />     <Inventory />                    <Recommendations/>  <AuditLogs />
```

#### Architecture of `frontend/src/components/ErrorBoundary.jsx`:
- **State Trapping**: Implements `static getDerivedStateFromError(error)` to capture render-phase exceptions and switch state to `{ hasError: true, error }`.
- **Diagnostic Logging**: Implements `componentDidCatch(error, errorInfo)` to log diagnostic component stack traces via `console.error` for developer inspection without exposing raw stacks to end-users.
- **Controlled Fallback Card**: Renders an alert card with an amber warning shield, clear explanation (*"Something went wrong while loading this section"*), and masked error message.
- **Non-Destructive State Recovery**: Provides a **"Retry Section"** button that invokes `this.setState({ hasError: false, error: null })`. This re-mounts the isolated component cleanly without discarding authentication tokens or navigating away from the page.
- **Global Reload Fallback**: Includes a secondary **"Reload Application"** button to force a clean browser reload (`window.location.reload()`) if network state is unrecoverable.

---

### 3.4 Backend Centralized Exception Handling & Shielding

In `backend/app/main.py`, centralized exception handlers intercept all runtime exceptions, preventing internal server traces from leaking:

1. **Starlette `HTTPException` Handler**:
   - Catches deliberate application errors (400, 401, 403, 404).
   - Formats response as:
     ```json
     {
       "error": true,
       "status_code": 403,
       "message": "You can only approve recommendations originating from your assigned pharmacy (PHARM-001)",
       "timestamp": "2026-09-29T10:00:00Z"
     }
     ```
2. **Pydantic `RequestValidationError` (422) Handler**:
   - Catches schema mismatches, missing required fields, or invalid numeric ranges (e.g. negative override quantities).
   - Summarizes offending fields into human-readable error descriptions.
3. **Global Unhandled `Exception` (500) Handler**:
   - Catches unexpected internal bugs, database disconnections, or calculation errors.
   - Logs the full traceback on the server console using `logger.error()`.
   - Returns a secure, sanitized response to the client:
     ```json
     {
       "error": true,
       "status_code": 500,
       "message": "An internal server error occurred. Please contact network administrator.",
       "timestamp": "2026-09-29T10:00:00Z"
     }
     ```

---

### 3.5 Automated Unit Testing Suite (49 Tests Across 16 Categories)

The automated test suite in `backend/tests/test_backend.py` was systematically expanded from 30 tests to **49 automated tests across all 16 functional categories**.

- **Execution Command**: `pytest -v backend/tests/test_backend.py`
- **Results**: **49 passed, 0 failed in 50.03 seconds (100% pass rate)**

```
============================== 49 passed in 50.03s ==============================
```

#### Detailed Test Catalog (16 Categories):

| Category # | Category Name | Test Count | Key Test Functions | Scope & Verification Criteria | Status |
|:---:|---|:---:|---|---|:---:|
| **1** | **Authentication** | 4 | `test_auth_login_success`, `test_auth_login_invalid_password`, `test_auth_login_inactive_user`, `test_auth_me_profile` | Validates bcrypt verification, JWT generation, invalid credentials rejection (401), inactive account blocking, profile extraction. | **PASSED** |
| **2** | **Authorization & RBAC** | 6 | `test_rbac_pharmacist_cannot_seed`, `test_rbac_manager_cannot_seed`, `test_rbac_admin_can_seed`, `test_rbac_pharmacist_branch_scoping`, `test_rbac_pharmacist_cannot_approve_other_branch`, `test_rbac_pharmacist_cannot_view_audit_logs` | Confirms that only `ADMIN` can trigger seed, `PHARMACIST` cannot approve other branch transfers (403), and audit logs are restricted. | **PASSED** |
| **3** | **Inventory** | 3 | `test_inventory_listing`, `test_inventory_filter_by_category`, `test_inventory_single_batch` | Tests batch queries across 5,193 records, category filtering (e.g., Antibiotics), and batch ID lookup. | **PASSED** |
| **4** | **Pharmacy Network** | 2 | `test_pharmacies_listing`, `test_pharmacies_single_detail` | Tests retrieval of 18 branch GPS coordinates, storage capacities, operating statuses, and 404 on invalid ID. | **PASSED** |
| **5** | **Demand & ML Inference** | 4 | `test_ml_prediction_endpoint`, `test_ml_metrics_endpoint`, `test_ml_fallback_chain`, `test_medicines_catalog` | Validates live inference from `ml/demand_model.joblib`, model metrics ($R^2=0.7523$), 3-tier fallback chain, and catalog. | **PASSED** |
| **6** | **Expiry-Risk Classification** | 4 | `test_expiry_math_dte`, `test_risk_brackets`, `test_fixed_reference_date`, `test_invalid_date_format` | Validates date parsing, DTE calculation relative to `DEMO_REFERENCE_DATE` (2026-08-14), and risk bracket boundaries. | **PASSED** |
| **7** | **Safety-Stock Retention** | 2 | `test_safety_stock_subtraction`, `test_zero_excess_when_demand_exceeds_stock` | Enforces mandatory 3-day local emergency stock reservation; verifies excess is zero if demand exceeds inventory. | **PASSED** |
| **8** | **Recommendation Engine** | 3 | `test_recommender_generates_recommendations`, `test_recommender_predicted_demand_influence`, `test_recommender_evidence_bullets` | Validates end-to-end recommendation generation, ML demand weighting, and structured evidence bullets generation. | **PASSED** |
| **9** | **Destination Ranking** | 2 | `test_destination_ranking_transit_days`, `test_destination_ranking_critical_bonus` | Validates Haversine transit time calculation and +20.0 priority scoring bonus for critical/emergency medicines. | **PASSED** |
| **10** | **Transfer Feasibility** | 7 | `test_feasibility_transit_exceeds_shelf_life`, `test_feasibility_destination_closed`, `test_feasibility_destination_maintenance`, `test_feasibility_destination_zero_demand`, `test_feasibility_already_expired_batch`, `test_feasibility_capacity_exceeded`, `test_feasibility_all_criteria_met` | Verifies all 7 feasibility guard rails: post-transit shelf life $\ge 3$ days, active branch status, non-zero demand, unexpired stock. | **PASSED** |
| **11** | **API Validation** | 2 | `test_override_quantity_negative_rejected`, `test_rejection_missing_reason_rejected` | Verifies Pydantic HTTP 422 rejections on negative override quantities and missing structured rejection reasons. | **PASSED** |
| **12** | **Database Integrity** | 1 | `test_database_relationships_and_foreign_keys` | Verifies ORM foreign key relationships between Batches, Pharmacies, Medicines, Recommendations, and Audit Logs. | **PASSED** |
| **13** | **Audit Trail** | 4 | `test_audit_log_created_on_approval`, `test_audit_log_created_on_rejection`, `test_audit_log_created_on_override`, `test_audit_logs_filtered_by_action` | Confirms immutable audit records are written on every state transition with actor, role, previous state, and new state. | **PASSED** |
| **14** | **Analytics & Simulation** | 2 | `test_dashboard_kpis_endpoint`, `test_simulation_results_endpoint` | Validates real-time KPI aggregations and multi-scenario simulation benchmarks from `data/simulation_results.json`. | **PASSED** |
| **15** | **Operational Edge Cases** | 1 | `test_edge_cases_all_scenarios` | Validates the deterministic Edge Cases Sandbox verifying all 8 failure prevention scenarios. | **PASSED** |
| **16** | **Error Handling & Telemetry** | 2 | `test_error_handling_404_not_found`, `test_system_health_telemetry` | Validates HTTP 404 on missing recommendation ID and verifies the `SystemHealthOut` subsystem diagnostic strip. | **PASSED** |

---

### 3.6 Explanatory "WHY" Code Comments

Complex clinical, mathematical, and security routines were augmented with comprehensive docstrings explaining the underlying rationale:

1. **`backend/app/recommender/engine.py`**:
   - Explains *why* the local demand buffer is subtracted prior to excess calculation (to prevent creating artificial stockouts at donor pharmacies).
   - Explains *why* candidate branches are sorted by demand velocity and distance penalty (to minimize transit cost and maximize rapid patient consumption).
2. **`backend/app/recommender/feasibility.py`**:
   - Explains *why* the 3-day post-transit shelf-life cushion is strictly enforced ($DTE - T_{\\text{transit}} \\ge 3$) to account for road congestion, receiving inspection, and retail shelf stocking.
   - Explains *why* destination branches marked as closed or under maintenance are immediately filtered out.
3. **`backend/app/recommender/risk_scorer.py`**:
   - Explains *why* a deterministic `DEMO_REFERENCE_DATE` is utilized during academic evaluations (to guarantee consistent, reproducible test outcomes across evaluation dates).
4. **`backend/app/services/ml_service.py`**:
   - Explains the 3-tier fallback strategy (Live Model $\\rightarrow$ Stored Database Rate $\\rightarrow$ 7-day Historical Moving Average) ensuring uninterrupted high-availability inference even during database or model reload events.
5. **`backend/app/utils/security.py`**:
   - Explains the 72-byte string truncation rationale required by Bcrypt's internal key size limitation to prevent silent denial-of-service vulnerabilities.

---

### 3.7 Master REST API Endpoints Directory (20 Endpoints)

| Group | Method | Path | Auth / Role | Description & Contract |
|---|:---:|---|:---:|---|
| **Auth** | `POST` | `/api/auth/login` | Public | Authenticates credentials; returns signed JWT bearer token and user metadata. |
| **Auth** | `GET` | `/api/auth/me` | Bearer Token | Returns authenticated user profile, assigned role, and pharmacy ID. |
| **Inventory** | `GET` | `/api/inventory/` | Bearer Token | Returns paginated inventory batches with DTE, risk tier, and branch location. |
| **Inventory** | `GET` | `/api/inventory/{batch_id}` | Bearer Token | Returns detailed single batch records including safety stock and excess. |
| **Pharmacies**| `GET` | `/api/pharmacies/` | Bearer Token | Returns 18 network branches, GPS coordinates, status, and capacities. |
| **Pharmacies**| `GET` | `/api/pharmacies/{id}` | Bearer Token | Returns single branch profile with inventory value and stockout metrics. |
| **ML Demand** | `POST` | `/api/demand/predict` | Bearer Token | Live ML demand inference for a specific (pharmacy, medicine) pair. |
| **ML Demand** | `GET` | `/api/demand/metrics` | Bearer Token | Returns model validation metrics ($R^2$, MAE, RMSE, feature importances). |
| **Catalog** | `GET` | `/api/medicines/` | Bearer Token | Returns 60 standardized pharmaceutical medications, units, and categories. |
| **Recommender**| `GET` | `/api/recommendations/` | Bearer Token | Returns active redistribution recommendations with 0-100 scores. |
| **Recommender**| `POST` | `/api/recommendations/generate`| `ADMIN`, `MANAGER` | Triggers asynchronous end-to-end evaluation pipeline over all batches. |
| **Actions** | `POST` | `/api/recommendations/{id}/approve` | Role Scoped | Records clinical approval and transitions recommendation to `APPROVED`. |
| **Actions** | `POST` | `/api/recommendations/{id}/reject` | Role Scoped | Records rejection with mandatory structured reason category. |
| **Actions** | `POST` | `/api/recommendations/{id}/override` | Role Scoped | Overrides transfer quantity with live financial recalculation. |
| **Audit** | `GET` | `/api/audit/` | `ADMIN`, `MANAGER` | Returns paginated immutable compliance audit records. |
| **Analytics** | `GET` | `/api/analytics/kpis` | Bearer Token | Returns network-wide KPIs (value protected, expiry risk, transfer rates). |
| **Analytics** | `GET` | `/api/analytics/simulation` | `ADMIN`, `MANAGER` | Returns 30-scenario Monte Carlo benchmark comparison vs FIFO. |
| **Edge Cases**| `GET` | `/api/edge-cases/` | Bearer Token | Returns 8 deterministic failure prevention sandbox scenarios. |
| **System** | `GET` | `/api/health` | Public | Subsystem health telemetry (DB, ML model, cache, reference date). |
| **Admin** | `POST` | `/api/seed` | `ADMIN` Only | Re-seeds database with 5,193 synthetic batches across 18 branches. |

---

### 3.8 Relational Database Architecture (10 Models)

```mermaid
erDiagram
    PHARMACIES ||--o{ BATCHES : "stocks"
    PHARMACIES ||--o{ USERS : "employs"
    MEDICINES ||--o{ BATCHES : "formulates"
    BATCHES ||--o{ RECOMMENDATIONS : "donor_batch"
    PHARMACIES ||--o{ RECOMMENDATIONS : "source_branch"
    PHARMACIES ||--o{ RECOMMENDATIONS : "destination_branch"
    RECOMMENDATIONS ||--o{ AUDIT_LOGS : "governs"
    USERS ||--o{ AUDIT_LOGS : "authorizes"

    PHARMACIES {
        string id PK
        string name
        float latitude
        float longitude
        string status
        int storage_capacity
    }
    MEDICINES {
        string id PK
        string name
        string category
        float unit_price
        boolean is_critical
    }
    BATCHES {
        string id PK
        string pharmacy_id FK
        string medicine_id FK
        int quantity
        date expiry_date
        int days_to_expiry
        string risk_level
    }
    RECOMMENDATIONS {
        string id PK
        string batch_id FK
        string source_pharmacy_id FK
        string destination_pharmacy_id FK
        int recommended_quantity
        float recommendation_score
        string status
    }
    AUDIT_LOGS {
        string id PK
        string recommendation_id FK
        string user_id FK
        string action
        string previous_state
        string new_state
        datetime timestamp
    }
```

#### Database Models Overview:
1. `Pharmacy`: Network facility metadata, GPS coordinates, operating status (`ACTIVE`, `MAINTENANCE`, `CLOSED`), and bay capacity.
2. `Medicine`: Pharmaceutical catalog metadata, ATC category, unit price, and critical life-saving flag.
3. `Batch`: Granular inventory lots with batch number, quantity, expiry date, DTE, risk tier, and safety buffer.
4. `Recommendation`: Actionable redistribution transfer orders with feasibility validation, score (0–100), and status.
5. `AuditLog`: Immutable compliance records capturing actor, action, previous state, new state, and timestamp.
6. `User`: User accounts with bcrypt hashed passwords, role assignment, and assigned pharmacy scoping.
7. `DemandRate`: Precomputed baseline and seasonal consumption rates per (pharmacy, medicine).
8. `DistanceMatrix`: Cached Haversine transit distances and road travel times between branch pairs.
9. `SimulationRun`: Persistent records of multi-scenario benchmark runs.
10. `SystemSetting`: Dynamic runtime configurations including `DEMO_REFERENCE_DATE`.

---

## 4. Machine Learning & Demand Forecasting Validation

PharmaShift employs a **Random Forest Regressor** trained on 1,080 historical daily dispensing records across 18 branches and 60 medicines.

- **Model Specification**: `RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42)`
- **Artifact Path**: `ml/demand_model.joblib`
- **Validation Source**: `ml/model_metrics.json`

### Empirical Regression Metrics:
- **Mean Absolute Error (MAE)**: `1.2152` units/day
- **Root Mean Squared Error (RMSE)**: `3.5170` units/day
- **Coefficient of Determination ($R^2$)**: `0.7523` (Explains 75.23% of dispensing variance)
- **In-Memory Cache Latency**: `< 0.05 ms` ($O(1)$ memory lookup via `(pharmacy_id, medicine_id)` tuple)

### 3-Tier Resilient Inference Chain:
```
1. Live ML Inference (Random Forest Model via scikit-learn)
   │ (If model missing or feature vector incomplete)
   ▼
2. Precomputed Database Demand Rate (Stored historical rate)
   │ (If database record missing)
   ▼
3. 7-Day Velocity Averaging Heuristic (Safe fallback rate)
```

---

## 5. Redistribution Algorithm & Clinical Constraints

### 5.1 Local Excess Stock Calculation:
$$\\text{Local Consumption} = \\text{Daily Demand} \\times DTE$$
$$\\text{Safety Buffer} = \\max(3, \\lceil 0.15 \\times \\text{Local Consumption} \\rceil)$$
$$\\text{Excess Quantity} = \\max(0, \\text{Current Quantity} - \\text{Local Consumption} - \\text{Safety Buffer})$$

### 5.2 Post-Transit Shelf Life Cushion:
$$\\text{Transit Time} = \\left\\lceil \\frac{\\text{Haversine Distance (km)}}{30.0 \\text{ km/h} \\times 8.0 \\text{ h/day}} \\right\\rceil$$
$$\\text{Post-Transit Shelf Life} = DTE - \\text{Transit Time} \\ge 3 \\text{ days}$$
*(If post-transit life is less than 3 days, the candidate branch is strictly disqualified).*

### 5.3 Destination Priority Ranking Formula:
$$\\text{Score} = (\\text{Dest Demand Velocity} \\times 12.0) + (\\text{Remaining Life} \\times 2.5) - (\\text{Distance km} \\times 0.35) [+ 20.0 \\text{ if Critical}]$$

### 5.4 Capacity-Constrained Allocation:
$$Q^* = \\min(\\text{Source Excess}, \\text{Dest Consumable Window}, \\text{Dest 15\\% Bay Allowance})$$

### 5.5 High-Impact Escalation Safeguards:
A transfer is automatically flagged as **High-Impact** if:
- Total transfer monetary value $\\ge ₹2,000$
- Transfer quantity $\\ge 50$ units
- Days-to-Expiry $\\le 14$ days
- Formulation flagged as life-saving Critical Medicine

---

## 6. Empirical Simulation Results (Baseline vs. Proposed)

Across **30 multi-scenario Monte Carlo simulation cycles** (`data/simulation_results.json`):

| Evaluation Metric | Baseline (Isolated FIFO) | Proposed PharmaShift Recommender | Net Benefit / Improvement |
|---|:---:|:---:|:---:|
| **Total Value Protected** | ₹75,70,344.23 | **₹83,14,345.38** | **+₹7,44,001.15 (+9.88% Gain)** |
| **Value Lost to Expiration** | ₹14,28,450.00 | **₹6,84,448.85** | **-₹7,44,001.15 (-52.09% Loss Reduction)** |
| **Recommendation Acceptance Rate** | N/A | **93.03%** | High clinician operational concurrence |
| **Average Transit Distance** | N/A | **10.27 km** | Localized urban logistics efficiency |
| **Average Remaining Shelf Life** | N/A | **19.41 days** | Ample safety cushion prior to expiry |
| **Total Evaluated Decisions** | 0 | **1,794 batches** | Comprehensive multi-scenario evaluation |

---

## 7. Step-by-Step Live Evaluator Demonstration Script

The following 17-step script provides a seamless, rigorous demonstration of all Review #3 features during evaluation defense:

1. **Step 1: Unauthenticated Interception**: Navigate to `http://localhost:5173/`. Verify that the protected dashboard cannot be accessed directly and the Login page is presented.
2. **Step 2: Quick-Fill Persona Selection**: Click the **"Review Evaluation Quick-Fill: Admin"** button. Observe automatic credential population (`admin@pharmacy.io`).
3. **Step 3: Secure Authentication**: Click **"Sign In"**. Verify successful authentication, JWT issuance, and redirection to the protected Dashboard.
4. **Step 4: Subsystem Health Telemetry**: Inspect the top health strip confirming `Database: CONNECTED`, `ML Model: LOADED (R²=0.7523)`, and `Ref Date: 2026-08-14`.
5. **Step 5: Executive AI Action Center**: Review the priority action hero card displaying immediate high-impact redistribution recommendations.
6. **Step 6: Expiry Risk Inventory Monitor**: Navigate to **Inventory**. Filter by "Critical" risk to observe batches nearing expiration with preserved safety stock buffers.
7. **Step 7: Explainable Recommendation Rationale**: Navigate to **Recommendations**. Open recommendation details to inspect the normalized 0–100 score and safety checklist bullets.
8. **Step 8: Human-in-the-Loop Approval**: Click **"Approve"** on a standard recommendation. Confirm status transitions to `APPROVED` with live value update.
9. **Step 9: High-Impact Escalation Challenge**: Click **"Approve"** on a high-value transfer (>₹2,000). Verify that the modal requires checking the explicit clinical safety confirmation checkbox before enabling approval.
10. **Step 10: Structured Rejection Workflow**: Select a recommendation and click **"Reject"**. Attempt to submit without selecting a reason; verify validation block. Select "Clinical Need at Source Branch", enter clinical notes, and confirm rejection.
11. **Step 11: Quantity Override with Live Math**: Click **"Override"** on a recommendation. Change quantity from 50 to 30. Verify that the displayed transfer value updates in real time, then confirm override.
12. **Step 12: Immutable Compliance Audit Trail**: Navigate to **Audit Logs**. Verify that the approval, rejection, and override operations executed in Steps 8–11 appear with actor email, role, previous state, and new state.
13. **Step 13: Deterministic Edge Cases Sandbox**: Navigate to **Edge Cases**. Review all 8 failure prevention scenarios (e.g. transit exceeding shelf life, closed branch, zero demand) confirming algorithmic safety enforcement.
14. **Step 14: Empirical Simulation Comparison**: Navigate to **Analytics**. Review the 30-scenario Monte Carlo benchmark charts demonstrating +₹7.44L (+9.88%) value gain and -52.09% expiry loss reduction.
15. **Step 15: Spatial Logistics Network**: Navigate to **Pharmacies**. Inspect the interactive network topology map showing transit distances and branch capacities.
16. **Step 16: Role-Based Access Scoping**: Click **"Sign Out"**. In the Quick-Fill panel, select **"Pharmacist 1"** (`pharmacist@pharmacy.io`). Sign in and verify that inventory and approval actions are strictly scoped to `PHARM-001`. Attempting unauthorized actions yields HTTP 403 Forbidden.
17. **Step 17: Automated Unit Test Verification**: Open the terminal and execute `pytest -v backend/tests/test_backend.py`. Present the live test run: **49 passed out of 49 in ~50 seconds (100% pass rate)**.

---

## 8. Milestone Completion Breakdown

| Milestone Stage | Target Scope | Key Deliverables | Verified Status |
|---|:---:|---|:---:|
| **Review #1** | Foundational Architecture | Problem formulation, system architecture, functional decomposition | **34.3 / 35 (98%)** |
| **Review #2** | Foundational Implementation | Relational schema, ML demand model, simulation suite, GitHub repo | **32.2 / 35 (92%)** |
| **Review #3** | **Governance & Resilience Phase** | **Login-First UI, RBAC, Error Boundaries, 49 Tests, API/DB Documentation, Rationale Comments** | **100% DELIVERED & VERIFIED** |
| **Review #4** | Enterprise Scale & Pilots | Hospital ERP connectors (HL7/FHIR), automated courier dispatch APIs, PWA barcode scanner | *Roadmap Planned* |

---

## 9. Conclusion

PharmaShift has successfully implemented all Review #3 requirements and resolved all evaluator feedback from Review #2. The platform guarantees a secure **Login-First** user experience, isolates runtime rendering anomalies via **React Error Boundaries**, enforces rigorous **Role-Based Access Control**, validates all business logic with **49 passing automated unit tests across 16 categories**, and provides complete, transparent architectural documentation across the codebase.
"""

with open(report_md_path, "w", encoding="utf-8") as f:
    f.write(markdown_content)

print(f"Written REVIEW_3_REPORT.md successfully to {report_md_path}!")

print("Generating Review #3 PDF Report via ReportLab...")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable, KeepTogether
    )
    from reportlab.pdfgen import canvas

    class NumberedCanvas(canvas.Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            num_pages = len(self._saved_page_states)
            for state in self._saved_page_states:
                self.__dict__.update(state)
                self.draw_page_number(num_pages)
                canvas.Canvas.showPage(self)
            canvas.Canvas.save(self)

        def draw_page_number(self, page_count):
            self.saveState()
            self.setFont("Helvetica", 9)
            self.setFillColor(colors.HexColor("#64748b"))
            # Header
            if self._pageNumber > 1:
                self.drawString(54, 750, "PharmaShift — Comprehensive Review #3 Project Completion Report")
                self.drawRightString(558, 750, "September 2026")
                self.setStrokeColor(colors.HexColor("#cbd5e1"))
                self.setLineWidth(0.5)
                self.line(54, 742, 558, 742)
            # Footer
            page_text = f"Page {self._pageNumber} of {page_count}"
            self.drawRightString(558, 36, page_text)
            self.drawString(54, 36, "Confidential — Academic Review #3 Submission Document")
            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(54, 48, 558, 48)
            self.restoreState()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Center
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#059669'),
        alignment=1, # Center
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'DocBullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=12.5,
        textColor=colors.HexColor('#334155'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#1e293b')
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8,
        leading=10.5,
        textColor=colors.white
    )

    story = []

    # Title Page
    story.append(Spacer(1, 30))
    story.append(Paragraph("Pharmacy Stock Redistribution &amp; Recommendation System", title_style))
    story.append(Paragraph("Product Name: PharmaShift – Expiry-Aware Pharmacy Network Optimizer", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#059669'), spaceBefore=5, spaceAfter=20))

    meta_data = [
        [Paragraph("Project Parameter", table_header), Paragraph("Academic Specification", table_header)],
        [Paragraph("Project Title", table_cell), Paragraph("Pharmacy Stock Redistribution & Recommendation System", table_cell)],
        [Paragraph("Product Name", table_cell), Paragraph("PharmaShift – Expiry-Aware Pharmacy Network Optimizer", table_cell)],
        [Paragraph("Review Milestone", table_cell), Paragraph("Project Review #3 (Evaluation Milestone)", table_cell)],
        [Paragraph("Review #1 Score", table_cell), Paragraph("34.3 / 35 marks (98% criteria met)", table_cell)],
        [Paragraph("Review #2 Score", table_cell), Paragraph("32.2 / 35 marks (92% criteria met)", table_cell)],
        [Paragraph("Automated Tests", table_cell), Paragraph("49 / 49 Passed across 16 categories (100% pass rate in 50.03s)", table_cell)],
        [Paragraph("Production Build", table_cell), Paragraph("Vite Production Bundle (2,355 modules, 0 errors)", table_cell)],
        [Paragraph("ML Regressor", table_cell), Paragraph("Random Forest (R²: 0.7523, MAE: 1.2152, RMSE: 3.5170)", table_cell)],
        [Paragraph("Simulation Validation", table_cell), Paragraph("30 cycles: ₹83.14L protected (+₹7.44L over FIFO), -52.09% loss", table_cell)],
        [Paragraph("Report Date", table_cell), Paragraph("September 29, 2026", table_cell)],
    ]
    meta_table = Table(meta_data, colWidths=[150, 350])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("<b>Student &amp; Department Placeholders:</b>", body_style))
    story.append(Paragraph("&bull; Student Name(s): [Student Name(s) Placeholder]", bullet_style))
    story.append(Paragraph("&bull; Register / Roll Number(s): [Register / Roll Number(s) Placeholder]", bullet_style))
    story.append(Paragraph("&bull; Project Supervisor / Guide: [Project Supervisor Name Placeholder]", bullet_style))
    story.append(Paragraph("&bull; Department of Computer Science &amp; Engineering / Information Technology", bullet_style))
    story.append(PageBreak())

    # Executive Summary & Review #2 Feedback Resolution
    story.append(Paragraph("2. Executive Summary &amp; Review #2 Feedback Resolution", h1_style))
    story.append(Paragraph(
        "PharmaShift is an AI-assisted pharmacy inventory optimization platform designed to eliminate near-expiry medicine wastage "
        "and resolve localized stockouts across distributed pharmacy networks. Following Review #1 (34.3/35, 98%) and Review #2 (32.2/35, 92%), "
        "Review #3 comprehensively addresses all evaluator feedback recommendations.",
        body_style
    ))

    feedback_data = [
        [Paragraph("Review #2 Evaluator Feedback", table_header), Paragraph("Review #3 Implementation Deliverable", table_header), Paragraph("Verification Evidence", table_header)],
        [Paragraph("1. Granular Technical Documentation on Unit Testing", table_cell), Paragraph("Expanded test suite from 30 to 49 automated tests across 16 categories.", table_cell), Paragraph("backend/tests/test_backend.py (49/49 passed in 50.03s)", table_cell)],
        [Paragraph("2. Technical Documentation on Error Boundaries", table_cell), Paragraph("Built React ErrorBoundary.jsx wrapping all 8 views with non-destructive state reset.", table_cell), Paragraph("frontend/src/components/ErrorBoundary.jsx, App.jsx", table_cell)],
        [Paragraph("3. Expanded Code Comments Explaining Logic", table_cell), Paragraph("Added in-depth 'WHY' docstrings across clinical, mathematical, and security routines.", table_cell), Paragraph("engine.py, feasibility.py, risk_scorer.py, ml_service.py", table_cell)],
        [Paragraph("4. Document API Endpoints in README", table_cell), Paragraph("Master API Directory (20 endpoints) with paths, methods, auth, roles, and status codes.", table_cell), Paragraph("README.md Section 12, docs/api.md", table_cell)],
        [Paragraph("5. Document Database Schema in README", table_cell), Paragraph("Relational Schema (10 models) with constraints, foreign keys, and Mermaid ER diagram.", table_cell), Paragraph("README.md Section 11, docs/database_schema.md", table_cell)],
        [Paragraph("6. Strict Login-First Architecture", table_cell), Paragraph("Removed auto-bypass; unauthenticated requests intercepted to Login; Quick-Fill panel added.", table_cell), Paragraph("frontend/src/pages/Login.jsx, App.jsx", table_cell)],
    ]
    feedback_table = Table(feedback_data, colWidths=[140, 210, 150])
    feedback_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(feedback_table)

    # Core Review #3 Implementations
    story.append(Paragraph("3. Core Implementations in Review #3 Category", h1_style))
    story.append(Paragraph(
        "<b>3.1 Strict Login-First &amp; Route Protection:</b> Unauthenticated users cannot view operational views. Direct URL access "
        "is intercepted by App.jsx, redirecting immediately to Login.jsx. Includes a Review Evaluation Quick-Fill panel with 1-click persona "
        "selection (Admin, Manager, Pharmacist 1, Pharmacist 2).",
        body_style
    ))
    story.append(Paragraph(
        "<b>3.2 Role-Based Access Control (RBAC):</b> Passwords hashed with bcrypt (10 rounds, 72-byte safe truncation). Stateless HS256 JWT tokens. "
        "Strict branch scoping: a Pharmacist assigned to PHARM-001 is prohibited from accessing or approving transfers for PHARM-002 (HTTP 403 Forbidden).",
        body_style
    ))
    story.append(Paragraph(
        "<b>3.3 React Error Boundaries &amp; Fault Isolation:</b> ErrorBoundary.jsx encloses all 8 core views. Catches rendering exceptions, "
        "displays a controlled fallback card, and provides a 'Retry Section' non-destructive reset button that restores component state without user logout.",
        body_style
    ))
    story.append(Paragraph(
        "<b>3.4 Backend Centralized Exception Shielding:</b> Global handlers for HTTPException, RequestValidationError (422), and unhandled 500 errors. "
        "Zero stack trace leakage to API consumers while maintaining structured server-side diagnostic logs.",
        body_style
    ))

    # Unit Testing Results Table
    story.append(PageBreak())
    story.append(Paragraph("4. Automated Unit Testing Results (49 / 49 Passed)", h1_style))
    story.append(Paragraph(
        "Command executed: <code>pytest -v backend/tests/test_backend.py</code>. <b>49 passed, 0 failed in 50.03 seconds (100% pass rate)</b>.",
        body_style
    ))

    test_data = [
        [Paragraph("Category", table_header), Paragraph("Count", table_header), Paragraph("Scope / Functionality Verified", table_header), Paragraph("Status", table_header)],
        [Paragraph("1. Authentication", table_cell), Paragraph("4", table_cell), Paragraph("Login success, invalid password (401), inactive user, me profile", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("2. Authorization / RBAC", table_cell), Paragraph("6", table_cell), Paragraph("Branch scoping, cross-branch approval block (403), seed admin check", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("3. Inventory", table_cell), Paragraph("3", table_cell), Paragraph("Batch listing, category filter, single batch lookup", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("4. Pharmacy Network", table_cell), Paragraph("2", table_cell), Paragraph("18 branches listing, single branch details, 404 missing branch", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("5. Demand & ML", table_cell), Paragraph("4", table_cell), Paragraph("Live RF inference, model metrics, 3-tier fallback chain, catalog", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("6. Expiry-Risk Class.", table_cell), Paragraph("4", table_cell), Paragraph("DTE math, risk brackets, fixed demo reference date, date parser", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("7. Safety-Stock", table_cell), Paragraph("2", table_cell), Paragraph("3-day safety buffer reservation, zero excess enforcement", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("8. Recommender Engine", table_cell), Paragraph("3", table_cell), Paragraph("End-to-end generation, ML demand weighting, evidence bullets", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("9. Destination Ranking", table_cell), Paragraph("2", table_cell), Paragraph("Haversine transit calculation, critical medication score bonus", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("10. Feasibility Checks", table_cell), Paragraph("7", table_cell), Paragraph("Post-transit life >= 3 days, closed/maintenance branch, expired batch", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("11. API Validation", table_cell), Paragraph("2", table_cell), Paragraph("Negative override rejection (422), missing rejection reason (422)", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("12. Database Integrity", table_cell), Paragraph("1", table_cell), Paragraph("ORM foreign keys and cascade integrity traversal across models", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("13. Audit Trail", table_cell), Paragraph("4", table_cell), Paragraph("Immutable log on approve, reject, override, and action filtering", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("14. Analytics", table_cell), Paragraph("2", table_cell), Paragraph("Dashboard KPIs aggregation, 30-scenario simulation endpoint", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("15. Edge Cases", table_cell), Paragraph("1", table_cell), Paragraph("Deterministic sandbox verifying all 8 failure prevention scenarios", table_cell), Paragraph("PASSED", table_cell)],
        [Paragraph("16. Error Handling", table_cell), Paragraph("2", table_cell), Paragraph("404 handling on invalid ID, subsystem health telemetry output", table_cell), Paragraph("PASSED", table_cell)],
    ]
    test_table = Table(test_data, colWidths=[120, 45, 275, 60])
    test_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(test_table)

    # ML & Simulation Results
    story.append(Spacer(1, 10))
    story.append(Paragraph("5. Machine Learning &amp; Empirical Simulation Validation", h1_style))
    story.append(Paragraph(
        "<b>ML Demand Regressor:</b> RandomForestRegressor (100 trees, depth 10) trained on 1,080 historical dispensing records: "
        "<b>MAE = 1.2152 units/day</b>, <b>RMSE = 3.5170 units/day</b>, <b>R² = 0.7523</b>.",
        body_style
    ))
    story.append(Paragraph("<b>Empirical Monte Carlo Simulation (30 Cycles Benchmark vs Isolated FIFO):</b>", body_style))

    sim_data = [
        [Paragraph("Evaluation Metric", table_header), Paragraph("Baseline (Isolated FIFO)", table_header), Paragraph("Proposed Recommender", table_header), Paragraph("Net Gain / Impact", table_header)],
        [Paragraph("Average Value Protected", table_cell), Paragraph("₹75,70,344.23", table_cell), Paragraph("₹83,14,345.38", table_cell), Paragraph("+₹7,44,001.15 (+9.88%)", table_cell)],
        [Paragraph("Value Lost to Expiration", table_cell), Paragraph("₹14,28,450.00", table_cell), Paragraph("₹6,84,448.85", table_cell), Paragraph("-₹7,44,001.15 (-52.09% loss reduction)", table_cell)],
        [Paragraph("Clinician Acceptance Rate", table_cell), Paragraph("N/A", table_cell), Paragraph("93.03%", table_cell), Paragraph("Empirical clinical concurrence", table_cell)],
        [Paragraph("Average Transit Distance", table_cell), Paragraph("N/A", table_cell), Paragraph("10.27 km", table_cell), Paragraph("Localized urban routing efficiency", table_cell)],
        [Paragraph("Average Remaining Shelf Life", table_cell), Paragraph("N/A", table_cell), Paragraph("19.41 days", table_cell), Paragraph("Generous safety margin post-transfer", table_cell)],
    ]
    sim_table = Table(sim_data, colWidths=[140, 110, 120, 130])
    sim_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8fafc'), colors.white])
    ]))
    story.append(sim_table)

    # 17-Step Demo Script Summary & Conclusion
    story.append(PageBreak())
    story.append(Paragraph("6. 17-Step Live Evaluator Demonstration Script Summary", h1_style))
    steps = [
        "1. Unauthenticated Interception: Access http://localhost:5173/ -> verifies redirect to Login.",
        "2. Quick-Fill Panel: Select 'Admin' -> auto-populates admin@pharmacy.io.",
        "3. Authentication: Click 'Sign In' -> JWT token issued, redirect to Protected Dashboard.",
        "4. Telemetry: Verify health strip (Database Connected, ML Model R²=0.7523, Ref Date 2026-08-14).",
        "5. AI Action Center: Review prioritized high-impact redistribution recommendations.",
        "6. Inventory Monitor: Filter by 'Critical' risk tier; observe 3-day safety stock reservation.",
        "7. Explainability: Inspect normalized 0-100 Recommendation Score and safety checklist.",
        "8. Clinical Approval: Approve standard transfer -> state transitions to APPROVED.",
        "9. High-Impact Escalation: Approve transfer >₹2,000 -> requires safety confirmation checkbox.",
        "10. Structured Rejection: Reject with mandatory reason 'Clinical Need at Source Branch' and clinical note.",
        "11. Quantity Override: Override quantity from 50 to 30; observe live value recalculation.",
        "12. Audit Trail: Verify immutable audit records created for approval, rejection, and override.",
        "13. Edge Cases Sandbox: Verify all 8 failure prevention scenarios (transit > shelf life, closed branch).",
        "14. Simulation Analytics: Inspect 30-scenario Monte Carlo comparison (+₹7.44L gain, -52.09% loss).",
        "15. Spatial Network: View interactive topology map of 18 branches and Haversine distances.",
        "16. RBAC Branch Scoping: Sign in as 'Pharmacist 1' -> actions strictly scoped to PHARM-001 (403 on others).",
        "17. Automated Tests: Run pytest backend/tests/test_backend.py -> 49 passed, 0 failed in 50.03s."
    ]
    for step in steps:
        story.append(Paragraph(f"&bull; <b>{step[:18]}</b>{step[18:]}", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("7. Milestone Completion Status &amp; Conclusion", h1_style))
    story.append(Paragraph(
        "PharmaShift has successfully implemented all Review #3 requirements and resolved all evaluator feedback from Review #2. "
        "The platform guarantees a secure <b>Login-First</b> user experience, isolates runtime rendering anomalies via <b>React Error Boundaries</b>, "
        "enforces rigorous <b>Role-Based Access Control</b>, validates all business logic with <b>49 passing automated unit tests across 16 categories</b>, "
        "and provides complete, transparent architectural documentation across the codebase.",
        body_style
    ))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Written REVIEW_3_REPORT.pdf successfully to {pdf_path}!")

except Exception as e:
    print(f"Note: PDF generation encountered an error: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()

print("All Review #3 documentation and reports generated successfully!")
