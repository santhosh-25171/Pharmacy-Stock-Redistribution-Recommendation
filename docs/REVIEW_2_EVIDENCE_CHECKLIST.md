# PharmaShift: Review #2 Evidence Checklist
**Project Milestone**: Review #2 Target (Minimum 70% Completion)  
**Report Date**: September 28, 2026  
**Status**: All Evidence Verified & Ready for Submission

---

## 1. Screenshot Preparation Checklist (Figures 1 – 9)

Capture and insert these exact 9 screenshots into `docs/REVIEW_2_REPORT.md` before submission:

| Figure # | Title | Required Content & Location | Status |
|---|---|---|---|
| **Figure 1** | **System Dashboard** | Top hero AI Action Center, Subsystem Health Strip, Demand Intelligence card, KPI summary cards (`http://localhost:3000/`) | [ ] Ready to Capture |
| **Figure 2** | **Inventory Monitor** | Paginated inventory table with batch codes, medicine names, days-to-expiry badges, and safety buffers (`http://localhost:3000/inventory`) | [ ] Ready to Capture |
| **Figure 3** | **AI Recommendation** | Recommendations cards / table view showing transfer routes, quantities, potential value saved, and transit duration (`http://localhost:3000/recommendations`) | [ ] Ready to Capture |
| **Figure 4** | **Recommendation Evidence** | Evidence Modal showing the 0–100 Recommendation Score, Demand Intelligence banner, and Safety Checklist | [ ] Ready to Capture |
| **Figure 5** | **ML Demand Evaluation** | Demand Intelligence Card showing Random Forest MAE (1.2152), RMSE (3.5170), R² (0.7523), and feature importances | [ ] Ready to Capture |
| **Figure 6** | **Analytics / Baseline** | 30-scenario simulation bar chart and KPI cards showing +₹7.44L (+9.88%) improvement over FIFO baseline (`http://localhost:3000/analytics`) | [ ] Ready to Capture |
| **Figure 7** | **Edge Case Sandbox** | 8 deterministic safety scenarios with Input Condition, Expected/Actual results, and PASS badges (`http://localhost:3000/edge-cases`) | [ ] Ready to Capture |
| **Figure 8** | **Audit Trail** | Immutable audit table showing timestamp, actor email, role, action, previous/new state, and reason notes (`http://localhost:3000/audit-logs`) | [ ] Ready to Capture |
| **Figure 9** | **Pharmacy Network** | Bangalore SVG spatial network mesh map with transfer vectors and hovered Node Balance state (`http://localhost:3000/pharmacies`) | [ ] Ready to Capture |

---

## 2. Test Execution & Build Evidence

Prepare terminal outputs or logs proving test and build execution:

- [x] **Pytest Execution Output**:
  ```bash
  pytest backend/tests/test_backend.py -v
  ```
  *Evidence: 30 passed in 76.87s (100% pass rate).*
- [x] **Frontend Production Build Output**:
  ```bash
  cd frontend && npm run build
  ```
  *Evidence: Built in 14.98s, 2,353 modules transformed, 0 errors.*
- [x] **Subsystem Health Endpoint Output**:
  ```bash
  curl http://localhost:8000/health
  ```
  *Evidence: Returns status "healthy", Random Forest loaded, and reference date "2026-08-14".*

---

## 3. GitHub Repository Verification Checklist

Verify that the following repository files are committed and synchronized:

- [x] `backend/app/services/ml_service.py` (Random Forest inference, cache, fallback)
- [x] `backend/app/recommender/engine.py` (Predicted demand scoring, checklist evidence)
- [x] `backend/app/recommender/risk_scorer.py` (Deterministic reference date configuration)
- [x] `backend/app/main.py` (Subsystem health endpoint, seed endpoint admin security)
- [x] `backend/tests/test_backend.py` (30 comprehensive automated tests)
- [x] `frontend/src/pages/Dashboard.jsx` (AI Action Center, Demand card, Priority Queue Table)
- [x] `frontend/src/components/EvidenceModal.jsx` (Recommendation Score, Demand banner, Checklist)
- [x] `frontend/src/components/NetworkMap.jsx` (Node balance classifications and legend)
- [x] `docs/REVIEW_2_REPORT.md` (Complete 30-section Review #2 report)
- [x] `docs/REVIEW_2_EVIDENCE_CHECKLIST.md` (Submission evidence checklist)
- [x] `docs/review2_improvements.md` (Detailed Review #1 improvement tracking)
- [x] `docs/review2_readiness.md` (78.5% completion matrix across 18 areas)
- [x] `docs/architecture.md` (Full architectural blueprint)
- [x] `docs/ml.md` (Demand forecasting specification)
- [x] `docs/api.md` (Complete REST API reference)
- [x] `docs/evaluation.md` & `README.md` (Synchronized with `data/simulation_results.json`)

---

## 4. Viva / Demonstration Sequence (16-Step Script)

1. **Step 1**: Show `http://localhost:3000` with the Subsystems Health Strip (`Ref Date: 2026-08-14`, `Demand Model: Loaded`).
2. **Step 2**: Point out the **AI Action Center** hero card spotlighting the highest-value urgent transfer.
3. **Step 3**: Point out the **Demand Intelligence Card** showcasing Random Forest metrics ($R^2=0.7523, MAE=1.2152$).
4. **Step 4**: Scroll to the **Priority Recommendations Queue Table** showing predicted demand and scores.
5. **Step 5**: Click `Why?` to open the **Evidence Modal** showing the 0–100 Recommendation Score and Safety Checklist.
6. **Step 6**: Click `Approve` to approve a transfer and show instant status update.
7. **Step 7**: Go to `Recommendations` tab, demonstrate filter pills and search bar.
8. **Step 8**: Click `Reject` on a recommendation and select a mandatory reason (`STOCK_COUNT_MISMATCH`).
9. **Step 9**: Click `Override` on another recommendation, change quantity from 50 to 25 units, and observe live value recalculation.
10. **Step 10**: Go to `Pharmacies`, hover over nodes to show real-time **Node Balance Classifications** (`Balanced`, `Excess`, `Shortage`).
11. **Step 11**: Go to `Edge Cases Sandbox` to demonstrate that all 8 safety failure guards deterministically pass.
12. **Step 12**: Go to `Audit Trail` (as Admin) to demonstrate immutable compliance records of approvals, rejections, and overrides.
13. **Step 13**: Switch persona to `Pharmacist`, show that Audit Logs are blocked (403) and inventory scopes to `PHARM-001`.
14. **Step 14**: In `Settings`, show that database re-seeding requires the `ADMIN` role.
15. **Step 15**: Go to `Analytics` to present the 30-scenario simulation benchmark (+₹7.44L gain, -52.09% loss reduction across 1,794 recs).
16. **Step 16**: Open `docs/REVIEW_2_REPORT.md` to prove the **78.5% completion milestone**.
