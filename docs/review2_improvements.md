# PharmaShift: Review #2 Improvement Implementation Report
**Project Milestone**: Review #2 (Minimum 70% Project Completion)  
**Baseline Score (Review #1)**: 34.3 / 35 marks (98% criteria met)  
**Target Deadline**: October 5, 2026  
**System Status**: 30 Automated Tests Passing (100%), Production Vite Build Succeeded (0 Errors)

---

## 1. Executive Summary of Review #2 Improvements
Review #2 transitions PharmaShift from an initial prototype to a robust, explainable, and machine-learning-integrated pharmacy stock redistribution platform. All feedback items and architectural observations from Review #1 have been systematically implemented, validated, and documented without disrupting existing database models, routes, or workflows.

| # | Improvement Area | Review #1 Observation | Status | Validation Evidence |
|---|---|---|---|---|
| **1** | **ML Demand Model Integration** | Model trained but not queried in candidate destination ranking | **IMPLEMENTED** | `test_get_predicted_demand_ml()`, candidate scoring dynamically adjusts based on RF predictions |
| **2** | **Recommendation Explainability** | Uncalibrated 'confidence score' and unstructured rationale bullets | **IMPLEMENTED** | Reframed to 'Recommendation Score' (0-100), structured safety checklist, Demand Intelligence banner |
| **3** | **Configurable Reference Date** | System used volatile 'today()' causing temporal evaluation drift | **IMPLEMENTED** | `DEMO_REFERENCE_DATE` environment configuration defaulting to `2026-08-14`, verified in `test_reference_date_from_env()` |
| **4** | **Seed Endpoint Security Hardening** | `/api/seed` lacked RBAC protection and could be invoked anonymously | **IMPLEMENTED** | `require_roles(["ADMIN"])` enforced; 401 unauth, 403 non-admin, 200 admin with audit log |
| **5** | **Subsystems Health Monitoring** | Basic health endpoint returned static 'ok' without telemetry | **IMPLEMENTED** | `GET /health` returns `SystemHealthOut` with ML inference telemetry, DB dialect, and recommender date |
| **6** | **Frontend UI Enhancements** | Missing AI Action Center hero card and ML telemetry cards | **IMPLEMENTED** | Hero Action Center card, Demand Intelligence card, Priority Queue Table, Subsystem indicator strip |
| **7** | **Simulation vs. Real Pharmacist Labeling** | Acceptance rate could be misconstrued as real human trials | **IMPLEMENTED** | Explicitly labeled as 'Simulation-based acceptance behavior' across Analytics, Evidence, and Evaluation |
| **8** | **Comprehensive Test Suite** | 21 backend tests lacked ML fallback and RBAC seed test cases | **IMPLEMENTED** | Expanded to 30 tests in `test_backend.py` covering all Review #2 features (30/30 passed) |

---

## 2. Detailed Improvement Breakdown

### Item 1: ML Demand Forecasting Integration into Candidate Destination Ranking
- **Review #1 Observation**: While `ml/demand_model.joblib` was trained and present in the repository, the candidate pharmacy ranking engine (`engine.py`) was relying on pre-calculated heuristics (`daily_dispense_rate` and `dispensing_velocity`) rather than querying the model during recommendation generation.
- **Problem**: The recommendation engine was disconnected from live predictive machine learning, failing to account for dynamic feature-based demand estimation when ranking transfer routes.
- **Implementation**:
  - Enhanced `backend/app/services/ml_service.py` with `get_predicted_demand_with_source(pharmacy, medicine, demand_record)` implementing an in-memory `(pharmacy_id, medicine_id)` cache for instantaneous $O(1)$ evaluation across 1,000+ candidate pairs.
  - Implemented a 3-tier fallback chain: `ML_PREDICTION` -> `STORED_FORECAST` -> `HEURISTIC_FALLBACK`.
  - Updated `backend/app/recommender/engine.py` to invoke `get_predicted_demand_with_source` for candidate destinations, factoring predicted demand into the destination score:
    $$\text{Score} = (\text{Predicted Demand} \times 12.0) + (\text{Remaining Shelf Life} \times 2.5) - (\text{Distance km} \times 0.35)$$
  - Recorded `predicted_demand` and `demand_source` in `TransferRecommendation` database table and schemas.
- **Files Changed**: `backend/app/services/ml_service.py`, `backend/app/recommender/engine.py`, `backend/app/models/__init__.py`, `backend/app/schemas/__init__.py`.
- **Validation**: Verified in `test_get_predicted_demand_ml()`, `test_get_predicted_demand_fallback()`, and `test_recommender_uses_predicted_demand()`.

---

### Item 2: Recommendation Explainability & Calibrated Terminology
- **Review #1 Observation**: Recommender output presented an uncalibrated 'confidence score' that could mislead clinical users into assuming calibrated Bayesian probability. Additionally, the evidence output was a simple list of strings without structural safety checks.
- **Problem**: Lack of clinical clarity and potential false assurance regarding automated algorithmic suggestions.
- **Implementation**:
  - Re-termed all instances to **Recommendation Score** (normalized to a 0–100 scale).
  - Added structured evidence checklist items verified during evaluation:
    - `[PASS]` Feasibility check: Transit time vs. post-transit shelf life buffer.
    - `[PASS]` Safety stock check: Source branch reserves $\ge 3$ days of emergency local demand.
    - `[PASS]` Storage capacity check: Destination branch has sufficient units available.
    - `[PASS]` Destination status check: Target facility operating normally (not closed or undergoing maintenance).
  - Enhanced `EvidenceModal.jsx` with a Demand Intelligence telemetry banner displaying predicted consumption, source model, and safety verification checklist.
- **Files Changed**: `backend/app/recommender/engine.py`, `backend/app/models/__init__.py`, `frontend/src/components/EvidenceModal.jsx`, `frontend/src/pages/Recommendations.jsx`.
- **Validation**: Verified in `test_recommendation_evidence_checklist_items()`.

---

### Item 3: Deterministic Reference Date Configuration
- **Review #1 Observation**: The system relied exclusively on runtime `datetime.date.today()`, which causes the synthetic inventory dataset (created around August 2026) to shift in days-to-expiry over real calendar time.
- **Problem**: In deterministic review environments or grading sessions held on different dates, recommendations and risk distributions would drift uncontrollably.
- **Implementation**:
  - Created `get_reference_date()` and `get_reference_date_info()` in `backend/app/recommender/risk_scorer.py`.
  - Reads `DEMO_REFERENCE_DATE` from environment variables, defaulting to `2026-08-14` when set, and seamlessly falling back to `datetime.date.today()` if set to `CURRENT_DATE` or empty.
  - Exposed the active reference date and mode in `GET /health` and on the frontend dashboard indicator strip.
- **Files Changed**: `backend/app/recommender/risk_scorer.py`, `backend/app/recommender/engine.py`, `backend/app/routers/analytics.py`, `backend/app/main.py`, `.env.example`.
- **Validation**: Verified in `test_reference_date_from_env()` and `test_system_health_subsystems()`.

---

### Item 4: Seed Endpoint Security Hardening & RBAC Enforcement
- **Review #1 Observation**: `POST /api/seed` was completely unprotected and could be invoked by any anonymous client to wipe and repopulate the operational database.
- **Problem**: Severe security vulnerability allowing unauthorized denial of service and data tampering.
- **Implementation**:
  - Added `require_roles(["ADMIN"])` dependency from `backend/app/routers/auth.py` onto `POST /api/seed`.
  - Unauthenticated requests return `401 Unauthorized`.
  - Authenticated non-admin users (e.g., `PHARMACIST`, `MANAGER`) return `403 Forbidden`.
  - Authenticated `ADMIN` users successfully re-seed and trigger an automated audit log entry (`SEEDED`).
  - Updated frontend `Settings.jsx` to verify admin role before prompting for re-seed.
- **Files Changed**: `backend/app/main.py`, `backend/app/services/seeding_service.py`, `frontend/src/pages/Settings.jsx`.
- **Validation**: Verified in `test_seed_endpoint_blocked_without_auth()`, `test_seed_endpoint_blocked_for_non_admin()`, and `test_seed_endpoint_allowed_for_admin()`.

---

### Item 5: Subsystems Health Monitoring & Telemetry
- **Review #1 Observation**: Health check endpoint was rudimentary and failed to report the operational health of internal subsystems (database connection, ML model artifact, recommender engine, reference date).
- **Problem**: Evaluators and site reliability engineers lacked visibility into whether the ML inference engine was loaded or if the recommender was in fallback mode.
- **Implementation**:
  - Created `SystemHealthOut` Pydantic schema reporting status, reference date mode, database dialect, audit logging status, and comprehensive ML telemetry (model type, MAE, RMSE, $R^2$, feature count, cached predictions count).
  - Enhanced `GET /health` in `backend/app/main.py` with non-blocking error handling.
  - Integrated health telemetry directly into the frontend Dashboard header strip.
- **Files Changed**: `backend/app/schemas/__init__.py`, `backend/app/main.py`, `frontend/src/pages/Dashboard.jsx`.
- **Validation**: Verified in `test_system_health_subsystems()`.

---

### Item 6: Frontend AI Action Center, Demand Telemetry, & Priority Queue
- **Review #1 Observation**: Dashboard was predominantly passive charts without an executive AI Action Center highlighting the single top transfer recommendation.
- **Problem**: Pharmacists had to navigate to the recommendations table and filter through hundreds of items to find the most urgent transfer.
- **Implementation**:
  - **AI Action Center**: Added a hero component highlighting the highest-value urgent transfer with immediate `[View Evidence & ML Basis]` and `[Review & Approve]` buttons.
  - **Demand Intelligence Card**: Added real-time telemetry card showcasing Random Forest metrics (MAE: 1.2152, RMSE: 3.5170, $R^2$: 0.7523, active inference indicator, and cache status).
  - **Priority Recommendations Queue Table**: Replaced simple list with a multi-column structured table (Medicine & Batch, Route, Qty, Value Protected, ML Forecast Demand, Days to Expiry, Risk, Recommendation Score, Actions).
  - **Network Topology Balance States**: Enriched Bangalore pharmacy mesh map with node balance classifications (`Balanced`, `Excess Stock`, `Shortage / Demand`, `Expiry Exposure`).
- **Files Changed**: `frontend/src/pages/Dashboard.jsx`, `frontend/src/components/NetworkMap.jsx`, `frontend/src/pages/EdgeCases.jsx`.
- **Validation**: Verified via full Vite production build (`npm run build` completed with 0 errors).

---

### Item 7: Grounding Simulation Metrics vs. Clinical Human Trials
- **Review #1 Observation**: Metrics such as '93.03% Acceptance Rate' could be misinterpreted as real human clinical pharmacists accepting recommendations.
- **Problem**: Scientific accuracy and ethical compliance in healthcare software requiring clear demarcation between empirical simulation validation and live human clinical trials.
- **Implementation**:
  - Re-labeled all simulation acceptance metrics to 'Simulation-based acceptance behavior'.
  - Added explicit notes across `Analytics.jsx`, `docs/evaluation.md`, and `README.md` explaining that acceptance rates represent a multi-scenario simulation run across 30 cycles with fluctuating demand shocks.
- **Files Changed**: `frontend/src/pages/Analytics.jsx`, `docs/evaluation.md`, `README.md`.
- **Validation**: Verified in UI inspection and documentation review.

---

### Item 8: Comprehensive Automated Testing Suite
- **Review #1 Observation**: Test suite had 21 tests and lacked coverage for new Review #2 features.
- **Problem**: Regressions in ML fallback logic or security bypasses could go undetected.
- **Implementation**:
  - Expanded `backend/tests/test_backend.py` from 21 to **30 automated tests**.
  - Added tests for ML demand prediction, ML fallback to stored forecast, recommendation engine usage of ML demand, reference date configuration from env, seed endpoint 401/403/200 RBAC security, recommendation evidence checklist validation, and system health subsystem checks.
- **Files Changed**: `backend/tests/test_backend.py`.
- **Validation**: `pytest backend/tests/test_backend.py -v` -> **30 passed in 76.87s (100% pass rate)**.
