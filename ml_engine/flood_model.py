"""
ClimateTwin AI — Module 4: Rainfall & Flood-Risk Prediction Model
Module: ml_engine/flood_model.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Objective:
1. Separate short-term rainfall forecasting from flood-hazard estimation.
2. Estimate hydrometeorological flood hazard (0-100) using current rainfall,
   antecedent cumulative rainfall (3d, 7d, 14d), rainfall intensity, soil moisture
   saturation, elevation, slope, and drainage capacity.

Scientific Distinction:
High rainfall alone does not automatically guarantee flooding. Where street-level
hydrodynamic inundation labels are unavailable, this module explicitly implements a
Hydrometeorological Rainfall-Runoff Flood-Hazard Proxy.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

from ml_engine.config import (
    FLOOD_MODEL_DIR,
    MODEL_VERSION,
    RANDOM_SEED,
    score_to_risk_level,
)
from ml_engine.reference_data import compute_flood_hazard_proxy


FLOOD_MODEL_FEATURES: List[str] = [
    "rainfall_mm",
    "rainfall_intensity_mm_hr",
    "rainfall_lag_1d",
    "rainfall_lag_3d",
    "rainfall_rolling_3d_sum",
    "rainfall_rolling_7d_sum",
    "rainfall_rolling_14d_sum",
    "rainfall_anomaly_mm",
    "rainfall_intensity_ratio",
    "soil_moisture",
    "humidity_pct",
    "pressure_hpa",
    "elevation_m",
    "slope_deg",
    "drainage_index",
    "runoff_potential_index",
    "topographic_flood_susceptibility",
    "is_monsoon_season",
]


class FloodRiskModel:
    """
    Separates next-day rainfall estimation from hydrometeorological flood-hazard
    estimation. Compares Ridge Baseline, Random Forest, and XGBoost/GradientBoosting.
    """

    def __init__(self, model_dir: Optional[Path] = None) -> None:
        self.model_dir: Path = Path(model_dir) if model_dir else FLOOD_MODEL_DIR
        self.model_path: Path = self.model_dir / "flood_model.joblib"
        self.meta_path: Path = self.model_dir / "flood_metadata.json"

        self.feature_names: List[str] = list(FLOOD_MODEL_FEATURES)
        self.selected_model_name: Optional[str] = None
        self.model: Any = None
        self.rainfall_forecaster: Any = None
        self.candidate_metrics: Dict[str, Dict[str, float]] = {}
        self.rainfall_forecast_metrics: Dict[str, float] = {}
        self.training_feature_means: Dict[str, float] = {}
        self.residual_std: float = 3.5
        self.is_trained: bool = False

    @staticmethod
    def _evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray, clip_100: bool = True) -> Dict[str, float]:
        preds = np.clip(y_pred, 0.0, 100.0) if clip_100 else np.clip(y_pred, 0.0, None)
        mse = float(mean_squared_error(y_true, preds))
        return {
            "MAE": round(float(mean_absolute_error(y_true, preds)), 4),
            "MSE": round(mse, 4),
            "RMSE": round(float(np.sqrt(mse)), 4),
            "R2": round(float(r2_score(y_true, preds)), 4),
        }

    def train_and_select(
        self,
        df_features: pd.DataFrame,
        target_col: str = "flood_risk_target",
        train_frac: float = 0.70,
        val_frac: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Train both:
        1. Auxiliary next-day rainfall forecaster (`rainfall_mm` at t+1).
        2. Primary Hydrometeorological Flood-Hazard Proxy model (0-100).
        Uses strict chronological splitting.
        """
        df = df_features.copy()
        if target_col not in df.columns:
            df[target_col] = compute_flood_hazard_proxy(df)

        missing_feats = [f for f in self.feature_names if f not in df.columns]
        if missing_feats:
            raise ValueError(f"Missing required flood model features: {missing_feats}")

        n = len(df)
        train_end = int(n * train_frac)
        val_end = int(n * (train_frac + val_frac))

        X = df[self.feature_names].to_numpy(dtype=float)
        y = df[target_col].to_numpy(dtype=float)

        X_train, y_train = X[:train_end], y[:train_end]
        X_val, y_val = X[train_end:val_end], y[train_end:val_end]
        X_test, y_test = X[val_end:], y[val_end:]

        self.training_feature_means = {
            f: float(np.mean(X_train[:, idx])) for idx, f in enumerate(self.feature_names)
        }

        # 1. Auxiliary Next-Day Rainfall Forecaster (strictly causal shift(-1) on train slice)
        next_day_rain = df["rainfall_mm"].shift(-1).fillna(df["rainfall_mm"]).to_numpy(dtype=float)
        self.rainfall_forecaster = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            min_samples_leaf=4,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        self.rainfall_forecaster.fit(X_train[:-1], next_day_rain[: train_end - 1])
        self.rainfall_forecast_metrics = self._evaluate_predictions(
            next_day_rain[train_end:val_end],
            self.rainfall_forecaster.predict(X_val),
            clip_100=False,
        )

        # 2. Flood-Hazard Estimation Candidates
        baseline = Ridge(alpha=1.0, random_state=RANDOM_SEED)
        baseline.fit(X_train, y_train)

        rf_model = RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_leaf=3,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        rf_model.fit(X_train, y_train)

        if HAS_XGBOOST:
            gb_name = "xgboost"
            gb_model = XGBRegressor(
                n_estimators=180,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.85,
                colsample_bytree=0.85,
                random_state=RANDOM_SEED,
                n_jobs=1,
            )
        else:
            gb_name = "gradient_boosting_xgb_equivalent"
            gb_model = GradientBoostingRegressor(
                n_estimators=180,
                max_depth=5,
                learning_rate=0.05,
                subsample=0.85,
                random_state=RANDOM_SEED,
            )
        gb_model.fit(X_train, y_train)

        candidates = {
            "ridge_baseline": baseline,
            "random_forest": rf_model,
            gb_name: gb_model,
        }

        self.candidate_metrics = {}
        best_name = None
        best_val_rmse = float("inf")

        for name, cand in candidates.items():
            val_metrics = self._evaluate_predictions(y_val, cand.predict(X_val))
            test_metrics = self._evaluate_predictions(y_test, cand.predict(X_test))
            self.candidate_metrics[name] = {
                "validation": val_metrics,
                "test": test_metrics,
            }
            if val_metrics["RMSE"] < best_val_rmse:
                best_val_rmse = val_metrics["RMSE"]
                best_name = name

        self.selected_model_name = best_name
        self.model = candidates[best_name]

        val_preds = np.clip(self.model.predict(X_val), 0.0, 100.0)
        self.residual_std = float(np.std(y_val - val_preds))
        self.is_trained = True

        self.save()
        return {
            "hazard": "flood",
            "selected_model": self.selected_model_name,
            "candidate_metrics": self.candidate_metrics,
            "rainfall_forecast_validation_metrics": self.rainfall_forecast_metrics,
            "feature_names": self.feature_names,
            "train_rows": int(len(X_train)),
            "val_rows": int(len(X_val)),
            "test_rows": int(len(X_test)),
        }

    def save(self) -> Path:
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save an untrained FloodRiskModel.")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "rainfall_forecaster": self.rainfall_forecaster,
            "selected_model_name": self.selected_model_name,
            "feature_names": self.feature_names,
            "candidate_metrics": self.candidate_metrics,
            "rainfall_forecast_metrics": self.rainfall_forecast_metrics,
            "training_feature_means": self.training_feature_means,
            "residual_std": self.residual_std,
            "version": MODEL_VERSION,
        }
        joblib.dump(payload, self.model_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "hazard": "flood",
                    "version": MODEL_VERSION,
                    "selected_model_name": self.selected_model_name,
                    "feature_names": self.feature_names,
                    "candidate_metrics": self.candidate_metrics,
                    "rainfall_forecast_metrics": self.rainfall_forecast_metrics,
                    "target_definition": "Hydrometeorological Rainfall-Runoff Flood-Hazard Proxy (0-100).",
                    "scientific_disclaimer": (
                        "High rainfall alone does not equal confirmed street flooding. "
                        "This model estimates hydrometeorological rainfall-runoff hazard proxy "
                        "combining cumulative rainfall, peak intensity, soil saturation, and drainage."
                    ),
                },
                f,
                indent=2,
            )
        return self.model_path

    def load(self) -> "FloodRiskModel":
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained FloodRiskModel artifact not found at '{self.model_path}'. "
                "Please run model training before inference."
            )
        payload = joblib.load(self.model_path)
        self.model = payload["model"]
        self.rainfall_forecaster = payload.get("rainfall_forecaster")
        self.selected_model_name = payload["selected_model_name"]
        self.feature_names = payload["feature_names"]
        self.candidate_metrics = payload.get("candidate_metrics", {})
        self.rainfall_forecast_metrics = payload.get("rainfall_forecast_metrics", {})
        self.training_feature_means = payload.get("training_feature_means", {})
        self.residual_std = payload.get("residual_std", 3.5)
        self.is_trained = True
        return self

    def predict(
        self,
        df_features: pd.DataFrame,
        missing_core_count: int = 0,
        soil_moisture_measured: bool = True,
    ) -> Dict[str, Any]:
        """
        Produce separated rainfall forecast and hydrometeorological flood-hazard estimate (0-100),
        along with contributing factors, data availability, and scientific limitations.
        """
        if not self.is_trained or self.model is None:
            self.load()

        if df_features is None or len(df_features) == 0:
            raise ValueError("FloodRiskModel.predict received empty feature DataFrame.")

        missing_cols = [c for c in self.feature_names if c not in df_features.columns]
        if missing_cols:
            raise ValueError(f"FloodRiskModel missing required features: {missing_cols}")

        row = df_features.iloc[-1]
        X_row = df_features[self.feature_names].iloc[[-1]].to_numpy(dtype=float)

        raw_flood = float(self.model.predict(X_row)[0])
        calibrated_score = round(float(np.clip(raw_flood, 0.0, 100.0)), 2)

        next_day_rain_mm = (
            round(float(max(0.0, self.rainfall_forecaster.predict(X_row)[0])), 2)
            if self.rainfall_forecaster is not None
            else round(float(row["rainfall_mm"]), 2)
        )

        if isinstance(self.model, RandomForestRegressor):
            tree_preds = np.array([est.predict(X_row)[0] for est in self.model.estimators_])
            dispersion = float(np.std(tree_preds))
        else:
            dispersion = self.residual_std

        soil_penalty = 0.0 if soil_moisture_measured else 0.06
        completeness_penalty = min(0.35, 0.08 * missing_core_count) + soil_penalty
        confidence = round(float(np.clip(1.0 - (dispersion / 25.0) - completeness_penalty, 0.40, 0.98)), 2)

        importances = getattr(
            self.model,
            "feature_importances_",
            np.ones(len(self.feature_names)) / len(self.feature_names),
        )
        contributions: List[Tuple[str, float]] = []
        for idx, feat in enumerate(self.feature_names):
            imp = float(importances[idx])
            val = float(row[feat])
            mean_val = self.training_feature_means.get(feat, val)
            rel_dev = abs(val - mean_val) / (abs(mean_val) + 1.0)
            contributions.append((feat, imp * (0.5 + 0.5 * min(rel_dev, 3.0))))

        contributions.sort(key=lambda item: item[1], reverse=True)
        top_factors = [feat for feat, _ in contributions[:4]]

        return {
            "flood_risk": calibrated_score,
            "risk_level": score_to_risk_level(calibrated_score),
            "confidence": confidence,
            "contributing_factors": top_factors,
            "forecast_next_24h_rainfall_mm": next_day_rain_mm,
            "is_proxy_hazard": True,
            "data_availability": {
                "soil_moisture_measured": soil_moisture_measured,
                "elevation_available": True,
                "historical_flood_polygon_labels_available": False,
            },
            "limitations": (
                "High rainfall does not automatically mean flooding. Output is a "
                "hydrometeorological rainfall-runoff flood-hazard proxy; real-time dam "
                "release and street stormwater blockage data are not included."
            ),
            "model_used": self.selected_model_name,
        }

