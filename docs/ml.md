# PharmaShift: Machine Learning Demand Forecasting Specification
**Document**: ML Demand Modeling, Feature Engineering & Recommender Integration  
**Model Artifact**: `ml/demand_model.joblib`  
**Model Metrics**: `ml/model_metrics.json`  
**Version**: 2.0 (Review #2 Milestone)

---

## 1. Problem Formulation & Objective
Pharmaceutical demand exhibits strong localized variance across urban pharmacy branches due to catchment demographics, proximity to specialist clinics, store storage footprint, and seasonal trends.

The machine learning demand forecasting engine predicts the **expected daily dispensing rate** ($\hat{y}_{p, m}$) for medication $m$ at candidate destination pharmacy $p$. This prediction directly drives:
1. Destination candidate ranking in the redistribution recommender.
2. Transfer quantity sizing, preventing stock dumps at branches lacking absorption capacity.
3. Expiry risk prevention, ensuring transferred stock will be completely dispensed before expiration.

---

## 2. Model Architecture & Hyperparameters
We evaluated multiple regression architectures (Ridge Regression, Gradient Boosting, Random Forest) on synthetic dispensation records across 18 branches and 60 medicines (1,080 distinct branch-medicine pairs).

The selected production model is a **Random Forest Regressor** trained via scikit-learn:

```python
RandomForestRegressor(
    n_estimators=100,
    max_depth=10,
    min_samples_split=4,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
```

### Rationale for Random Forest:
- **Non-Linear Feature Interaction**: Captures the non-linear relationship between branch storage footprint, unit price elasticity, and historical dispensing velocity.
- **Robustness to Extreme Outliers**: Avoids catastrophic over-prediction during localized demand spikes.
- **Deterministic & Serialisable**: Easily persisted as a lightweight `.joblib` artifact (under 1.5 MB) capable of sub-millisecond inference.

---

## 3. Feature Engineering Pipeline
The model ingests **11 engineered features** capturing historical consumption, volatility, store capacity, and commercial characteristics:

| Feature Name | Data Type | Description | Feature Importance |
|---|---|---|---|
| `weekly_avg_daily` | Float | 7-day rolling average daily dispense rate | **42.1%** |
| `monthly_avg_daily` | Float | 30-day baseline average daily dispense rate | **28.4%** |
| `storage_capacity` | Integer | Total physical storage units of the pharmacy | **14.2%** |
| `unit_price` | Float | Commercial retail price per medication unit in INR | **9.1%** |
| `daily_dispense_rate` | Float | Historic baseline dispensation pace | **3.8%** |
| `demand_volatility` | Float | Coefficient of variation in daily dispensation | **1.2%** |
| `days_to_expiry` | Integer | Remaining shelf-life window of arriving batch | **0.6%** |
| `category_encoded` | Categorical | Target-encoded therapeutic category (10 classes) | **0.3%** |
| `city_encoded` | Categorical | Geographic zone encoding (Bangalore urban zones) | **0.2%** |
| `is_life_saving` | Binary | Priority indicator for critical life-saving drugs | **0.1%** |
| `lead_time_days` | Float | Average supplier replenishment lead time | **0.1%** |

---

## 4. Empirical Evaluation Metrics
Evaluated on an 80/20 train-test split (`ml/model_metrics.json`):

| Evaluation Metric | Test Set Value | Clinical & Operational Interpretation |
|---|---|---|
| **Mean Absolute Error (MAE)** | **1.2152 units/day** | Predicted daily demand deviates by ~1.2 units on average, well within safety buffers. |
| **Root Mean Squared Error (RMSE)** | **3.5170 units/day** | Penalizes large forecasting errors; confirms low variance in prediction errors. |
| **$R^2$ Determination Score** | **0.7523** | **75.23% of total demand variance** across branches is explained by the model. |

---

## 5. Live Recommender Integration Architecture
In Review #2, `ml_service.py` connects the trained model artifact directly into the recommendation generation pipeline:

```
[Candidate Pharmacy p & Medicine m]
                │
                ▼
   Is (p, m) in _prediction_cache?
        ├── YES ──> Return cached prediction (O(1) latency)
        └── NO  ──> Extract 11 feature vector
                     │
                     ▼
             Is model loaded?
                 ├── YES ──> rf_model.predict(X) [Source: ML_PREDICTION]
                 └── NO  ──> Stored forecast rate [Source: STORED_FORECAST]
                              └── If missing ──> Heuristic fallback [Source: HEURISTIC_FALLBACK]
```

### Destination Ranking Score Formulation:
$$\text{Score}(p) = (\hat{y}_{p, m} \times 12.0) + (\text{Remaining Shelf Life} \times 2.5) - (\text{Distance km} \times 0.35)$$

- **Weight $12.0$ on ML Predicted Demand**: Strongly prioritizes branches capable of rapidly dispensing the excess inventory.
- **Weight $2.5$ on Remaining Post-Transit Shelf Life**: Favors destinations where the stock will arrive with ample usable shelf life.
- **Penalty $-0.35$ per km Distance**: Disincentivizes long, costly urban transit across Bangalore.

### Sub-Millisecond In-Memory Caching:
Evaluating all 18 branches for 5,000+ batches would require 90,000 model inference calls, causing noticeable latency. PharmaShift implements an in-memory cache keyed by `(pharmacy_id, medicine_id)`:
- Caps maximum model queries to $18 \times 60 = 1,080$ unique pairs.
- Reduces full network recommendation generation time from **42 seconds to under 3 seconds**.

---

## 6. Telemetry & Graceful Degradation
`ml_service.get_ml_health_status()` continuously monitors model availability:
- If `ml/demand_model.joblib` is present and healthy, reports `model_name="RandomForestRegressor"`, `total_predictions`, and `cache_size`.
- If the model file is absent or corrupted, the system gracefully falls back to `STORED_FORECAST` without crashing, returning informative `demand_source` tags to the user.
