# PharmaShift: Review #3 Evaluation Readiness & Presentation Script

This document provides the operational readiness checklist and step-by-step demonstration walkthrough script for the official **Review #3** project defense.

---

## 1. Review #3 Readiness Checklist

| Category | Verification Item | Status | Verification Evidence |
|---|---|:---:|---|
| **Authentication** | Login page appears first upon opening website | **VERIFIED** | `frontend/src/pages/Login.jsx` & `App.jsx` |
| **Authentication** | Unauthenticated direct dashboard access blocked | **VERIFIED** | `App.jsx` strict routing (`if (!user) return <Login />`) |
| **Authentication** | Valid login works & generates signed JWT | **VERIFIED** | `POST /api/auth/login` (Admin/Manager/Pharmacist) |
| **Authentication** | Invalid login rejected with clear error alert | **VERIFIED** | HTTP 401 alert banner rendered |
| **Authentication** | Visible Logout button clears state & redirects | **VERIFIED** | Navbar & Sidebar Sign Out buttons |
| **RBAC** | Pharmacist inventory and transfer scoping | **VERIFIED** | Query filters to `assigned_pharmacy_id` |
| **RBAC** | Admin-only seed endpoint protected | **VERIFIED** | Non-Admin receives HTTP 403 Forbidden |
| **Testing** | Automated unit & API tests executed | **VERIFIED** | **49 / 49 tests passing** (`pytest`) |
| **Testing** | Tests categorized across all 16 domains | **VERIFIED** | Documented in `docs/testing.md` |
| **Error Handling**| React Error Boundaries active around pages | **VERIFIED** | `frontend/src/components/ErrorBoundary.jsx` |
| **Error Handling**| Controlled error fallback & recovery button | **VERIFIED** | "Retry Section" resets boundary state |
| **Error Handling**| Backend HTTP status codes standardized | **VERIFIED** | 400, 401, 403, 404, 422, 500 handlers in `main.py` |
| **API Docs** | Complete API endpoints documented in README | **VERIFIED** | README Section 16 & `docs/api.md` |
| **DB Schema** | Database schema documented in README & docs | **VERIFIED** | README Section 17 & `docs/database_schema.md` |
| **Code Quality** | Complex logic commented with "WHY" rationales | **VERIFIED** | `engine.py`, `feasibility.py`, `ml_service.py`, etc. |
| **Frontend Build**| Production bundle builds cleanly | **VERIFIED** | `npx.cmd vite build` (Exit code 0, 0 errors) |
| **Cleanliness** | Zero secrets, credentials, or caches committed | **VERIFIED** | `.gitignore` active, `.env.example` placeholders |

---

## 2. 17-Step Review #3 Live Demonstration Script

Follow this structured protocol during the live evaluator presentation:

### Phase 1: Authentication & Route Protection (Steps 1–5)
1. **Step 1: Open Application**
   - Navigate to `http://localhost:3000`.
   - **Show Evaluator**: The **Login Page** appears first. The dashboard is completely inaccessible until authentication is complete.
2. **Step 2: Demonstrate Invalid Login Handling**
   - Type an invalid email/password (`test@pharmacy.io` / `wrongpass`) and click *Sign In*.
   - **Show Evaluator**: The system catches the 401 response and displays a styled error banner: *"Authentication Error: Incorrect email or password"*.
3. **Step 3: Successful Authentication via Quick-Fill**
   - In the *Review Evaluation Quick-Fill* panel, click **Admin**. Notice the credentials automatically populate.
   - Click **Sign In to Dashboard**.
   - **Show Evaluator**: The button shows a loading spinner, establishes the JWT bearer session, and redirects to the protected Dashboard.
4. **Step 4: Verify Session Logout**
   - Click the **Sign Out** button in the top navigation bar.
   - **Show Evaluator**: The JWT token is cleared from `localStorage` and the application immediately returns to the Login page.
5. **Step 5: Verify Route Protection After Logout**
   - Attempt to interact with or navigate back to the dashboard.
   - **Show Evaluator**: Access is strictly blocked; the Login page persists.

---

### Phase 2: Role Scoping & Operational Modules (Steps 6–10)
6. **Step 6: Log In as Pharmacist (Branch Scoping)**
   - Click **Pharmacist (Central Hub PHARM-001)** quick-fill and log in.
   - Open **Inventory Monitor**.
   - **Show Evaluator**: Notice the inventory table is strictly scoped exclusively to `PHARM-001` batches, demonstrating RBAC in action.
7. **Step 7: Log In as Admin (Network Overview)**
   - Click the user switcher or log out and log in as **Admin**.
   - Open **Inventory Monitor**.
   - **Show Evaluator**: The Admin sees all 5,193 batches across all 18 network branches, with real-time risk badges (`CRITICAL`, `HIGH`, `MEDIUM`).
8. **Step 8: Demand Intelligence & ML Prediction**
   - Open **Transfer Recommendations**.
   - Point out the **Demand Source** column (`ML_PREDICTION` via `RandomForestRegressor`).
   - Highlight the **Recommendation Score** (0–100 normalized score).
9. **Step 9: Explainable Recommendation Evidence**
   - Click **Why Recommended?** on a pending recommendation.
   - **Show Evaluator**: Open the modal displaying 100% transparent, factual evidence bullets (Source excess units, ML predicted destination demand velocity, transit distance, remaining post-transit shelf-life, and storage capacity).
10. **Step 10: Human-in-the-Loop Actions**
    - Click **Approve** on a High-Impact transfer; demonstrate that the system enforces an explicit confirmation checkbox.
    - Click **Reject** on another recommendation; demonstrate mandatory selection of a structured rejection reason (*"Physical stock count differs"*).
    - Click **Override** on a third recommendation; alter the quantity to 25 units and observe the dynamic value recalculation.

---

### Phase 3: Traceability, Resilience & Verification (Steps 11–17)
11. **Step 11: Audit Trail Compliance**
    - Navigate to **Audit Trail**.
    - **Show Evaluator**: Point out the immutable logs capturing the approval, rejection, and override events executed in Step 10, complete with user email, timestamp, and previous vs. new states.
12. **Step 12: Analytics & Simulation Benchmarks**
    - Navigate to **Analytics & Baseline**.
    - Point out the empirical 30-scenario simulation results: **+₹7.44 Lakhs (+9.88%)** value protected and **-52.1% waste reduction** compared to naive isolated FIFO.
13. **Step 13: Operational Edge Cases Sandbox**
    - Navigate to **Edge Cases Sandbox**.
    - **Show Evaluator**: Review the 8 operational edge cases (e.g. transit exceeding shelf-life, closed destination, zero demand, duplicate batch codes) and show that each safety guard blocked unsafe transfers.
14. **Step 14: Demonstrate Error Boundary Resilience**
    - Point out how each major view is encapsulated within `<ErrorBoundary />` to isolate unexpected client rendering exceptions.
15. **Step 15: Showcase API Documentation**
    - Open `http://localhost:8000/docs` (Swagger UI) or `README.md` Section 16.
    - **Show Evaluator**: Point out the complete endpoint directory across all 9 routers.
16. **Step 16: Showcase Database Schema Documentation**
    - Open `README.md` Section 17 or `docs/database_schema.md`.
    - **Show Evaluator**: Review the 10 SQLAlchemy models, foreign key relationships, and the Mermaid ER diagram.
17. **Step 17: Showcase Automated Testing Results**
    - Show `docs/testing.md` and terminal pytest output: **49 passed in 50 seconds**, covering all 16 requested categories.
