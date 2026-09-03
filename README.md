# PharmaShift: Expiry-Aware Pharmacy Stock Redistribution Recommender

> **Important Clinical & Privacy Disclaimer**:
> *This prototype uses 100% synthetic operational pharmacy data and is not intended to make clinical decisions. It serves strictly as an operational decision-support tool for inventory logistics and stock waste minimization.*

---

## 1. Problem Statement
Multi-branch pharmacy networks suffer massive financial losses and unnecessary medication destruction when near-expiry pharmaceutical batches sit unconsumed in low-demand branches while central or high-volume branches experience stock shortages for those exact items. Manual identification is slow, prone to oversight, and frequently occurs when remaining shelf-life is shorter than the logistics transit window.

## 2. Project Objective
Build a production-grade, explainable, and safety-constrained redistribution recommender that:
1. Detects batches approaching expiration across all pharmacy branches.
2. Quantifies local surplus stock after reserving mandatory local patient safety stock.
3. Discovers and ranks candidate destination pharmacies based on real dispensing velocity, road transit distance, and available storage capacity.
4. Verifies operational feasibility (ensuring transit time does not exceed remaining shelf life).
5. Generates fully explainable, transparent recommendation evidence bullets.
6. Enforces human-in-the-loop confirmation for high-impact transfers ($> ₹2,000$, large volumes, or urgent expiry).
7. Captures structured rejection and override reasons with full audit logging.
8. Benchmarks economic savings against a naive FIFO baseline across 30 simulation cycles.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| **Frontend** | React 18, Vite, Tailwind CSS, Lucide React, Recharts |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy, Pydantic V2 |
| **Database** | PostgreSQL 15 (Docker) / SQLite (Zero-config local fallback) |
| **Machine Learning & Data** | scikit-learn (`RandomForestRegressor`), pandas, NumPy, joblib |
| **DevOps & Containers** | Docker, Docker Compose, Nginx |
| **Testing** | pytest, FastAPI TestClient (21 automated tests) |

---

## 4. System Architecture

```
project-root/
├── frontend/                     # React 18 + Vite + Tailwind CSS + Recharts
│   ├── src/
│   │   ├── components/           # Navbar, Sidebar, Badges, Modals (Evidence, Approval, Reject, Override), NetworkMap
│   │   ├── context/              # AuthContext (Role switching, JWT persistence)
│   │   ├── pages/                # Dashboard, Inventory, Recommendations, Pharmacies, Analytics, AuditLogs, EdgeCases, Privacy, Settings
│   │   ├── services/             # Axios API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── Dockerfile
│   └── package.json
│
├── backend/                      # FastAPI Application
│   ├── app/
│   │   ├── database/             # SessionLocal, PostgreSQL / SQLite engine
│   │   ├── models/               # SQLAlchemy ORM models (Users, Pharmacies, Batches, Recommendations, Evidence, AuditLogs)
│   │   ├── schemas/              # Pydantic validation models
│   │   ├── recommender/          # Explainable Rule Engine, Risk Scorer, Feasibility & Routing
│   │   ├── services/             # Seeding, Audit, Simulation, and ML services
│   │   ├── utils/                # Direct bcrypt hashing, JWT security, Haversine distance
│   │   ├── routers/              # auth, inventory, pharmacies, medicines, recommendations, analytics, evaluation, audit_logs, edge_cases
│   │   └── main.py               # FastAPI entrypoint & Lifespan auto-seeding
│   ├── tests/                    # 21 automated pytest test cases
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
├── ml/                           # ML Pipelines & Evaluation Scripts
│   ├── generate_data.py          # Synthetic dataset generator
│   ├── train.py                  # Random Forest demand forecasting model training
│   ├── evaluate.py               # 30-scenario simulation suite comparing Baseline vs Recommender
│   ├── demand_model.joblib       # Trained ML model artifact
│   └── model_metrics.json        # MAE (1.21), RMSE (3.51), R² (0.75)
│
├── docs/                         # Detailed Architectural Documentation
│   ├── problem_analysis.md
│   ├── workflow.md
│   ├── failure_analysis.md
│   ├── evaluation.md
│   └── stakeholder_validation.md
│
├── docker-compose.yml
├── .env.example
├── README.md
└── pytest.ini
```

---

## 5. Synthetic Dataset Description
The system is pre-populated with **5,193 inventory batches** across **18 pharmacy branches** and **60 medicines**:
- **Shelf-life Distribution**:
  - ~8% Expired ($\le 0$ days)
  - ~12% Critical Risk ($1–7$ days)
  - ~20% High Risk ($8–30$ days)
  - ~25% Medium Risk ($31–60$ days)
  - ~35% Normal Stock ($>60$ days)
- **8 Explicit Edge-Case Batches**:
  1. `INV-EDGE-001` (Expires before transfer can complete)
  2. `INV-EDGE-002` (No destination has demand)
  3. `INV-EDGE-003` (Source stock below 3-day safety buffer)
  4. `INV-EDGE-004` (Invalid/malformed expiry date string)
  5. `INV-EDGE-005` (Destination pharmacy closed/maintenance)
  6. `INV-EDGE-006` (Already expired batch)
  7. `INV-EDGE-007` (Sudden demand collapse)
  8. `INV-EDGE-008A/B` (Duplicate manufacturer lot across locations)

---

## 6. Recommendation Logic & Decision Formula

1. **Days to Expiry ($DTE$)** & **Local Excess Calculation**:
   $$\text{Excess} = \max(0, \text{Quantity} - [\text{Daily Demand} \times DTE] - \text{Safety Stock})$$
2. **Transit & Feasibility Validation**:
   $$\text{Remaining Post-Transit Life} = DTE - T_{\text{transit}} \ge 3 \text{ days}$$
3. **Candidate Destination Ranking**:
   $$\text{Score} = (\text{Dest Demand Velocity} \times 12.0) + (\text{Remaining Shelf Life} \times 2.5) - (\text{Distance km} \times 0.35)$$
4. **Optimal Transfer Quantity**:
   $$Q^* = \min(\text{Source Excess}, \text{Dest Consumable Window}, \text{Dest Storage Capacity})$$
5. **High-Impact Escalation Flag**:
   - Potential Value Saved $\ge ₹2,000$ OR
   - Recommended Quantity $\ge 50$ units OR
   - Days to Expiry $\le 14$ days OR
   - Life-saving / critical medication flag.

---

## 7. Machine Learning Demand Forecasting
- **Model**: `RandomForestRegressor(n_estimators=100, max_depth=10)`
- **Target**: Predicted daily dispensing demand
- **Features**: 7-day rolling velocity, 30-day average, demand volatility, store capacity, unit price, category encoding.
- **Evaluation**:
  - **MAE**: `1.2152` units/day
  - **RMSE**: `3.5170` units/day
  - **$R^2$ Score**: `0.7523`

---

## 8. Empirical Simulation Results (Baseline vs. Proposed)

Across **30 multi-scenario simulation cycles**:

| Metric | Baseline (Isolated FIFO) | Proposed Recommender | Net Gain / Impact |
|---|---|---|---|
| **Average Value Protected** | **₹75,70,344.23** | **₹83,14,345.38** | **+₹7,44,001.15 (+9.88%)** |
| **Value Lost to Expiry** | ₹14,28,450.00 | ₹6,84,448.85 | **-₹7,44,001.15 (-52.1% Loss Reduction)** |
| **Acceptance Rate** | N/A | **93.03%** | High operational compliance |
| **Avg Transit Distance** | N/A | **14.82 km** | Urban logistics efficiency |
| **Avg Shelf Life at Transfer** | N/A | **19.45 days** | Safe buffer before expiry |

---

## 9. Role-Based Access Control (RBAC) & Demo Credentials

| Role | Demo Email | Password | Access Scope |
|---|---|---|---|
| **ADMIN** | `admin@pharmacy.io` | `Admin@123` | Full access: all branches, recommendations, audit trail, re-seeding |
| **MANAGER** | `manager@pharmacy.io` | `Manager@123` | Regional oversight: all branches, approvals, analytics, simulations |
| **PHARMACIST** | `pharmacist@pharmacy.io` | `Pharmacist@123` | Scoped to Central Hub (`PHARM-001`) inventory and related transfers |
| **PHARMACIST 2** | `pharmacist2@pharmacy.io` | `Pharmacist@123` | Scoped to Indiranagar (`PHARM-002`) branch |

---

## 10. Quickstart & Local Execution

### Option A: Local Development (Zero Docker Requirement)
1. **Backend**:
   ```bash
   pip install -r backend/requirements.txt
   python backend/app/main.py
   ```
   *The backend starts at `http://localhost:8000` and automatically populates `pharmacy_db.sqlite3` with 5,000+ batches.*

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   *The frontend starts at `http://localhost:3000`.*

### Option B: Docker Compose (Full Production Multi-Service Stack)
```bash
docker compose up --build
```
- Frontend UI: `http://localhost:3000`
- Backend API Docs (Swagger): `http://localhost:8000/docs`
- PostgreSQL Database: `localhost:5432`

---

## 11. Automated Test Suite
Run the 21 comprehensive backend test cases:
```bash
pytest backend/tests/test_backend.py -v
```
**Test Coverage Includes**:
- Expiry date parsing & Days-to-Expiry math
- Risk classification ($DTE \le 7$d Critical, $8–30$d High, $31–60$d Medium, $>60$d Low, Expired)
- Excess stock calculation with 3-day safety buffer
- Haversine transit distance & transit days
- Feasibility rule blocks (transit exceeds shelf-life, closed store, no demand, expired batch)
- Authentication login & invalid password rejection
- Human approval workflow with high-impact validation
- Mandatory rejection reason category enforcement
- Override quantity workflow and value recalculation
- Audit log RBAC restriction (Pharmacist 403, Admin 200)
- Machine learning demand service inference

---

## 12. 3-Minute Interactive Demo Walkthrough
1. **Log in as Admin** via the top-right persona switcher.
2. **Dashboard**: View the live KPIs (₹2.4 Cr Inventory, ₹18.5 Lakhs at risk, ₹83.1 Lakhs protected) and inspect the *Near-Expiry Stock by Pharmacy* bar chart.
3. **Recommendations**:
   - Open a high-priority recommendation.
   - Click **Why Recommended?** to see the 100% explainable factual evidence bullets and transit math.
   - Click **Approve** on a High-Impact transfer; observe the confirmation checklist before submitting.
   - Click **Reject** on another recommendation and select a structured reason (*"Physical stock count differs"*).
   - Click **Override** on a third recommendation; change the quantity to 25 units and observe the live value recalculation.
4. **Audit Trail**: Switch to the *Audit Trail* page to view the immutable historical record of all your actions with previous & new states.
5. **Analytics & Baseline Benchmark**: View the 30-scenario simulation metrics proving a **+₹7.44 Lakhs (+9.88%)** improvement over naive FIFO. Click **Run 30-Scenario Experiment** to re-run the simulation live.
6. **Edge Cases Sandbox**: Visit the *Edge Cases Sandbox* to see live verification of all 8 safety failure guards.
7. **Switch to Pharmacist**: Use the top persona switcher to switch to `pharmacist@pharmacy.io` and notice the inventory and recommendations automatically scope exclusively to branch `PHARM-001`.
