# Pharmacy Stock Redistribution & Recommendation System
## Product Name: PharmaShift – Expiry-Aware Pharmacy Network Optimizer
### Project Review #2 Report — Minimum 70% Project Completion Milestone

---

## 1. TITLE PAGE

| Project Metadata | Specification |
|---|---|
| **Project Title** | Pharmacy Stock Redistribution & Recommendation System |
| **Product Name** | PharmaShift – Expiry-Aware Pharmacy Network Optimizer |
| **Review Milestone** | Project Review #2 |
| **Completion Target** | Minimum 70% Project Completion (Evaluated at **78.5%**) |
| **Previous Milestone** | Review #1 – 35% Milestone |
| **Review #1 Score** | **34.3 / 35 marks (98% criteria met)** |
| **Report Date** | September 28, 2026 |
| **Target Submission Deadline** | October 5, 2026 |
| **Academic Department** | Department of Computer Science & Engineering / Information Technology |
| **Student Name(s)** | [Student Name(s) Placeholder] |
| **Register / Roll Number(s)**| [Register / Roll Number(s) Placeholder] |
| **Project Supervisor / Guide**| [Project Supervisor Name Placeholder] |
| **Academic Year** | 2026 – 2027 |

---

## 2. EXECUTIVE SUMMARY

PharmaShift is an AI-assisted pharmacy stock redistribution and recommendation decision-support platform designed to address the critical pharmaceutical logistics problem of near-expiry inventory loss, localized stockouts, and inter-branch inventory imbalances across multi-branch pharmacy networks. 

In traditional retail pharmacy networks, individual branches operate as isolated inventory silos. Medicines approaching their expiration dates frequently sit unconsumed in low-velocity suburban branches, leading to complete capital loss and hazardous chemical destruction, while central hospital or urban branches simultaneously face critical stockouts for those exact medications. PharmaShift bridges this gap through an end-to-end algorithmic and machine-learning-driven pipeline that:
1. Continuously tracks inventory batches across 18 metropolitan pharmacy branches.
2. Identifies batches approaching expiry and computes accurate local excess after strictly reserving a mandatory 3-day patient emergency safety stock buffer.
3. Ingests a pre-trained **Random Forest regression model** (`ml/demand_model.joblib`) to forecast destination dispensing velocity ($MAE=1.2152$ units/day, $R^2=0.7523$).
4. Evaluates road transit distances and clinical feasibility constraints (ensuring transferred medications arrive with at least 3 days of consumable shelf-life post-transit).
5. Ranks suitable candidate destination pharmacies and determines the optimal, capacity-constrained transfer quantity.
6. Generates factual, transparent evidence bullets with a normalized **Recommendation Score (0–100)** to eliminate uncalibrated probability claims.
7. Enforces a human-in-the-loop clinical governance workflow (Approval, Rejection with structured reasons, and Quantity Override with live value recalculation) supported by an immutable compliance audit trail.

### Progress to the Review #2 Milestone (78.5% Completion):
Following the completion of Review #1 (35% milestone, evaluated at **34.3 / 35 marks**), the project has advanced to **78.5% overall project completion**, exceeding the mandatory 70% threshold required for Review #2. This 78.5% milestone represents a fully functional, integrated system verified by:
- **30 automated unit and integration tests** passing with a 100% pass rate.
- **A production Vite frontend bundle** compiling with zero warnings and zero errors across 2,353 modules.
- **Live backend and frontend services** running concurrently with full telemetry.
- **Empirical simulation validation** across 30 scenarios demonstrating a **+₹7,44,001.15 (+9.88%)** net value gain and a **52.09% reduction** in expired stock waste compared to a naive FIFO baseline.

---

## 3. PROBLEM STATEMENT

Multi-branch pharmacy networks in urban metropolitan regions face persistent operational challenges arising from decoupled inventory management:
- **Near-Expiry Capital Destruction**: Substantial quantities of pharmaceutical stock expire on branch shelves due to localized demand slowdowns, seasonality shifts, or over-procurement.
- **Concurrent Stock Imbalances & Shortages**: While one suburban clinic branch holds an unconsumable surplus of near-expiry antibiotics, a downtown trauma center branch experiences severe stockouts for the same formulation.
- **Transit and Logistics Friction**: Ad-hoc transfers arranged manually frequently fail because medications arrive after or immediately prior to expiration, failing to account for road transit time and mandatory shelf-life buffers.
- **Safety-Stock Depletion Risk**: Naive redistribution risks stripping a donor pharmacy of its emergency buffer, leaving local patients vulnerable to acute stockouts.
- **Cognitive Overload and Audit Deficits**: Pharmacy managers lack automated tooling to identify excess stock in time, evaluate candidate branches, and document the regulatory compliance rationale behind transfers.

PharmaShift resolves this multifaceted supply chain bottleneck through an integrated decision framework:
$$	ext{Demand Prediction (ML)} + 	ext{Expiry Risk Scoring} + 	ext{Safety Buffer Protection} + 	ext{Transit Feasibility} + 	ext{Destination Ranking} + 	ext{Human Governance}$$

---

## 4. PROJECT OBJECTIVES

The core objectives of the PharmaShift project are:
1. **Monitor Multi-Branch Inventory**: Ingest and track pharmaceutical batches across a distributed multi-branch network.
2. **Detect Expiry Risk Deterministically**: Quantify remaining Days-to-Expiry ($DTE$) against a configurable reference date and classify risk levels ($Expired$, $Critical$, $High$, $Medium$, $Low$).
3. **Compute Real Local Surplus**: Calculate excess stock mathematically after protecting a mandatory 3-day local patient safety buffer.
4. **Predict Local Dispensing Demand**: Utilize a trained Machine Learning model to forecast daily consumption rates at candidate destination pharmacies.
5. **Enforce Transit Feasibility Constraints**: Calculate Haversine transit distances and block transfers where transit duration leaves less than 3 days of usable post-arrival shelf-life.
6. **Screen Facility Operational Status**: Automatically block transfers to destination branches that are closed or undergoing maintenance.
7. **Rank Destination Candidates Algorithmically**: Dynamically score candidate branches based on ML predicted demand, remaining shelf life, and distance penalties.
8. **Size Optimal Transfer Quantities**: Constrain transfer batches by donor excess, destination absorption window, and physical destination storage capacity.
9. **Calculate Protected Monetary Value**: Quantify the monetary value saved from impending expiry waste.
10. **Flag High-Impact Transfers**: Require human escalation for transfers exceeding ₹2,000, 50 units, or urgent expiry windows ($\le 14$ days).
11. **Provide Explainable Recommendation Evidence**: Deliver transparent factual rationale and safety checklist bullets for every recommendation.
12. **Enable Human Decision Workflows**: Allow authorized pharmacists to approve, reject with structured reason categories, or override quantities.
13. **Maintain Immutable Compliance Audit Records**: Record every user interaction, state transition, quantity modification, and dispatch rationale.
14. **Empirically Benchmark Against Baseline**: Quantify economic improvement over an isolated FIFO baseline across 30 multi-scenario simulation cycles.
15. **Deliver an Executive Monitoring Dashboard**: Provide real-time KPI visualization, spatial logistics mesh mapping, and subsystem telemetry.

---

## 5. SYSTEM OVERVIEW

PharmaShift operates as a multi-tier service architecture comprising a persistent relational database, a machine learning inference module, an asynchronous recommendation engine, an authenticated REST API gateway, and a responsive single-page web dashboard:

```
                            +-----------------------------------+
                            |     Synthetic Operational Data    |
                            | (5,193 Batches, 18 Branches, 60M) |
                            +-----------------+-----------------+
                                              |
                                              v
                            +-----------------+-----------------+
                            |       SQLAlchemy ORM Layer        |
                            |   (SQLite / PostgreSQL Dual Mode) |
                            +--------+-----------------+--------+
                                     |                 |
                   +-----------------+                 +-----------------+
                   v                                                     v
   +---------------+---------------+                     +---------------+---------------+
   |      ML Demand Service        |                     |      Expiry Risk Scorer       |
   | - RandomForestRegressor       |                     | - Days-to-Expiry Math         |
   | - 11 Engineered Features      |                     | - Fixed Demo Ref Date         |
   | - (pharm, med) In-Memory Cache|                     | - Risk Tiering Classification |
   +---------------+---------------+                     +---------------+---------------+
                   |                                                     |
                   +-----------------+                 +-----------------+
                                     |                 |
                                     v                 v
                            +--------+-----------------+--------+
                            |      Recommendation Engine        |
                            | - Excess Calculation (Buffer)     |
                            | - Haversine Transit Feasibility   |
                            | - Destination Ranking Formula     |
                            | - Optimal Quantity Allocation     |
                            +-----------------+-----------------+
                                              |
                                              v
                            +-----------------+-----------------+
                            | Explainable Evidence & Scoring    |
                            | - Recommendation Score (0-100)    |
                            | - Safety Checklist Verification   |
                            +-----------------+-----------------+
                                              |
                                              v
                            +-----------------+-----------------+
                            |   Human-in-the-Loop Governance    |
                            | - Approve / Reject / Override     |
                            | - Structured Reason Categories    |
                            +-----------------+-----------------+
                                              |
                                              v
                            +-----------------+-----------------+
                            | Immutable Compliance Audit Trail  |
                            | - Actor, Role, Previous/New State |
                            +-----------------+-----------------+
                                              |
                                              v
                            +-----------------+-----------------+
                            |      React 18 Dashboard UI        |
                            | - AI Action Center & Telemetry    |
                            | - Spatial Network Topology Mesh   |
                            +-----------------------------------+
```

---

## 6. TECHNOLOGY STACK

PharmaShift utilizes modern open-source technologies verified in the current codebase:

### Table 5: Technology Stack
| Architectural Layer | Technology / Library | Version | Purpose in PharmaShift |
|---|---|---|---|
| **Frontend Framework** | React | 18.2.0 | Reactive component architecture, virtual DOM rendering, and single-page routing |
| **Frontend Build Tool** | Vite | 5.4.21 | Lightning-fast HMR and optimized production asset bundling |
| **CSS & Design System** | Tailwind CSS | 3.4.1 | Utility-first responsive styling and consistent dark-mode theme |
| **Iconography** | Lucide React | 0.359.0 | Clinical, supply chain, and telemetry interface icons |
| **Data Visualization** | Recharts | 2.12.3 | Responsive SVG charting for KPI trends, risk breakdowns, and scenario comparisons |
| **HTTP Client** | Axios | 1.6.8 | Promise-based API communication with automatic JWT bearer token injection |
| **Backend Framework** | FastAPI | 0.110.0 | High-concurrency asynchronous REST API with automatic OpenAPI documentation |
| **ASGI Server** | Uvicorn | 0.28.0 | Production ASGI server powering the FastAPI asynchronous backend |
| **ORM / Database Abstraction** | SQLAlchemy | 2.0.28 | Object-relational mapping with dual support for SQLite and PostgreSQL |
| **Data Validation** | Pydantic | 2.6.4 | Strict schema validation, serialization, and type enforcement |
| **Database Engine** | SQLite3 / PostgreSQL | 15 (Docker) | Relational persistence for inventory, users, recommendations, and audit logs |
| **Machine Learning** | scikit-learn | 1.4.1.post1 | Random Forest regression modeling, feature extraction, and model persistence |
| **Numerical Computing** | NumPy & Pandas | 1.26.4 / 2.2.1 | Matrix operations, rolling statistics, and feature matrix preparation |
| **Model Persistence** | joblib | 1.3.2 | Fast serialization and deserialization of the trained Random Forest model |
| **Authentication & Security** | PyJWT & bcrypt | 2.8.0 / 4.1.2 | Stateless JWT token issuance, verification, and salted password hashing |
| **Automated Testing** | pytest & httpx | 8.1.1 / 0.27.0 | Test automation framework and ASGI TestClient for API endpoint verification |
| **Containerization** | Docker & Docker Compose | 3.8 Spec | Multi-container orchestration (FastAPI backend, React frontend, PostgreSQL) |

---

## 7. PROJECT DEVELOPMENT PROGRESS

The project development roadmap is structured into 10 cohesive engineering phases:

### Table 1: Project Milestones
| Milestone Phase | Major Functional Scope | Implementation Details | Status |
|---|---|---|---|
| **Phase 1: Project Foundation** | Problem definition, dataset synthesis, schema design | Formulated mathematical excess formulas; generated 5,193 synthetic batches across 18 branches and 60 medicines | **Completed** |
| **Phase 2: Database & Backend** | Relational schemas, dual dialect setup, FastAPI core | Created 10 SQLAlchemy models, SessionLocal engine, and Lifespan auto-seeding logic | **Completed** |
| **Phase 3: Inventory & Network** | Branch coordinates, GPS distance calculation | Implemented Haversine distance utility, inventory batch filtering, and branch status validation | **Completed** |
| **Phase 4: Recommendation Engine** | Expiry risk detection, excess stock calculation | Implemented Days-to-Expiry math, 3-day safety buffer protection, and feasibility filters | **Completed** |
| **Phase 5: ML Demand Prediction** | Demand feature engineering, model training | Trained Random Forest Regressor ($N=100$) yielding MAE 1.2152, RMSE 3.5170, $R^2$ 0.7523 | **Completed** |
| **Phase 6: ML + Recommender Integration** | Candidate destination scoring with ML predictions | Connected `ml_service.py` to `engine.py`, added memory cache, and 3-tier fallback chain | **Completed (Review #2)** |
| **Phase 7: Frontend Dashboard** | UI layout, KPI cards, charts, priority queue | Built AI Action Center, Demand Intelligence telemetry card, Priority Queue table, and Health strip | **Completed (Review #2)** |
| **Phase 8: Human-in-the-Loop & Audit** | Clinical governance, approval/rejection/override | Implemented approval checklist, mandatory structured rejection reasons, quantity overrides, and audit log | **Completed (Review #2)** |
| **Phase 9: Testing & Edge Cases** | Test automation, clinical safety sandbox | Expanded test suite to 30 tests (100% passing); built 8-scenario deterministic Edge Cases Sandbox | **Completed (Review #2)** |
| **Phase 10: Analytics & Simulation** | Multi-scenario benchmark suite | Validated 30 simulation cycles (+₹7.44L value gain, -52.09% expiry reduction across 1,794 recs) | **Completed (Review #2)** |

---

## 8. CLEAR 70% COMPLETION BREAKDOWN

PharmaShift does not measure completion using arbitrary, unverified line counts. Completion is evaluated across **16 functional operational domains** essential to healthcare logistics software:

### Table 7: 70% Completion Evidence
| Core Functional Area | Implemented Capability | Source Code / Repository Evidence | Status |
|---|---|---|---|
| **A. Project Foundation** | Mathematical excess models, synthetic data schemas | `data/synthetic_*.csv`, `ml/generate_data.py` | **100% Complete** |
| **B. Database & Data Layer** | Relational ORM models, migrations, dual database | `backend/app/models/`, `backend/app/database/` | **95% Complete** |
| **C. Inventory Management** | Real-time batch query, category and branch filtering | `backend/app/routers/inventory.py`, `Inventory.jsx` | **90% Complete** |
| **D. Pharmacy Network** | Spatial branch coordinates, transit distance routing | `backend/app/utils/distance.py`, `NetworkMap.jsx` | **85% Complete** |
| **E. Demand Prediction** | Random Forest ML forecasting (11 features) | `ml/demand_model.joblib`, `ml/train.py`, `ml_service.py` | **90% Complete** |
| **F. Recommendation Engine** | Feasibility-constrained excess redistribution | `backend/app/recommender/engine.py` | **90% Complete** |
| **G. Expiry & Safety Logic** | Safety buffer protection, post-transit life buffer | `backend/app/recommender/risk_scorer.py` | **95% Complete** |
| **H. Backend APIs** | 10 modular REST router groups with OpenAPI docs | `backend/app/routers/`, `backend/app/main.py` | **95% Complete** |
| **I. Frontend Dashboard** | AI Action Center, Demand Telemetry, Health Strip | `frontend/src/pages/Dashboard.jsx` | **85% Complete** |
| **J. Human Approval Workflow** | Approval, structured rejection, quantity override | `ApprovalModal.jsx`, `RejectModal.jsx`, `OverrideModal.jsx` | **90% Complete** |
| **K. Audit Trail & Governance**| Immutable state transitions, role tracking, notes | `backend/app/services/audit_service.py`, `AuditLogs.jsx` | **90% Complete** |
| **L. Analytics & Baseline** | 30-scenario simulation benchmark vs. isolated FIFO | `backend/app/services/simulation_service.py`, `Analytics.jsx` | **85% Complete** |
| **M. Edge Case Handling** | 8 deterministic clinical safety failure guards | `backend/app/routers/edge_cases.py`, `EdgeCases.jsx` | **90% Complete** |
| **N. Testing & Quality** | 30 comprehensive backend automated test cases | `backend/tests/test_backend.py` (30/30 passed) | **95% Complete** |
| **O. Security & RBAC** | Stateless JWT authentication, role restrictions | `backend/app/routers/auth.py`, `backend/app/utils/security.py` | **90% Complete** |
| **P. Technical Documentation** | Full architectural blueprints, ML docs, API guides | `docs/*.md`, `README.md` | **90% Complete** |

### Synthesis of the 78.5% Milestone:
These 16 functional domains represent the complete core pipeline of an intelligent healthcare redistribution platform. The project has progressed from foundational architecture to an operational, tested system. The remaining ~21.5% of work encompasses enterprise hospital ERP connectors (HL7/FHIR), multi-vehicle route optimization (CVRP), automated online retraining pipelines, and physical warehouse barcode scanner hardware integration.

---

## 9. REVIEW #1 COMPLETION

During the initial Project Review #1, PharmaShift presented its core 35% milestone prototype, achieving:
- **Official Score**: **34.3 / 35 marks**
- **Evaluation Percentage**: **98% criteria met**

The Review #1 evaluation committee acknowledged the following foundational strengths:
- A clean, modular FastAPI backend utilizing SQLAlchemy ORM with dual SQLite and PostgreSQL support.
- Initial API routers covering authentication, inventory, pharmacies, and recommendations.
- Mathematical formulations for expiry-risk scoring and 3-day local safety-stock reservation.
- Haversine pairwise distance calculations and basic road transit duration estimation.
- A standalone trained Random Forest demand forecasting model (`demand_model.joblib`) with low MAE (~1.22 units/day).
- An initial React 18 single-page application showcasing batch monitoring and transfer routes.
- A suite of 21 automated backend tests validating core mathematical routines and authentication.

---

## 10. IMPROVEMENTS AFTER REVIEW #1

### Table 2: Review #1 vs Review #2 Improvements
| Improvement Area | Review #1 State | Review #2 Implemented State | Nature of Improvement |
|---|---|---|---|
| **A. ML Demand Integration** | Model trained but not queried in candidate destination ranking | `ml_service.py` actively queries Random Forest model during recommendation generation | Destination ranking is dynamically weighted by live predictive ML demand |
| **B. Recommendation Explainability** | Generic bulleted text without structured validation | Structured Safety & Feasibility checklist (`[PASS]` Feasibility, Buffer, Capacity, Node Status) | Factual, auditable verification bullets displayed in modal |
| **C. Scoring Terminology** | Uncalibrated \'confidence score\' resembling Bayesian probability | Calibrated **Recommendation Score (0–100 scale)** | Mathematically normalized score eliminating misleading probability claims |
| **D. Seed Endpoint Security** | `POST /api/seed` was public and could be invoked anonymously | Strictly guarded by `require_roles(["ADMIN"])` | Returns 401 unauth, 403 non-admin, 200 admin with audit log |
| **E. RBAC Consistency** | Audit logs had partial role checks | Enforced across all administrative endpoints; Pharmacist restricted to branch | Strict role segregation (`ADMIN`, `MANAGER`, `PHARMACIST`) |
| **F. Secret & Env Hardening** | Default secrets lacked production warnings | Added production insecure-key detection and UTC timezone standardization | Security hardening against unauthorized token forging |
| **G. Configurable Reference Date** | Used runtime `today()`, causing temporal evaluation drift | `DEMO_REFERENCE_DATE` environment configuration defaulting to `2026-08-14` | 100% deterministic test execution and reproducibility |
| **H. Test Suite Expansion** | 21 test cases covering basic logic | **30 test cases** covering ML inference, fallback chains, seed security, ref dates | 100% test pass rate verifying all Review #2 features |
| **I. Documentation Synchronization** | Metrics varied across markdown files | Synchronized all docs with `data/simulation_results.json` as single source of truth | Truthful reporting (10.27 km, 19.41 days, 1,794 recs) |
| **J. Dashboard Architecture** | Simple KPI cards and basic charts | Added AI Action Center hero card, Demand Intelligence card, Priority Queue Table | Actionable clinical decision support at top of dashboard |

---

## 11. MACHINE LEARNING IMPLEMENTATION

### Problem Formulation
Pharmaceutical demand exhibits localized volatility. To prevent stock from being transferred to branches unable to dispense it, PharmaShift deploys a supervised **Random Forest Regressor** to predict the expected daily dispensing rate ($\hat{y}_{p, m}$) for medicine $m$ at candidate branch $p$.

```
[Branch Historical Dispensation Data]
                  │
                  ▼
      [11 Engineered Features]
                  │
                  ▼
     [Random Forest Regressor]
   (100 Trees, Max Depth 10)
                  │
                  ▼
     [Predicted Daily Demand]
```

### Table 4: ML Model Metrics
| Metric Name | Value | Source / Verification Artifact | Operational Meaning |
|---|---|---|---|
| **Mean Absolute Error (MAE)** | **1.2152 units/day** | `ml/model_metrics.json` | Daily demand prediction deviates by only ~1.2 units on average |
| **Root Mean Squared Error (RMSE)**| **3.5170 units/day** | `ml/model_metrics.json` | Variance in prediction errors is strictly controlled |
| **R² Goodness of Fit** | **0.7523** | `ml/model_metrics.json` | **75.23% of total demand variance** across branches is explained |
| **Estimators ($N$)** | 100 | `ml/demand_model.joblib` | Ensemble size ensuring robust generalization |
| **Maximum Tree Depth** | 10 | `ml/train.py` | Constrained depth preventing overfitting |
| **Training Records** | 1,080 profiles | `data/synthetic_demand.csv` | Full coverage across 18 pharmacies and 60 medicines |

### Engineered Features & Importances:
1. `weekly_avg_daily` (**42.1%**): 7-day rolling dispensing pace.
2. `monthly_avg_daily` (**28.4%**): 30-day baseline pace.
3. `storage_capacity` (**14.2%**): Physical footprint of receiving pharmacy.
4. `unit_price` (**9.1%**): Commercial value per unit.
5. `daily_dispense_rate` (**3.8%**): Historical average demand.
6. `demand_volatility` (**1.2%**): Variance in daily consumption.
7. `days_to_expiry` (**0.6%**): Remaining shelf life of incoming batch.
8. `category_encoded` (**0.3%**): Therapeutic category encoding.
9. `city_encoded` (**0.2%**): Bangalore urban zone encoding.
10. `is_life_saving` (**0.1%**): Emergency critical drug indicator.
11. `lead_time_days` (**0.1%**): Supplier replenishment lead time.

---

## 12. ML + RECOMMENDATION INTEGRATION

In Review #2, the recommendation engine directly queries the ML demand model during candidate destination ranking:

```
[Candidate Destination Pharmacy p & Medicine m]
                       │
                       ▼
         Check In-Memory Cache?
          ├── YES ──> Return cached prediction (O(1))
          └── NO  ──> Prepare 11-feature vector
                       │
                       ▼
                 Is Model Loaded?
                  ├── YES ──> rf_model.predict(X) [Source: ML_PREDICTION]
                  └── NO  ──> Stored demand forecast [Source: STORED_FORECAST]
                               └── Missing? ──> Heuristic fallback [Source: HEURISTIC_FALLBACK]
```

### Destination Ranking Score Formulation:
$$	ext{Score}(p) = (\hat{y}_{p, m} 	imes 12.0) + (	ext{Remaining Post-Transit Life} 	imes 2.5) - (	ext{Distance km} 	imes 0.35)$$

- **Predicted Demand Factor ($	imes 12.0$)**: Strongly prioritizes pharmacies capable of rapidly dispensing the transferred batch.
- **Shelf Life Factor ($	imes 2.5$)**: Favors transfers where medications arrive with ample usable shelf-life.
- **Distance Penalty ($-0.35$ per km)**: Penalizes excessive transit distances across urban Bangalore.

### Sub-Millisecond In-Memory Caching:
Evaluating all 18 branches for 5,000+ batches would require 90,000 model queries, resulting in 40+ seconds of latency. PharmaShift implements an in-memory cache keyed by `(pharmacy_id, medicine_id)` in `_prediction_cache`, capping model calls to at most 1,080 unique pairs and reducing full network recommendation generation to **under 3 seconds**.

---

## 13. RECOMMENDATION ENGINE

The recommendation generation follows a strict 5-step mathematical procedure:

### Step 1: Days to Expiry ($DTE$)
$$DTE = 	ext{Batch Expiry Date} - 	ext{Reference Date (2026-08-14)}$$

### Step 2: Local Consumption & Excess Stock
$$	ext{Local Need} = 	ext{Daily Dispense Rate} 	imes DTE$$
$$	ext{Safety Buffer} = 	ext{Daily Dispense Rate} 	imes 3 	ext{ days}$$
$$	ext{Excess Stock} = \max(0, 	ext{Batch Quantity} - 	ext{Local Need} - 	ext{Safety Buffer})$$
*If $	ext{Excess Stock} \le 0$, the batch is retained locally and no transfer is generated.*

### Step 3: Feasibility & Safety Constraints
For every candidate destination branch $p$:
- **Status Check**: $p$ must be `ACTIVE` (branches in `MAINTENANCE` or `CLOSED` are rejected).
- **Haversine Distance**:
  $$d = 2R rcsin\left(\sqrt{\sin^2\left(rac{\Delta \phi}{2}ight) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(rac{\Delta \lambda}{2}ight)}ight)$$
- **Transit Duration**: $T_{	ext{transit}} = \max(1, \lceil d / 50 ceil)$ days.
- **Feasibility Constraint**:
  $$DTE - T_{	ext{transit}} \ge 3 	ext{ days post-arrival}$$
  *Transfers arriving with $<3$ days of usable shelf-life are blocked.*

### Step 4: Transfer Quantity Allocation
$$Q^* = \min(	ext{Excess Stock}, \hat{y}_{p, m} 	imes (DTE - T_{	ext{transit}}), 	ext{Destination Storage Capacity})$$

### Step 5: Economic Valuation & High-Impact Flag
$$	ext{Potential Value Protected} = Q^* 	imes 	ext{Medicine Unit Price (INR)}$$
A transfer is flagged as **High-Impact** if:
$$	ext{Value Protected} \ge ₹2,000 \quad	ext{OR}\quad Q^* \ge 50 	ext{ units}\quad	ext{OR}\quad DTE \le 14 	ext{ days}$$

---

## 14. EXPLAINABLE AI RECOMMENDATIONS

To ensure clinical trustworthiness, PharmaShift answers *"Why is this transfer recommended?"* using factual, transparent evidence:

1. **Calibrated Recommendation Score**: Displayed on a 0–100 normalized scale, eliminating uncalibrated probability assumptions.
2. **Demand Intelligence Telemetry Banner**: Displays the destination predicted daily consumption rate ($\hat{y}$ units/day) and the active demand source (`ML_PREDICTION`).
3. **Safety & Feasibility Verification Checklist**:
   - `[PASS]` Feasibility check: Transit time leaves $\ge 3$ days post-arrival buffer.
   - `[PASS]` Safety stock check: Source branch reserves $\ge 3$ days emergency local demand.
   - `[PASS]` Storage capacity check: Destination branch has sufficient physical units available.
   - `[PASS]` Operational status check: Target facility operating normally.

---

## 15. FRONTEND / DASHBOARD

The frontend provides an intuitive clinical interface across 9 distinct functional views:

Figure 1 – System Dashboard  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays Subsystems Health Strip, AI Action Center hero card, Demand Intelligence telemetry card, KPI summary cards, Near-Expiry bar chart, Risk pie chart, and Priority Queue Table.*

Figure 2 – Inventory Monitor  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays searchable, paginated inventory batches across 18 branches with days-to-expiry badges, safety buffers, and risk categorizations.*

Figure 3 – AI Recommendation  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays pending redistribution routes, donor excess, destination demand, distance in km, transit days, potential value protected, and action buttons.*

Figure 4 – Recommendation Evidence  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays the Evidence Modal showing the 0–100 Recommendation Score, Demand Intelligence banner, and Safety Verification checklist.*

Figure 5 – ML Demand Evaluation  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays the Demand Intelligence telemetry card showing Random Forest MAE, RMSE, R², feature importances, and active inference status.*

Figure 6 – Analytics / Baseline  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays the 30-scenario simulation benchmark comparing naive FIFO baseline vs. proposed recommender (+₹7.44L gain, 93.03% simulation acceptance).*

Figure 7 – Edge Case Sandbox  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays live verification of all 8 clinical safety edge cases with input conditions, expected vs actual results, safety rules, and deterministic PASS badges.*

Figure 8 – Audit Trail  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays filterable compliance audit logs tracking timestamp, user email, assigned role, state transitions, quantities, and dispatch notes.*

Figure 9 – Pharmacy Network  
`[INSERT ACTUAL SCREENSHOT]`  
*Displays the Bangalore spatial logistics mesh map with active transfer vectors and real-time node balance states (Balanced, Excess, Shortage, Exposure).*

---

## 16. HUMAN-IN-THE-LOOP WORKFLOW

PharmaShift operates as a clinical decision-support tool; it **never executes transfers automatically without human authorization**:

```
[Recommendation Generated (Status: PENDING)]
                    │
                    ▼
       Pharmacist Reviews Evidence
                    │
       +------------+------------+
       |            |            |
       v            v            v
   [Approve]     [Reject]    [Override]
       │            │            │
       │            │            └── Pharmacist adjusts quantity (e.g., 50 -> 25 units)
       │            │                System recalculates value protected live
       │            │                Selects reason: STORAGE_CONSTRAINT
       │            │
       │            └── Pharmacist rejects transfer
       │                Must select mandatory category:
       │                - STOCK_COUNT_MISMATCH
       │                - LOCAL_PROMOTION_PLANNED
       │                - SUSPECTED_CONTAMINATION
       │
       └── Pharmacist confirms dispatch
           If High-Impact, confirms acknowledgment checklist
                    │
                    ▼
     [Immutable Audit Log Committed]
```

---

## 17. SECURITY AND RBAC

Security is built into every layer of the API and database:
1. **Stateless JWT Authentication**: Tokens signed via HS256 with configurable expiry and secret keys.
2. **Password Security**: Standard salted `bcrypt` hashing with salt rounds.
3. **Role-Based Access Control Matrix**:
   - `ADMIN`: Global access, audit log inspection, system settings, database re-seeding.
   - `MANAGER`: Multi-branch oversight, approval/rejection/override authority, analytics access.
   - `PHARMACIST`: Scoped strictly to inventory and transfers involving their assigned branch (`PHARM-001`).
4. **Administrative Seed Hardening**: `POST /api/seed` enforces `require_roles(["ADMIN"])`. Unauthenticated requests receive `401 Unauthorized`; non-admin users receive `403 Forbidden`.

---

## 18. AUDIT TRAIL

The audit system maintains an immutable record of every write operation:
- **Timestamp**: UTC standardized timestamp.
- **Actor Email & Role**: Identity and permission scope of the acting user.
- **Action Type**: `APPROVED`, `REJECTED`, `OVERRIDDEN`, `GENERATED`, `SEEDED`.
- **Recommendation ID**: Unique reference to the underlying recommendation.
- **State Transition**: Explicit recording of state shifts (`PENDING` $	o$ `APPROVED`, `PENDING` $	o$ `OVERRIDDEN`).
- **Transfer Quantity**: Approved or overridden unit count.
- **Structured Reason & Notes**: Clinical rationale and dispatch notes.

---

## 19. EDGE CASE SAFETY

PharmaShift incorporates 8 explicit deterministic safety failure guards:

1. `INV-EDGE-001` (Transit Exceeds Shelf-Life): Remaining life post-transit is $<3$ days $	o$ **BLOCKED**.
2. `INV-EDGE-002` (No Destination Demand): Zero destination absorption capacity $	o$ **BLOCKED**.
3. `INV-EDGE-003` (Below Safety Stock Buffer): Source stock $<3$-day emergency buffer $	o$ **BLOCKED**.
4. `INV-EDGE-004` (Malformed Expiry String): Unparseable date format $	o$ **BLOCKED & LOGGED**.
5. `INV-EDGE-005` (Target Branch Closed): Destination branch in `MAINTENANCE` or `CLOSED` $	o$ **BLOCKED**.
6. `INV-EDGE-006` (Already Expired Stock): $DTE \le 0$ days $	o$ **BLOCKED & MARKED FOR DISPOSAL**.
7. `INV-EDGE-007` (Sudden Demand Collapse): Primary destination demand collapses $	o$ **AUTOMATICALLY RE-ROUTED**.
8. `INV-EDGE-008A/B` (Duplicate Manufacturer Lot): Identical lot present at two branches $	o$ **INDEPENDENTLY RESOLVED**.

All 8 edge cases pass deterministic assertions in `test_backend.py` and are visually verifiable in the frontend `EdgeCases.jsx` sandbox.

---

## 20. ANALYTICS AND BASELINE EVALUATION

To quantify performance, PharmaShift was evaluated across a **30-scenario simulation suite** (`data/simulation_results.json`) comparing:
- **Baseline Strategy (A)**: Isolated First-In, First-Out (FIFO) clearance without inter-branch stock sharing.
- **Proposed Recommender (B)**: Expiry-aware, ML-demand-ranked redistribution with feasibility constraints.

### Quantitative Benchmark Comparison:
- **Baseline Average Value Protected**: **₹75,70,344.23**
- **Proposed Recommender Value Protected**: **₹83,14,345.38**
- **Average Monetary Improvement**: **+₹7,44,001.15 (+9.88%)**
- **Average Value Lost to Expiry Reduction**: **-₹7,44,001.15 (-52.09% loss reduction)**
- **Total Recommendations Evaluated**: **1,794 transfer recommendations**
- **Average Transfer Transit Distance**: **10.27 km** (Haversine urban routes across Bangalore)
- **Average Usable Shelf Life at Transfer**: **19.41 days**
- **Simulation-Based Acceptance Rate**: **93.03%** *(Explicitly labeled as simulation-based acceptance behavior across 30 scenario cycles, not real human trials).*

---

## 21. TESTING

The test suite in `backend/tests/test_backend.py` was executed directly against the codebase:

### Table 6: Testing Summary
| Test Category | Total Tests | Passed | Failed | Test Execution Status |
|---|---|---|---|---|
| **Expiry & Days-to-Expiry Math** | 2 | 2 | 0 | **100% Passed** |
| **Risk Level Classification** | 1 | 1 | 0 | **100% Passed** |
| **Excess Stock & Safety Buffer** | 1 | 1 | 0 | **100% Passed** |
| **Haversine Distance & Transit Duration** | 2 | 2 | 0 | **100% Passed** |
| **Clinical Feasibility Failure Guards** | 4 | 4 | 0 | **100% Passed** |
| **Authentication & Password Rejection** | 2 | 2 | 0 | **100% Passed** |
| **Human Approval & High-Impact Validation**| 2 | 2 | 0 | **100% Passed** |
| **Rejection Mandatory Reason Validation** | 1 | 1 | 0 | **100% Passed** |
| **Override Quantity & Value Recalculation** | 1 | 1 | 0 | **100% Passed** |
| **Audit Logging & State Tracking** | 1 | 1 | 0 | **100% Passed** |
| **RBAC Route-Level Permissions** | 2 | 2 | 0 | **100% Passed** |
| **ML Demand Model Inference & Fallback** | 3 | 3 | 0 | **100% Passed** |
| **Recommender ML Integration** | 1 | 1 | 0 | **100% Passed** |
| **Reference Date Environment Configuration** | 1 | 1 | 0 | **100% Passed** |
| **Seed Endpoint RBAC Security (401/403/200)** | 3 | 3 | 0 | **100% Passed** |
| **Evidence Checklist Assertions** | 1 | 1 | 0 | **100% Passed** |
| **Subsystem Health Telemetry** | 1 | 1 | 0 | **100% Passed** |
| **Edge Cases Endpoint Verification** | 1 | 1 | 0 | **100% Passed** |
| **TOTAL BACKEND SUITE** | **30** | **30** | **0** | **100% PASSED (76.87s)** |

---

## 22. DATABASE AND DATA

### Database Architecture
PharmaShift implements an ORM schema supporting SQLite3 (`pharmacy_db.sqlite3`) and PostgreSQL 15:
- `users`: Authentication credentials and roles.
- `pharmacies`: 18 Bangalore branches with coordinates, capacities, and statuses.
- `medicines`: 60 pharmaceutical formulations across 10 therapeutic categories.
- `inventory_batches`: 5,193 batch records with batch codes, expiry dates, quantities, and risk levels.
- `demand_forecasts`: 1,080 historical demand records.
- `transfer_recommendations`: 668 generated redistribution recommendations with ML predicted demand, demand source, and scores.
- `recommendation_evidence`: 1-to-many structured factual checklist bullets.
- `transfer_actions` & `override_reasons`: Human approval, rejection, and override records.
- `audit_logs`: Immutable compliance audit trail.

*Dataset Disclosure: The project uses 100% synthetic operational data generated via `ml/generate_data.py`. No real patient health information (PHI) is used.*

---

## 23. API IMPLEMENTATION

The backend exposes 10 modular REST router groups:
1. **Health Telemetry**: `GET /health` (Public subsystem status).
2. **Administrative**: `POST /api/seed` (Guarded by `ADMIN` role).
3. **Authentication**: `POST /api/auth/login`, `GET /api/auth/me`.
4. **Inventory**: `GET /api/inventory`, `GET /api/inventory/{id}`.
5. **Pharmacies**: `GET /api/pharmacies`, `GET /api/pharmacies/{id}`.
6. **Medicines**: `GET /api/medicines`.
7. **Recommendations**: `GET /api/recommendations`, `GET /api/recommendations/{id}`, `POST /api/recommendations/{id}/approve`, `POST /api/recommendations/{id}/reject`, `POST /api/recommendations/{id}/override`, `POST /api/recommendations/generate`.
8. **Analytics**: `GET /api/analytics`.
9. **Evaluation**: `GET /api/evaluation`, `POST /api/evaluation/run`.
10. **Compliance & Safety**: `GET /api/audit-logs`, `GET /api/edge-cases`.

---

## 24. DEPLOYMENT

### Option A: Local Development Environment
- Backend: Python 3.11+, `pip install -r backend/requirements.txt`, `python backend/app/main.py` (starts on port 8000).
- Frontend: Node.js 18+, `npm install`, `npm run dev` (starts on port 3000).

### Option B: Docker Compose Multi-Container Orchestration
- `docker-compose.yml` orchestrates three containerized services:
  1. `frontend`: Node/Nginx container serving the compiled React 18 SPA.
  2. `backend`: Uvicorn/FastAPI asynchronous container.
  3. `db`: PostgreSQL 15 container with persistent volume storage.

---

## 25. CURRENT PROJECT STATUS – 70% MILESTONE

### Table 3: Current Module Status
| Module Name | Implementation Summary | Validation Evidence | Milestone Status |
|---|---|---|---|
| **Inventory Core** | Multi-branch batch tracking with safety buffers | `test_excess_stock_calculation` | **COMPLETED** |
| **Risk Scorer** | Deterministic Days-to-Expiry math relative to reference date | `test_calculate_days_to_expiry` | **COMPLETED** |
| **ML Demand Model** | Random Forest Regressor ($R^2=0.7523$) | `ml/model_metrics.json` | **COMPLETED** |
| **ML Integration** | Destination ranking queries ML model with cache | `test_recommender_uses_predicted_demand` | **COMPLETED** |
| **Safety Feasibility** | Haversine distance, post-transit life buffer | `test_feasibility_check_*` | **COMPLETED** |
| **Evidence & Scoring** | Recommendation Score (0-100), checklist items | `test_recommendation_evidence_*` | **COMPLETED** |
| **Human Workflow** | Approval, structured rejection, quantity override | `test_approve_*`, `test_override_*` | **COMPLETED** |
| **Audit Logging** | Immutable state transition logging | `test_audit_log_created_on_action` | **COMPLETED** |
| **Security & RBAC** | JWT authentication, admin seed protection | `test_seed_endpoint_*` | **COMPLETED** |
| **Telemetry & Health** | Subsystems health telemetry endpoint | `test_system_health_subsystems` | **COMPLETED** |
| **Executive UI** | AI Action Center, Demand card, Priority Queue | `npm run build` (0 errors) | **COMPLETED** |
| **Simulation Suite** | 30-scenario simulation benchmark | `data/simulation_results.json` | **COMPLETED** |

**Current Status Assessment**: **78.5% Completion** — The core functional pipeline is complete, tested, and demonstrated.

---

## 26. REMAINING 30%

The remaining ~21.5% of development required for final completion (Review #3) encompasses:
1. **Hospital & Pharmacy ERP Connectors**: Live HL7 / FHIR API connectors to ingest live inventory feeds from hospital information systems.
2. **Capacitated Vehicle Routing (CVRP)**: Upgrading pairwise Haversine routing to a multi-stop vehicle routing solver.
3. **Automated MLOps Pipeline**: Monthly automated model retraining, drift monitoring, and automated fallback triggers.
4. **Enterprise Multi-Tenancy & SSO**: Multi-tenant database isolation and SAML 2.0 / OAuth2 single sign-on.
5. **Mobile Warehouse Companion**: Native PWA or Android application for physical barcode/RFID scanning during dispatch.

---

## 27. LIMITATIONS

1. **Synthetic Operational Dataset**: Data is 100% synthetically generated to model realistic clinical patterns without violating patient privacy laws.
2. **Simulation-Based Behavioral Acceptance**: Pharmacist acceptance rates are generated through a 30-scenario simulation engine, not multi-year clinical field trials.
3. **Urban Geographic Boundary**: Geographic routing is currently bounded to 18 metropolitan pharmacy hubs across Bangalore.
4. **Deterministic Reference Date**: For repeatable evaluation, the system operates with a configured reference date of `2026-08-14`.

---

## 28. FUTURE WORK

Post-academic future enhancements include:
- Multi-region cold-chain temperature sensor integration via IoT gateways.
- Reinforcement learning for automated cross-hospital transfer negotiations.
- Dynamic pricing models to discount near-expiry medicines locally before triggering transfers.

---

## 29. CONCLUSION

PharmaShift has successfully progressed from an initial architectural foundation (Review #1: 34.3 / 35 marks) to a complete, machine-learning-integrated, and explainable stock redistribution system.

The project stands at **78.5% completion**, comfortably surpassing the mandatory 70% requirement for Review #2. The completed core pipeline is supported by **30 passing automated tests**, a **flawless production build**, an **immutable compliance audit trail**, and an **empirical simulation benchmark proving a +9.88% value gain and 52.09% expiry waste reduction**. PharmaShift is fully prepared for Review #2 evaluation.

---

## 30. REVIEW #2 DEMONSTRATION CHECKLIST

- [x] **Login & Persona Switching**: Seamless switching between Admin, Manager, and Pharmacist.
- [x] **Subsystems Health Status**: Live verification of API, Database, ML model, and Reference Date via `/health`.
- [x] **Dashboard Overview**: Inspection of AI Action Center, Demand Telemetry, and KPI cards.
- [x] **Priority Recommendations Queue Table**: Inspection of transfer routes, ML demand, and expiry dates.
- [x] **Explainable Evidence Modal**: Viewing calibrated Recommendation Score and Safety Checklist.
- [x] **Human Approval Flow**: Approving a transfer and verifying status update.
- [x] **Structured Rejection Flow**: Rejecting a transfer with mandatory reason category (`STOCK_COUNT_MISMATCH`).
- [x] **Quantity Override Flow**: Overriding quantity from 50 to 25 units and verifying live value recalculation.
- [x] **Spatial Network Topology**: Inspecting Bangalore mesh map and Node Balance states.
- [x] **Edge Cases Sandbox**: Verifying all 8 deterministic clinical safety blocks with PASS badges.
- [x] **Audit Trail Verification**: Inspecting immutable compliance logs as Administrator.
- [x] **RBAC Security Enforcement**: Demonstrating Pharmacist restriction on Audit Logs and Seed endpoint.
- [x] **Analytics & Simulation Benchmarks**: Inspecting 30-scenario results (+₹7.44L gain, 93.03% acceptance).
- [x] **Automated Test Suite**: Running `pytest backend/tests/test_backend.py -v` (30/30 passed).
- [x] **Production Build**: Running `npm run build` in frontend (0 errors).
- [x] **GitHub Repository Readiness**: Up-to-date documentation, clean working tree, and synchronized results.
