"""
ClimateTwin AI - ML Baseline Model Trainer
Trains Random Forest & Gradient Boosted regressors for the 4 core climate hazards:
1. Heat Risk Model
2. Flood Risk Model
3. Air Quality Risk Model
4. Water Stress Risk Model
Exports trained weights to models/*.joblib for seamless FastAPI backend inference.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

DATASET_PATH = "datasets/pune_environmental_historical.csv"
MODELS_DIR = "models"

def train_and_export_models():
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}. Run scripts/build_unified_dataset.py first.")

    os.makedirs(MODELS_DIR, exist_ok=True)
    df = pd.read_csv(DATASET_PATH)
    print(f"Loaded {len(df)} records from {DATASET_PATH}\n" + "=" * 50)

    # 1. HEAT RISK MODEL
    X_heat = df[["temp_c", "humidity_pct", "heat_index_c", "is_summer_season"]]
    y_heat = df["target_heat_risk"]
    X_train, X_test, y_train, y_test = train_test_split(X_heat, y_heat, test_size=0.2, random_state=42)

    heat_rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    heat_rf.fit(X_train, y_train)
    y_pred = heat_rf.predict(X_test)
    print(f"[Heat Model] MAE: {mean_absolute_error(y_test, y_pred):.2f} | R²: {r2_score(y_test, y_pred):.3f}")
    heat_path = os.path.join(MODELS_DIR, "heat_model.joblib")
    joblib.dump(heat_rf, heat_path)
    print(f" -> Saved to {heat_path}")

    # 2. FLOOD RISK MODEL
    X_flood = df[["precip_current_mm", "precip_24h_sum_mm", "is_monsoon_season"]]
    y_flood = df["target_flood_risk"]
    X_train, X_test, y_train, y_test = train_test_split(X_flood, y_flood, test_size=0.2, random_state=42)

    flood_rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    flood_rf.fit(X_train, y_train)
    y_pred = flood_rf.predict(X_test)
    print(f"[Flood Model] MAE: {mean_absolute_error(y_test, y_pred):.2f} | R²: {r2_score(y_test, y_pred):.3f}")
    flood_path = os.path.join(MODELS_DIR, "flood_model.joblib")
    joblib.dump(flood_rf, flood_path)
    print(f" -> Saved to {flood_path}")

    # 3. AIR QUALITY RISK MODEL
    X_aqi = df[["aqi", "pm2_5", "pm10", "wind_speed_kmh"]]
    y_aqi = df["target_air_quality_risk"]
    X_train, X_test, y_train, y_test = train_test_split(X_aqi, y_aqi, test_size=0.2, random_state=42)

    aqi_rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    aqi_rf.fit(X_train, y_train)
    y_pred = aqi_rf.predict(X_test)
    print(f"[Air Quality Model] MAE: {mean_absolute_error(y_test, y_pred):.2f} | R²: {r2_score(y_test, y_pred):.3f}")
    aqi_path = os.path.join(MODELS_DIR, "air_quality_model.joblib")
    joblib.dump(aqi_rf, aqi_path)
    print(f" -> Saved to {aqi_path}")

    # 4. WATER STRESS RISK MODEL
    X_water = df[["precip_24h_sum_mm", "temp_c", "month"]]
    y_water = df["target_water_stress_risk"]
    X_train, X_test, y_train, y_test = train_test_split(X_water, y_water, test_size=0.2, random_state=42)

    water_rf = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
    water_rf.fit(X_train, y_train)
    y_pred = water_rf.predict(X_test)
    print(f"[Water Stress Model] MAE: {mean_absolute_error(y_test, y_pred):.2f} | R²: {r2_score(y_test, y_pred):.3f}")
    water_path = os.path.join(MODELS_DIR, "water_stress_model.joblib")
    joblib.dump(water_rf, water_path)
    print(f" -> Saved to {water_path}")

    print("=" * 50)
    print("All 4 ML Hazard Models trained and exported successfully!")

if __name__ == "__main__":
    train_and_export_models()

