# PharmaShift: System Architecture Specification
**Document**: Architectural Blueprint & Implementation Guide  
**Version**: 2.0 (Review #2 Milestone)  
**Status**: Implemented & Validated

---

## 1. High-Level Architectural Overview
PharmaShift is designed as a decoupled, microservice-ready full-stack platform consisting of a high-performance **FastAPI (Python 3.11+)** backend, an interactive **React 18 (Vite)** single-page application, an integrated **scikit-learn** predictive machine learning inference engine, and a dual-dialect **SQLAlchemy ORM** database layer supporting both SQLite (local zero-config) and PostgreSQL (production Docker Compose).

```
+--------------------------------------------------------------------------+
|                        React 18 SPA (Vite + Tailwind)                   |
|  - AI Action Center      - Recommendations Queue    - Network Mesh Map   |
|  - Demand Telemetry      - Evidence / HITL Modals   - Analytics & Audit  |
+------------------------------------+-------------------------------------+
                                     | JSON / REST / JWT Bearer
                                     v
+------------------------------------+-------------------------------------+
|                     FastAPI Backend Application                          |
|  - Routers: auth, inventory, pharmacies, medicines, recommendations,    |
|             analytics, evaluation, audit_logs, edge_cases               |
|  - Security: JWT tokens, role-based access control (ADMIN/MGR/PHARM)     |
|  - Lifespan Service: Auto-seeding, deterministic reference date setup    |
+-----------------+-------------------+-------------------+----------------+
                  |                   |                   |
                  v                   v                   v
+-----------------+----+      +-------+----------+      +-+----------------+
|  Recommender Engine  |      |   ML Demand      |      |   SQLAlchemy     |
|  - Excess Stock Math |      |   Service        |      |   ORM Layer      |
|  - Risk Scorer (DTE) |<---->| - Random Forest  |      | - Dual Support:  |
|  - Haversine Routing |      | - 11 Features    |      |   PostgreSQL /   |
|  - Safety Feasibility|      | - O(1) Cache     |      |   SQLite3        |
+----------------------+      +------------------+      +------------------+
```

---

## 2. Recommendation Engine Pipeline Flow
The core value proposition of PharmaShift is its 6-stage algorithmic redistribution pipeline, executed asynchronously across all network inventory batches:

```
[Stage 1: Batch Ingestion & Expiry Risk Scoring]
   │ - Calculate Days to Expiry (DTE) relative to configured Reference Date (2026-08-14)
   │ - Classify Risk: Expired (<=0d), Critical (1-7d), High (8-30d), Medium (31-60d), Low (>60d)
   ▼
[Stage 2: Source Surplus & Local Safety Stock Calculation]
   │ - Compute local consumption: Local Need = Daily Dispense Rate * DTE
   │ - Apply Safety Buffer: 3 days of mandatory local emergency stock
   │ - Excess Stock = max(0, Quantity - Local Need - Safety Buffer)
   │ - If Excess Stock <= 0, batch is retained locally (transfer aborted)
   ▼
[Stage 3: Candidate Destination Discovery & Feasibility Filtering]
   │ - For all other operating branches:
   │   * Check operating status: Destination must NOT be CLOSED or in MAINTENANCE
   │   * Compute Haversine distance: Distance km and transit days (1 day per 50 km)
   │   * Feasibility Constraint: DTE - Transit Days >= 3 days post-arrival
   ▼
[Stage 4: ML-Driven Destination Ranking & Scoring]
   │ - Query ML Demand Service for predicted destination consumption rate
   │ - Calculate Destination Score:
   │     Score = (Predicted Demand * 12.0) + (Post-Transit Life * 2.5) - (Distance km * 0.35)
   │ - Rank candidate destinations and select the optimal destination
   ▼
[Stage 5: Optimal Transfer Quantity & Economic Impact Determination]
   │ - Transfer Qty = min(Source Excess, Dest Consumable in Window, Dest Spare Capacity)
   │ - Value Protected = Transfer Qty * Medicine Unit Price
   │ - Evaluate High-Impact Flag: Value >= ₹2,000 OR Qty >= 50 OR DTE <= 14 days
   ▼
[Stage 6: Explainable Evidence Generation & Human-in-the-Loop Routing]
   │ - Generate factual evidence bullets and checklist assertions
   │ - Route to PENDING queue for pharmacist review / approval / override
```

---

## 3. Database Architecture & Schema ERD
The system implements a normalized relational database schema via SQLAlchemy ORM:

- **User**: Authentication credentials, hashed password (bcrypt), assigned role (`ADMIN`, `MANAGER`, `PHARMACIST`), associated branch.
- **Pharmacy**: Physical branch metadata, geographic coordinates (`latitude`, `longitude`), total storage capacity, operational status (`ACTIVE`, `MAINTENANCE`, `CLOSED`).
- **Medicine**: Pharmaceutical master table, chemical category, unit price, standard unit.
- **InventoryBatch**: Specific lot records, batch code, source pharmacy, medicine, current quantity, expiration date, days-to-expiry, risk level.
- **DemandForecast**: Historical baseline statistics (daily dispense rate, 7-day velocity, 30-day velocity).
- **TransferRecommendation**: Generated redistribution suggestions, source pharmacy, destination pharmacy, batch, recommended quantity, potential value saved, days to expiry, distance km, estimated transit days, recommendation score, predicted demand, demand source, status (`PENDING`, `APPROVED`, `REJECTED`, `OVERRIDDEN`), high-impact flag.
- **RecommendationEvidence**: Structured factual evidence bullets and checklist verifications linked 1-to-many with recommendations.
- **TransferAction**: Human-in-the-loop decisions (approval notes, rejection reasons, override quantities).
- **AuditLog**: Immutable historical audit trail recording every state change, actor, role, timestamp, and reasoning.

---

## 4. Frontend Architecture
The frontend is built with React 18 using modern functional components, hooks, and clean layer separation:
- **Routing & Navigation**: Single-page application with responsive sidebar navigation and tab switching.
- **State Management**:
  - `AuthContext`: Centralized authentication provider managing JWT persistence in `localStorage`, role resolution, and persona switching for demonstrations.
  - Component-level state with optimistic updates for approval and override actions.
- **UI & Visualization Components**:
  - `Dashboard.jsx`: Executive AI Action Center, Demand Intelligence telemetry card, KPI cards, Recharts bar and pie charts, Priority Recommendations Queue Table.
  - `Recommendations.jsx`: Filterable queue (Status, Risk Level, High-Impact), search bar, card and table views.
  - `EvidenceModal.jsx`: Calibrated Recommendation Score, Demand Intelligence banner, structured Safety & Feasibility checklist.
  - `NetworkMap.jsx`: SVG-based spatial logistics mesh visualizing inter-pharmacy transfer vectors and node balance states.
  - `AuditLogs.jsx`: Filterable compliance table with actor, role, recommendation ID, and state transitions.
  - `EdgeCases.jsx`: Interactive safety sandbox demonstrating the 8 deterministic clinical safety blocks.
  - `Analytics.jsx`: Empirical benchmark dashboard comparing naive FIFO baseline against the proposed recommender across 30 simulation scenarios.
  - `Settings.jsx`: Escalation threshold sliders, demo accounts table, and role-enforced database re-seeding.

---

## 5. Security & Governance Architecture
1. **Password Security**: Direct `bcrypt` hashing with salt rounds, zero reliance on vulnerable legacy wrappers.
2. **Stateless JWT Authentication**: Signed with HS256, configurable secret key and expiration, bearer token injection via Axios interceptors.
3. **Role-Based Access Control (RBAC)**:
   - `ADMIN`: Full global read/write, audit inspection, database reset.
   - `MANAGER`: Multi-branch oversight, approval/override authority, analytics access.
   - `PHARMACIST`: Branch-scoped inventory and transfer operations.
4. **Administrative Hardening**: `POST /api/seed` strictly guarded with `require_roles(["ADMIN"])`.
5. **Immutable Audit Trail**: Any write operation (approval, rejection, override, batch regeneration, database seed) commits an immutable row into the `audit_logs` table.
