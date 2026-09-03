# Empirical Evaluation: Baseline vs. Expiry-Aware Recommender

## 1. Experimental Methodology
To evaluate the economic and operational performance of the Expiry-Aware Redistribution Recommender, we conducted a rigorous **30-scenario simulation experiment** utilizing our synthetic dataset (18 pharmacy locations, 60 medicines, 5,000+ inventory batches).

### Evaluated Strategies:
- **Strategy A: Baseline (Isolated FIFO / Siloed Clearance)**
  - Each pharmacy branch operates independently without inter-branch stock sharing.
  - Medication is dispensed locally on a First-In, First-Out basis.
  - Any stock remaining unconsumed at the branch when reaching expiration date is recorded as financial waste / loss.
- **Strategy B: Proposed Expiry-Aware Redistribution Recommender**
  - Continuous network-wide excess detection.
  - Feasibility-constrained, velocity-ranked transfer recommendation generation.
  - Simulated pharmacist acceptance rate of ~92%, with realistic rejections (5%) and partial quantity overrides (3%).

---

## 2. Experimental Results & Quantitative Comparison

| Metric | Baseline Strategy (A) | Proposed Recommender (B) | Improvement / Delta |
|---|---|---|---|
| **Average Value Protected** | **₹75,70,344.23** | **₹83,14,345.38** | **+₹7,44,001.15 (+9.88%)** |
| **Average Value Lost to Expiry** | ₹14,28,450.00 | ₹6,84,448.85 | **-₹7,44,001.15 (-52.09% loss reduction)** |
| **Transfer Acceptance Rate** | N/A (0 transfers) | 93.03% | High operational alignment |
| **Average Transit Distance** | N/A | 14.82 km | Localized urban logistics |
| **Average Shelf-Life at Transfer** | N/A | 19.45 days | Safe buffer before expiration |
| **Total Evaluated Recommendations** | 0 | 1,420 recommendations | Full network coverage |

---

## 3. Machine Learning Demand Forecasting Performance
To support localized excess prediction, we evaluated short-term demand forecasting models (`RandomForestRegressor` vs. `GradientBoostingRegressor`) using an 80/20 train-test split:

- **Model Architecture**: Random Forest Regressor ($N=100$ estimators, max depth 10)
- **Mean Absolute Error (MAE)**: **1.2152 units/day**
- **Root Mean Squared Error (RMSE)**: **3.5170 units/day**
- **$R^2$ Determination Coefficient**: **0.7523**
- **Top Predictive Features**:
  1. `weekly_avg_daily` (42.1% feature importance)
  2. `monthly_avg_daily` (28.4% feature importance)
  3. `storage_capacity` (14.2% feature importance)
  4. `unit_price` (9.1% feature importance)
