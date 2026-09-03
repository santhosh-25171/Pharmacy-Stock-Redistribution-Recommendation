"""
ML Demand Forecasting Pipeline.
Trains an explainable Machine Learning model (Random Forest / Gradient Boosting) to predict
short-term medicine demand from historical synthetic sales and pharmacy characteristics.

Outputs:
- ml/demand_model.joblib (Saved model artifact)
- ml/model_metrics.json (MAE, RMSE, R², feature importances)
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
ML_DIR = os.path.join(BASE_DIR, "ml")

def train_demand_model():
    print("[*] Loading synthetic demand and metadata...")
    demand_df = pd.read_csv(os.path.join(DATA_DIR, "synthetic_demand.csv"))
    pharmacies_df = pd.read_csv(os.path.join(DATA_DIR, "synthetic_pharmacies.csv"))
    medicines_df = pd.read_csv(os.path.join(DATA_DIR, "synthetic_medicines.csv"))

    # Merge dataset
    df = demand_df.merge(pharmacies_df[["pharmacy_id", "storage_capacity", "operating_status"]], on="pharmacy_id")
    df = df.merge(medicines_df[["medicine_id", "category", "unit_price", "is_critical"]], on="medicine_id")

    # Filter out closed pharmacies for training demand patterns
    df = df[df["operating_status"] != "CLOSED"].copy()

    # Synthetic feature engineering: rolling estimates and trend encoding
    df["weekly_avg_daily"] = df["weekly_demand"] / 7.0
    df["monthly_avg_daily"] = df["monthly_demand"] / 30.0
    df["historical_avg_daily"] = df["historical_demand"] / 30.0
    df["demand_volatility"] = np.abs(df["weekly_avg_daily"] - df["monthly_avg_daily"])

    feature_cols_num = ["weekly_avg_daily", "monthly_avg_daily", "historical_avg_daily", "demand_volatility", "storage_capacity", "unit_price"]
    feature_cols_cat = ["category", "demand_trend", "is_critical"]
    
    X = df[feature_cols_num + feature_cols_cat]
    y = df["daily_demand"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", feature_cols_num),
            ("cat", OneHotEncoder(handle_unknown="ignore"), feature_cols_cat)
        ]
    )

    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42))
    ])

    print("[*] Training Random Forest Demand Regressor...")
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = float(mean_absolute_error(y_test, y_pred))
    mse = float(mean_squared_error(y_test, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_test, y_pred))

    print(f"[+] Model Evaluation Metrics:")
    print(f"    - MAE:  {mae:.4f} units/day")
    print(f"    - RMSE: {rmse:.4f} units/day")
    print(f"    - R²:   {r2:.4f}")

    # Extract feature importances
    onehot_features = list(model.named_steps["preprocessor"].transformers_[1][1].get_feature_names_out(feature_cols_cat))
    all_features = feature_cols_num + onehot_features
    importances = model.named_steps["regressor"].feature_importances_

    feature_importance_list = [
        {"feature": feat, "importance": round(float(imp), 4)}
        for feat, imp in sorted(zip(all_features, importances), key=lambda x: x[1], reverse=True)[:10]
    ]

    metrics = {
        "model_type": "RandomForestRegressor",
        "n_estimators": 100,
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "mae": round(mae, 4),
        "rmse": round(rmse, 4),
        "r2_score": round(r2, 4),
        "top_features": feature_importance_list,
        "trained_at": "2026-08-14T10:00:00Z"
    }

    # Save model and metrics
    model_file = os.path.join(ML_DIR, "demand_model.joblib")
    metrics_file = os.path.join(ML_DIR, "model_metrics.json")
    
    joblib.dump(model, model_file)
    with open(metrics_file, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"[OK] Saved model -> {model_file}")
    print(f"[OK] Saved metrics -> {metrics_file}")

if __name__ == "__main__":
    train_demand_model()
