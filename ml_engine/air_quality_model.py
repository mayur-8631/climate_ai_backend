"""
ClimateTwin AI — Module 5: Air-Quality Risk Prediction Model
Module: ml_engine/air_quality_model.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Objective:
Estimate atmospheric air-quality hazard (0-100 scale) calibrated against official
Indian Central Pollution Control Board (CPCB) National Air Quality Index (NAQI)
standards across PM2.5, PM10, NO2, SO2, CO, and O3, combined with meteorological
dispersion conditions.

Scientific Rule:
Clearly distinguishes source-supplied `measured_aqi` from the ML-predicted
`air_quality_risk` hazard score and identifies the dominant pollutants driving
the CPCB sub-index.
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
    AIR_QUALITY_MODEL_DIR,
    CPCB_AQI_BREAKPOINTS,
    MODEL_VERSION,
    RANDOM_SEED,
    score_to_risk_level,
)
from ml_engine.feature_engineering import compute_cpcb_sub_index
from ml_engine.reference_data import compute_air_quality_hazard_proxy


AIR_QUALITY_MODEL_FEATURES: List[str] = [
    "pm25_ugm3",
    "pm10_ugm3",
    "no2_ugm3",
    "so2_ugm3",
    "co_mgm3",
    "o3_ugm3",
    "pm_ratio_25_to_10",
    "pm25_lag_1d",
    "pm25_rolling_3d_mean",
    "temperature_c",
    "humidity_pct",
    "wind_speed_kmh",
    "wind_stagnation_index",
    "cpcb_calculated_aqi",
    "pollutant_load_index",
    "is_winter_inversion",
    "is_monsoon_season",
]

POLLUTANT_DISPLAY_NAMES: Dict[str, str] = {
    "pm25_ugm3": "PM2.5",
    "pm10_ugm3": "PM10",
    "no2_ugm3": "NO2",
    "so2_ugm3": "SO2",
    "co_mgm3": "CO",
    "o3_ugm3": "O3",
}


class AirQualityRiskModel:
    """
    Trains, evaluates, persists, and serves the Air-Quality Risk Prediction model.
    Uses official Indian CPCB NAQI sub-indices and meteorological dispersion features.
    """

    def __init__(self, model_dir: Optional[Path] = None) -> None:
        self.model_dir: Path = Path(model_dir) if model_dir else AIR_QUALITY_MODEL_DIR
        self.model_path: Path = self.model_dir / "air_quality_model.joblib"
        self.meta_path: Path = self.model_dir / "air_quality_metadata.json"

        self.feature_names: List[str] = list(AIR_QUALITY_MODEL_FEATURES)
        self.selected_model_name: Optional[str] = None
        self.model: Any = None
        self.candidate_metrics: Dict[str, Dict[str, float]] = {}
        self.training_feature_means: Dict[str, float] = {}
        self.residual_std: float = 2.5
        self.is_trained: bool = False

    @staticmethod
    def _evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        preds = np.clip(y_pred, 0.0, 100.0)
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
        target_col: str = "air_quality_risk_target",
        train_frac: float = 0.70,
        val_frac: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Perform chronological split, train Ridge Baseline, Random Forest, and
        XGBoost/GradientBoosting, compare on validation set, and evaluate on test set.
        """
        df = df_features.copy()
        if target_col not in df.columns:
            df[target_col] = compute_air_quality_hazard_proxy(df)

        missing_feats = [f for f in self.feature_names if f not in df.columns]
        if missing_feats:
            raise ValueError(f"Missing required air-quality model features: {missing_feats}")

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
            "hazard": "air_quality",
            "selected_model": self.selected_model_name,
            "candidate_metrics": self.candidate_metrics,
            "feature_names": self.feature_names,
            "train_rows": int(len(X_train)),
            "val_rows": int(len(X_val)),
            "test_rows": int(len(X_test)),
        }

    def save(self) -> Path:
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save an untrained AirQualityRiskModel.")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "selected_model_name": self.selected_model_name,
            "feature_names": self.feature_names,
            "candidate_metrics": self.candidate_metrics,
            "training_feature_means": self.training_feature_means,
            "residual_std": self.residual_std,
            "version": MODEL_VERSION,
        }
        joblib.dump(payload, self.model_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "hazard": "air_quality",
                    "version": MODEL_VERSION,
                    "selected_model_name": self.selected_model_name,
                    "feature_names": self.feature_names,
                    "candidate_metrics": self.candidate_metrics,
                    "aqi_standard": "Central Pollution Control Board (CPCB) India National Air Quality Index (NAQI)",
                    "target_definition": "0-100 Air Quality Hazard Score calibrated to CPCB NAQI sub-indices and dispersion stagnation.",
                },
                f,
                indent=2,
            )
        return self.model_path

    def load(self) -> "AirQualityRiskModel":
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained AirQualityRiskModel artifact not found at '{self.model_path}'. "
                "Please run model training before inference."
            )
        payload = joblib.load(self.model_path)
        self.model = payload["model"]
        self.selected_model_name = payload["selected_model_name"]
        self.feature_names = payload["feature_names"]
        self.candidate_metrics = payload.get("candidate_metrics", {})
        self.training_feature_means = payload.get("training_feature_means", {})
        self.residual_std = payload.get("residual_std", 2.5)
        self.is_trained = True
        return self

    def predict(
        self,
        df_features: pd.DataFrame,
        missing_pollutant_count: int = 0,
        measured_aqi_supplied: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Estimate 0-100 air-quality risk score, identify dominant pollutants by CPCB
        sub-index, and explicitly distinguish measured AQI from predicted hazard.
        """
        if not self.is_trained or self.model is None:
            self.load()

        if df_features is None or len(df_features) == 0:
            raise ValueError("AirQualityRiskModel.predict received empty feature DataFrame.")

        missing_cols = [c for c in self.feature_names if c not in df_features.columns]
        if missing_cols:
            raise ValueError(f"AirQualityRiskModel missing required features: {missing_cols}")

        row = df_features.iloc[-1]
        X_row = df_features[self.feature_names].iloc[[-1]].to_numpy(dtype=float)

        raw_pred = float(self.model.predict(X_row)[0])
        calibrated_score = round(float(np.clip(raw_pred, 0.0, 100.0)), 2)

        # Rank dominant pollutants by their CPCB sub-index
        pollutant_sub_indices: List[Tuple[str, float]] = []
        for pol_col, bp_list in CPCB_AQI_BREAKPOINTS.items():
            if pol_col in row:
                sub_idx = compute_cpcb_sub_index(float(row[pol_col]), bp_list)
                if not np.isnan(sub_idx):
                    pollutant_sub_indices.append((POLLUTANT_DISPLAY_NAMES[pol_col], float(sub_idx)))

        pollutant_sub_indices.sort(key=lambda item: item[1], reverse=True)
        dominant_pollutants = [name for name, _ in pollutant_sub_indices[:3]]

        if isinstance(self.model, RandomForestRegressor):
            tree_preds = np.array([est.predict(X_row)[0] for est in self.model.estimators_])
            dispersion = float(np.std(tree_preds))
        else:
            dispersion = self.residual_std

        pol_penalty = min(0.40, 0.06 * missing_pollutant_count)
        confidence = round(float(np.clip(1.0 - (dispersion / 25.0) - pol_penalty, 0.35, 0.98)), 2)

        cpcb_aqi_est = round(float(row["cpcb_calculated_aqi"]), 1)

        return {
            "air_quality_risk": calibrated_score,
            "risk_level": score_to_risk_level(calibrated_score),
            "confidence": confidence,
            "dominant_pollutants": dominant_pollutants,
            "cpcb_calculated_aqi": cpcb_aqi_est,
            "source_measured_aqi": (
                round(float(measured_aqi_supplied), 1)
                if measured_aqi_supplied is not None and not pd.isna(measured_aqi_supplied)
                else None
            ),
            "aqi_source_distinction": (
                "source_measured_aqi_and_ml_hazard_both_available"
                if measured_aqi_supplied is not None and not pd.isna(measured_aqi_supplied)
                else "ml_hazard_and_cpcb_subindex_calculated_from_pollutants"
            ),
            "model_used": self.selected_model_name,
        }

