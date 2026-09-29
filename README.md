# PharmaShift: Expiry-Aware Pharmacy Stock Redistribution Recommender

> **Important Clinical & Privacy Disclaimer**:  
> *This system operates exclusively on 100% synthetic operational pharmacy data and does not make clinical decisions. It serves strictly as an operational decision-support tool for inventory logistics, stock waste minimization, and supply-chain optimization.*

---

## 1. Project Overview
**PharmaShift** is an enterprise-grade, explainable, and safety-constrained stock redistribution recommendation engine tailored for multi-branch pharmacy networks. The system prevents perishable pharmaceutical inventory from expiring in low-velocity retail branches by intelligently routing excess batches to high-dispensing central hubs before remaining shelf-life expires.

---

## 2. Problem Statement
Multi-branch pharmacy networks suffer severe financial losses and unnecessary medication destruction because near-expiry medication batches sit unconsumed in low-demand suburban clinics while central hospitals and high-volume retail hubs experience stock shortages for those exact items. Manual identification is slow, labor-intensive, error-prone, and frequently occurs too late—when remaining shelf-life is shorter than road transit times.

---

## 3. Objectives
1. **Detect At-Risk Batches**: Continuously scan network inventory to identify batches approaching expiration.
2. **Quantify Local Surplus**: Calculate actionable excess stock while strictly reserving mandatory local patient safety buffers.
3. **Discover Candidate Destinations**: Rank candidate branches using machine-learning demand forecasting, road transit distance, and storage capacity.
4. **Enforce Feasibility Rules**: Clinically validate that remaining shelf-life exceeds road transit duration with a minimum 3-day buffer.
5. **Provide Full Explainability**: Generate factual, transparent evidence bullets justifying every recommendation.
6. **Ensure Human Oversight**: Require explicit confirmation for high-impact transfers ($> ₹2,000$, large volumes, or critical medicines).
7. **Maintain Immutable Traceability**: Log every approval, rejection (with mandatory reason category), and override in an audit trail.
8. **Demonstrate Economic Superiority**: Benchmark savings against a naive isolated FIFO baseline across 30 simulation cycles.

---

## 4. Key Features
- **Login-First Secure Access**: Strict authentication requirement; direct dashboard access without valid JWT is blocked.
- **Role-Based Scoping (RBAC)**: Distinct permissions for `ADMIN`, `MANAGER`, and `PHARMACIST` (with branch-level data scoping).
- **React Error Boundaries**: Component-level fault isolation with instant user recovery controls across all dashboard views.
- **Machine Learning Demand Forecasting**: Trained `RandomForestRegressor` with a resilient 3-tier fallback architecture.
- **Human-in-the-Loop Workflow**: High-impact confirmation checklist, structured rejection reasons, and dynamic quantity overrides.
- **Synthetic Safety Sandbox**: Live validation of 8 core operational edge cases (e.g. transit exceeding shelf-life, closed branches, zero demand).
- **Empirical Simulation Engine**: 30-scenario simulation demonstrating **+₹7.44 Lakhs (+9.88%)** value protected and **-52.1% waste reduction**.

---

## 5. System Architecture

```mermaid
flowchart TD
    User([Authenticated User]) --> UI[React 18 + Vite Frontend]
    UI --> Auth[AuthContext & Login Page]
    UI --> EB[React Error Boundaries]
    
    UI -- REST API Calls (Bearer JWT) --> API[FastAPI Backend]
    
    subgraph Backend Services
        API --> AuthRouter[Auth & RBAC Router]
        API --> RecEngine[Recommendation Engine]
        API --> RiskScorer[Risk & Excess Scorer]
        API --> Feasibility[Feasibility Constraint Verifier]
        API --> MLService[ML Demand Service]
        API --> AuditService[Audit Logging Service]
    end
    
    subgraph Machine Learning
        MLService --> ModelArtifact[RandomForestRegressor joblib]
        MLService --> FallbackTier[3-Tier Fallback Cascade]
    end
    
    subgraph Persistence Layer
        Backend Services --> DB[(PostgreSQL / SQLite)]
    end
```

---

## 6. Technology Stack

| Layer | Technologies | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite 5, Tailwind CSS, Lucide React, Recharts | Fast, responsive, dark-themed decision support UI with error boundaries |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy ORM, Pydantic V2 | High-throughput REST API with dependency injection and RBAC guards |
| **Database** | PostgreSQL 15 (Docker) / SQLite (Zero-config local fallback) | Relational persistence for inventory batches, recommendations, and audit logs |
| **Machine Learning** | scikit-learn (`RandomForestRegressor`), pandas, NumPy, joblib | Daily dispensing demand forecasting with feature volatility metrics |
| **Security** | PyJWT / python-jose, passlib / direct bcrypt (rounds=10) | HS256 Bearer JWT token issuance and salted password hashing |
| **DevOps** | Docker, Docker Compose, Nginx | Multi-container orchestration for production deployment |
| **Automated Testing**| pytest 9.1, FastAPI TestClient | 49 comprehensive tests across 16 categories (100% passing) |

---

## 7. Project Structure

```
project-root/
├── frontend/                     # React 18 + Vite Frontend Application
│   ├── src/
│   │   ├── components/           # Navbar, Sidebar, ErrorBoundary, Modals, Badges, NetworkMap
│   │   ├── context/              # AuthContext (JWT management & session handling)
│   │   ├── pages/                # Login, Dashboard, Inventory, Recommendations, Pharmacies,
│   │   │                         # Analytics, AuditLogs, EdgeCases, Privacy, Settings
│   │   ├── services/             # Axios API client with 401 response interceptor
│   │   ├── App.jsx               # Protected routing & ErrorBoundary integration
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
│
├── backend/                      # FastAPI Backend Application
│   ├── app/
│   │   ├── database/             # SQLAlchemy SessionLocal, PostgreSQL/SQLite engine
│   │   ├── models/               # SQLAlchemy models (User, Pharmacy, Batch, Recommendation, AuditLog)
│   │   ├── schemas/              # Pydantic validation schemas
│   │   ├── recommender/          # Recommendation Engine, Risk Scorer, Feasibility Verifier
│   │   ├── services/             # ML Demand Service, Seeding Service, Audit Service, Simulation
│   │   ├── utils/                # Direct bcrypt hashing, JWT security, Haversine distance
│   │   ├── routers/              # auth, inventory, pharmacies, medicines, recommendations,
│   │   │                         # analytics, evaluation, audit_logs, edge_cases
│   │   └── main.py               # FastAPI entrypoint, centralized error handlers, Lifespan
│   ├── tests/                    # 49 automated pytest test cases across 16 categories
│   ├── requirements.txt
│   └── Dockerfile
│
├── data/                         # 100% Synthetic Datasets
│   ├── synthetic_inventory.csv   # 5,193 batches with realistic shelf-life distributions & edge cases
│   ├── synthetic_pharmacies.csv  # 18 metropolitan pharmacy branches
│   ├── synthetic_medicines.csv   # 60 synthetic medicines across 10 categories
│   ├── synthetic_demand.csv      # 1,080 daily/weekly/monthly demand profiles
│   ├── synthetic_transfers.csv   # 306 inter-pharmacy transit routes & distances
│   └── simulation_results.json   # 30-scenario simulation benchmarks
│
├── ml/                           # ML Pipelines & Artifacts
│   ├── generate_data.py          # Synthetic dataset generator
│   ├── train.py                  # Random Forest demand forecasting model training
│   ├── evaluate.py               # 30-scenario simulation suite comparing Baseline vs Recommender
│   ├── demand_model.joblib       # Trained ML model artifact
│   └── model_metrics.json        # MAE: 1.2152, RMSE: 3.5170, R²: 0.7523
│
├── docs/                         # Granular Technical Documentation
│   ├── REVIEW_3_REPORT.md        # Comprehensive Review #3 completion report
│   ├── REVIEW_3_EVIDENCE_CHECKLIST.md # 20 itemized evaluator evidence items
│   ├── review3_improvements.md   # Alignment with Review #2 feedback
│   ├── review3_readiness.md      # 17-step evaluator presentation script
│   ├── database_schema.md        # Full table definitions & Mermaid ER diagram
│   ├── api.md                    # Master API documentation with schemas
│   ├── testing.md                # 49-test catalog across 16 categories
│   ├── error_handling.md         # React Error Boundaries & backend exception architecture
│   └── authentication.md         # Login-First flow, JWT lifecycle & RBAC matrix
│
├── docker-compose.yml
├── .env.example
├── README.md
└── pytest.ini
```

---

## 8. Setup Instructions

### Option A: Local Development (Zero Docker Requirement)

1. **Backend Setup**:
   ```bash
   # Navigate to backend and install Python dependencies
   pip install -r backend/requirements.txt

   # Start the FastAPI server
   python backend/app/main.py
   ```
   *The backend starts at `http://localhost:8000`. On first launch, it automatically initializes `pharmacy_db.sqlite3` and seeds 5,193 batches, 18 pharmacies, 60 medicines, and initial recommendations.*

2. **Frontend Setup**:
   ```bash
   # Navigate to frontend and install node packages
   cd frontend
   npm install

   # Start the Vite development server
   npm run dev
   ```
   *The application UI starts at `http://localhost:3000` (or `http://localhost:5173`).*

### Option B: Docker Compose (Multi-Service Production Stack)

```bash
docker compose up --build
```
- **Frontend UI**: `http://localhost:3000`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`
- **PostgreSQL Database**: `localhost:5432`

---

## 9. Environment Configuration

Copy `.env.example` to `.env`:
```ini
# Database Configuration (PostgreSQL in Docker, SQLite fallback for local dev)
DATABASE_URL=postgresql://postgres:replace-with-a-secure-password@localhost:5432/pharmacy_db

# Security & JWT Configuration
SECRET_KEY=replace-with-a-secure-random-secret-key-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ALGORITHM=HS256

# Configurable Reference Date Mode (2026-08-14 for deterministic benchmark or CURRENT_DATE for live)
DEMO_REFERENCE_DATE=2026-08-14

# Network & Ports
PORT=8000
VITE_API_BASE_URL=http://localhost:8000
```

---

## 10. Authentication Architecture
- **Algorithm**: `HS256` Bearer JWT token issued upon successful verification.
- **TTL**: 24 hours (1,440 minutes).
- **Password Security**: Direct bcrypt password hashing with 10 salt rounds and explicit 72-byte truncation safety.
- **Session Revocation**: 401 Unauthorized API responses automatically clear client storage and redirect the browser to the Login page.

---

## 11. User Roles & RBAC Matrix

| Role | Access Scope | Inventory | Approvals / Overrides | Audit Trail | System Reseed |
|---|---|---|---|:---:|:---:|
| **`ADMIN`** | Network-Wide (All 18 branches) | Full view | Full authority | Full access | Allowed (`POST /api/seed`) |
| **`MANAGER`** | Network-Wide (All 18 branches) | Full view | Full authority | Full access | Blocked (HTTP 403) |
| **`PHARMACIST`**| Scoped (e.g. `PHARM-001`) | Scoped to assigned branch | Outgoing from assigned branch only | Blocked (HTTP 403) | Blocked (HTTP 403) |

### Development Demo Accounts (Pre-Seeded):
| Role | Email | Password | Scope |
|---|---|---|---|
| **ADMIN** | `admin@pharmacy.io` | `Admin@123` | System Administrator (Network-Wide) |
| **MANAGER** | `manager@pharmacy.io` | `Manager@123` | Regional Supply Chain Manager (Network-Wide) |
| **PHARMACIST** | `pharmacist@pharmacy.io` | `Pharmacist@123` | Senior Pharmacist (Central Hub `PHARM-001`) |
| **PHARMACIST 2**| `pharmacist2@pharmacy.io`| `Pharmacist@123` | Duty Pharmacist (Indiranagar `PHARM-002`) |

---

## 12. Login Flow (Login-First Architecture)

```
Open Website (http://localhost:3000)
             │
             ▼
   Login Screen Appears First
             │
   User Enters Credentials / Uses Demo Quick-Fill
             │
   POST /api/auth/login
             │
   JWT Bearer Token Issued & Stored
             │
   User Redirected to Protected Dashboard
             │
   Sign Out Clicked ──► Clear Token ──► Redirect to Login
```
- Direct access to any dashboard module without logging in is strictly blocked.
- Evaluators can use the **Review Evaluation Quick-Fill** panel on the Login card for 1-click credential entry.

---

## 13. Machine Learning Demand Forecasting
- **Model**: `RandomForestRegressor(n_estimators=100, max_depth=10)`
- **Artifact**: `ml/demand_model.joblib`
- **Features (9)**:
  1. `weekly_avg_daily`: Short-term dispensing rate
  2. `monthly_avg_daily`: Mid-term velocity baseline
  3. `historical_avg_daily`: Macro long-term average
  4. `demand_volatility`: $| \text{weekly} - \text{monthly} |$ (surge/dip indicator)
  5. `storage_capacity`: Facility scale proxy
  6. `unit_price`: Drug cost tier
  7. `category`: Therapeutic class encoding
  8. `demand_trend`: Directional velocity trend
  9. `is_critical`: Life-saving inelasticity flag
- **Evaluation Performance**:
  - **MAE**: `1.2152` units/day
  - **RMSE**: `3.5170` units/day
  - **$R^2$ Score**: `0.7523`
- **3-Tier Fallback Cascade**: `ML_PREDICTION` $\rightarrow$ `STORED_FORECAST` $\rightarrow$ `HEURISTIC_FALLBACK`.

---

## 14. Recommendation Engine & Decision Rules
1. **Local Excess Calculation**:
   $$\text{Excess} = \max(0, \text{Quantity} - [\text{Daily Demand} \times DTE] - \text{Safety Stock Buffer})$$
2. **Post-Transit Shelf-Life Feasibility**:
   $$\text{Remaining Shelf Life} = DTE - T_{\text{transit}} \ge 3 \text{ days}$$
3. **Destination Candidate Ranking Formula**:
   $$\text{Score} = (\text{Dest Demand Velocity} \times 12.0) + (\text{Remaining Shelf Life} \times 2.5) - (\text{Distance km} \times 0.35) [+ 20.0 \text{ if Critical}]$$
4. **Capacity Capping**:
   $$Q^* = \min(\text{Source Excess}, \text{Dest Consumable Window}, \text{Dest 15\% Bay Allowance})$$
5. **High-Impact Escalation Guard**:
   Triggered if Value $\ge ₹2,000$, Quantity $\ge 50$ units, $DTE \le 14$ days, or Critical Medicine. Requires explicit human confirmation checkbox before approval.

---

## 15. Explainability & Transparent Evidence
Every recommendation embeds 9 factual evidence bullets displayed in the **"Why Recommended?"** modal:
- Source excess available beyond safety buffer
- ML-predicted daily destination demand
- ML demand model source tracking
- Local safety stock protection guarantee
- Remaining post-transit shelf-life cushion
- Road transit distance and transit duration
- Storage bay capacity window
- Monetary value protected
- Normalized recommendation score (0–100)

---

## 16. API Documentation

### Master API Endpoints Directory (20 Implemented Endpoints):

| Method | Endpoint | Description | Auth | Role | Common Status Codes |
|---|---|---|:---:|:---:|---|
| **`GET`** | `/health` | Subsystem health telemetry (API, DB, ML, Recommender) | No | None | `200`, `500` |
| **`POST`** | `/api/seed` | Force database reseed with 5,000+ synthetic batches | Yes | `ADMIN` | `200`, `401`, `403` |
| **`POST`** | `/api/auth/login` | Authenticate credentials and receive Bearer JWT | No | None | `200`, `400`, `401`, `422` |
| **`GET`** | `/api/auth/me` | Fetch active user profile from Bearer token | Yes | Any | `200`, `401` |
| **`GET`** | `/api/inventory` | Search & filter network inventory batches (scoped) | Yes | Any (Scoped) | `200`, `401` |
| **`GET`** | `/api/inventory/{id}` | Inspect single inventory batch risk & excess metrics | Yes | Any (Scoped) | `200`, `401`, `403`, `404` |
| **`GET`** | `/api/pharmacies` | List all network pharmacy branches & coordinates | No | None | `200` |
| **`GET`** | `/api/pharmacies/{id}` | Detailed branch metrics, capacity, and stock risk | No | None | `200`, `404` |
| **`GET`** | `/api/medicines` | Query pharmaceutical master catalog & categories | No | None | `200` |
| **`GET`** | `/api/recommendations` | Browse transfer recommendations & evidence bullets | Yes | Any (Scoped) | `200`, `401` |
| **`GET`** | `/api/recommendations/{id}` | Single transfer recommendation detail & evidence | Yes | Any (Scoped) | `200`, `401`, `403`, `404` |
| **`POST`** | `/api/recommendations/{id}/approve` | Approve transfer (validates high-impact confirmation) | Yes | Any (Scoped) | `200`, `400`, `401`, `403`, `404` |
| **`POST`** | `/api/recommendations/{id}/reject` | Reject transfer with mandatory structured reason | Yes | Any | `200`, `400`, `401`, `404` |
| **`POST`** | `/api/recommendations/{id}/override` | Override transfer quantity with reason & value update | Yes | Any | `200`, `400`, `401`, `404` |
| **`POST`** | `/api/recommendations/generate` | Trigger live re-evaluation of recommendations | Yes | `ADMIN`, `MANAGER` | `200`, `401`, `403` |
| **`GET`** | `/api/analytics` | Aggregated network KPIs, risk distribution & savings | No | None | `200` |
| **`GET`** | `/api/evaluation` | 30-scenario simulation benchmarks vs. naive FIFO | No | None | `200` |
| **`POST`** | `/api/evaluation/run` | Execute live 30-scenario simulation suite | Yes | `ADMIN`, `MANAGER` | `200`, `401`, `403` |
| **`GET`** | `/api/audit-logs` | Immutable audit trail with filtering by action/user | Yes | `ADMIN`, `MANAGER` | `200`, `401`, `403` |
| **`GET`** | `/api/edge-cases` | Status and safety verification of all 8 edge cases | No | None | `200` |

*For complete request/response schemas and parameters, see [`docs/api.md`](file:///c:/Users/santh/OneDrive%20-%20Rathinam%20Group%20Of%20Institutions/Desktop/raale%20project/docs/api.md).*

---

## 17. Database Schema

### Entity-Relationship Diagram:

```mermaid
erDiagram
    PHARMACY ||--o{ INVENTORY_BATCH : "stores"
    PHARMACY ||--o{ DEMAND_FORECAST : "experiences"
    PHARMACY ||--o{ TRANSFER_RECOMMENDATION : "source / destination"
    MEDICINE ||--o{ INVENTORY_BATCH : "categorizes"
    MEDICINE ||--o{ DEMAND_FORECAST : "projected for"
    MEDICINE ||--o{ TRANSFER_RECOMMENDATION : "transferred item"
    INVENTORY_BATCH ||--o{ TRANSFER_RECOMMENDATION : "target batch"
    TRANSFER_RECOMMENDATION ||--o{ RECOMMENDATION_EVIDENCE : "justified by"
    TRANSFER_RECOMMENDATION ||--o{ TRANSFER_ACTION : "history"
    TRANSFER_RECOMMENDATION ||--o| OVERRIDE_REASON : "custom modification"
    USER ||--o{ TRANSFER_ACTION : "executes"
    USER ||--o{ OVERRIDE_REASON : "authorizes"
    USER ||--o{ AUDIT_LOG : "recorded in"
```

### Table Directory:
1. **`users`**: User identities, roles (`ADMIN`, `MANAGER`, `PHARMACIST`), bcrypt hashes, branch assignment.
2. **`pharmacies`**: 18 network branches, GPS coordinates, storage capacity, operating status.
3. **`medicines`**: 60 synthetic medicines across 10 categories, unit acquisition prices, critical flags.
4. **`inventory_batches`**: 5,193 batch records, quantities, expiry dates (`YYYY-MM-DD`), edge case tags.
5. **`demand_forecasts`**: Daily, weekly, monthly dispensing rates and ML predicted demand.
6. **`transfer_recommendations`**: Generated transfer proposals with recommendation scores, predicted demand, and status.
7. **`recommendation_evidence`**: Factual explanation bullets and metrics per recommendation.
8. **`transfer_actions`**: Human decisions (`APPROVED`, `REJECTED`, `OVERRIDDEN`) with quantities and notes.
9. **`override_reasons`**: Manager override justifications and modified quantities.
10. **`audit_logs`**: Immutable historical compliance trail of all state transitions.

*For complete column definitions and constraints, see [`docs/database_schema.md`](file:///c:/Users/santh/OneDrive%20-%20Rathinam%20Group%20Of%20Institutions/Desktop/raale%20project/docs/database_schema.md).*

---

## 18. Error Handling & Resilience
- **Frontend Error Boundaries (`ErrorBoundary.jsx`)**: Encapsulates all 8 views. Isolates client-side rendering exceptions and renders a friendly recovery card (*"Something went wrong while loading this section"*) with a **"Retry Section"** button without crashing the user session.
- **Backend Exception Handlers (`main.py`)**:
  - `HTTPException`: Consistent JSON error payloads with status codes.
  - `RequestValidationError`: Formats Pydantic 422 errors into field-level feedback.
  - `Exception`: Catches uncaught server errors, logs securely, and returns HTTP 500 JSON without exposing stack traces.

*For in-depth architecture details, see [`docs/error_handling.md`](file:///c:/Users/santh/OneDrive%20-%20Rathinam%20Group%20Of%20Institutions/Desktop/raale%20project/docs/error_handling.md).*

---

## 19. Testing Overview & Pyramid
PharmaShift follows a 5-tier testing strategy:
1. **Unit Tests**: Expiry calculations, risk classification, Haversine formulas.
2. **Integration Tests**: SQLAlchemy relationships, SQLite/PostgreSQL operations, ML model inference.
3. **API Tests**: FastAPI `TestClient` endpoint status and schema assertions.
4. **Frontend / Build Validation**: Clean production bundle compile (`npx.cmd vite build`).
5. **End-to-End Demonstration**: Structured 17-step operational walkthrough.

---

## 20. Granular Test Categories (49 / 49 Passing Tests)

Run the automated test suite:
```bash
pytest backend/tests/test_backend.py -v
```

### Test Suite Execution Breakdown:
- **Category 1 (Authentication)**: 4 tests (Login success, invalid password, inactive user, token validation)
- **Category 2 (Authorization / RBAC)**: 6 tests (Pharmacist branch scoping, cross-branch approval block, admin seed protection)
- **Category 3 (Inventory)**: 3 tests (Listing, single batch lookup, category filtering)
- **Category 4 (Pharmacy Network)**: 2 tests (Branch listing, detail metrics, 404 on missing branch)
- **Category 5 (Demand / ML)**: 4 tests (Model inference, metrics validation, 3-tier fallback chain, medicines catalog)
- **Category 6 (Expiry-Risk Classification)**: 4 tests (Date parsing, risk brackets, dynamic reference date)
- **Category 7 (Safety-Stock Retention)**: 2 tests (3-day buffer reservation, zero excess enforcement)
- **Category 8 (Recommendation Engine)**: 3 tests (Generation, predicted demand integration, evidence verification)
- **Category 9 (Destination Ranking)**: 2 tests (Transit days estimation, critical medicine bonus)
- **Category 10 (Transfer Feasibility)**: 7 tests (Shelf-life vs transit, closed branch, zero demand, expired batch, maintenance, capacity exceeded, success)
- **Category 11 (API Validation)**: 2 tests (Negative override quantity rejection, missing rejection reason rejection)
- **Category 12 (Database Integrity)**: 1 test (ORM relationship traversal across tables)
- **Category 13 (Audit Trail)**: 4 tests (Approval logging, rejection logging, override logging, action filtering)
- **Category 14 (Analytics)**: 2 tests (Dashboard KPIs, 30-scenario simulation endpoint)
- **Category 15 (Operational Edge Cases)**: 1 test (All 8 failure guard scenarios verified)
- **Category 16 (Error Handling)**: 2 tests (404 on non-existent recommendation, system health telemetry)

**Total**: **49 Passed, 0 Failed (100% Pass Rate in 50 seconds)**.  
*For itemized input/output test documentation, see [`docs/testing.md`](file:///c:/Users/santh/OneDrive%20-%20Rathinam%20Group%20Of%20Institutions/Desktop/raale%20project/docs/testing.md).*

---

## 21. Operational Edge Cases Sandbox
The system includes 8 dedicated edge cases tested against safety guards:
1. `INV-EDGE-001` (Expires before transit completes): **Blocked** by Rule-01.
2. `INV-EDGE-002` (No destination has demand): **Blocked** by Rule-02.
3. `INV-EDGE-003` (Source below safety buffer): **Blocked** by Rule-03.
4. `INV-EDGE-004` (Invalid/malformed expiry date): **Quarantined** by Rule-04.
5. `INV-EDGE-005` (Destination closed/maintenance): **Blocked** by Rule-05.
6. `INV-EDGE-006` (Already expired batch): **Blocked** by Rule-06 (Disposal prompted).
7. `INV-EDGE-007` (Sudden demand collapse): **Triggered** for proactive redistribution.
8. `INV-EDGE-008A/B` (Duplicate lot across branches): **Isolated** by Inventory ID.

---

## 22. Analytics & Simulation Benchmarks

Across **30 multi-scenario simulation cycles** (`data/simulation_results.json`):

| Evaluation Metric | Naive FIFO Baseline | Proposed Recommender | Net Impact / Improvement |
|---|---|---|---|
| **Average Value Protected** | ₹75,70,344.23 | **₹83,14,345.38** | **+₹7,44,001.15 (+9.88% Gain)** |
| **Value Lost to Expiration**| ₹14,28,450.00 | **₹6,84,448.85** | **-₹7,44,001.15 (-52.1% Loss Reduction)** |
| **Recommendation Acceptance** | N/A | **93.03%** | Clinician concurrence |
| **Average Transit Distance**| N/A | **10.27 km** | Urban logistics efficiency |
| **Average Remaining Life** | N/A | **19.41 days** | Post-transit safety buffer |

---

## 23. Audit Trail & Human Oversight
- Every recommendation action records an immutable audit log with:
  - User identity and role at the time of execution.
  - Previous status and new status (`PENDING` $\rightarrow$ `APPROVED` / `REJECTED` / `OVERRIDDEN`).
  - Quantity committed.
  - Structured justification reason.
  - Immutable UTC timestamp.

---

## 24. Security & Privacy
- **Zero Real Patient PII**: Operates on 100% synthetic operational logistics data.
- **Bcrypt Salted Hashes**: Passwords hashed with 10 rounds and 72-byte truncation safety.
- **Signed HS256 JWTs**: Strict token signature verification on all protected routes.
- **Clean Configuration**: Zero hardcoded credentials in source code. `.env.example` contains placeholders only.

---

## 25. Docker & Deployment
PharmaShift includes production-ready Docker containers:
- `backend/Dockerfile`: Lightweight Python 3.11 image running FastAPI with Uvicorn.
- `frontend/Dockerfile`: Multi-stage build producing compiled Nginx static assets.
- `docker-compose.yml`: Automated service composition linking PostgreSQL 15, FastAPI, and Nginx.

---

## 26. Limitations
1. **Urban Distance Assumption**: Road transit distance uses Haversine geodesic math with city road transit factor (1.3x) rather than live Google Maps traffic APIs.
2. **Batch Granularity**: Operates on batch-level inventory records rather than individual RFID blister packs.
3. **Cold-Chain Logistics**: Assumes all participating transport vehicles have standard thermal protection for refrigerated stock.

---

## 27. Review #3 Progress & Feedback Resolution
All Review #2 feedback items have been completely addressed:
1. **Granular Unit Testing Documentation**: 49 tests documented across 16 categories in `docs/testing.md`.
2. **Frontend Error Boundaries**: Implemented in `ErrorBoundary.jsx` and documented in `docs/error_handling.md`.
3. **Code Comments**: Detailed "WHY" rationales added to `engine.py`, `feasibility.py`, `risk_scorer.py`, `ml_service.py`, and `security.py`.
4. **API Endpoints in README**: Full 20-endpoint master directory added to Section 16 of `README.md`.
5. **Database Schema in README**: Full relational table directory and ER diagram added to Section 17 of `README.md`.
6. **Login-First Architecture**: Strictly implemented; unauthenticated access to dashboard is blocked.

---

## 28. Future Work
1. **Multi-Hop Consolidated Routing**: Optimize hub-and-spoke routes for regional distribution.
2. **Third-Party Logistics Webhooks**: Integrate with Dunzo, Porter, or Shadowfax for automated dispatch.
3. **Mobile PWA Barcode Scanner**: In-browser camera scanning for physical shelf stock verification.
