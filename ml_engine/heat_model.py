"""
ClimateTwin AI — Module 3: Heat-Risk Prediction Model
Module: ml_engine/heat_model.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Objective:
Estimate environmental heat hazard (0-100 scale) using weather observations,
psychrometric interactions (Heat Index, Wet-Bulb temperature), and historical
temperature anomalies.

Scientific Disclaimer:
Predicts meteorological/environmental heat hazard. Does NOT claim medically
validated heat-illness or mortality prediction without clinical ground-truth data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

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
    HEAT_MODEL_DIR,
    MODEL_VERSION,
    RANDOM_SEED,
    score_to_risk_level,
)
from ml_engine.reference_data import compute_heat_hazard_proxy


HEAT_MODEL_FEATURES: List[str] = [
    "temperature_c",
    "temp_max_c",
    "temp_min_c",
    "humidity_pct",
    "wind_speed_kmh",
    "diurnal_temp_range_c",
    "heat_index_c",
    "wet_bulb_temp_c",
    "vapor_pressure_deficit_kpa",
    "temp_anomaly_c",
    "temp_max_anomaly_c",
    "temp_lag_1d",
    "temp_rolling_3d_mean",
    "temp_rolling_7d_mean",
    "temp_max_rolling_3d_mean",
    "sin_day_of_year",
    "cos_day_of_year",
    "is_summer_season",
]


class HeatRiskModel:
    """
    Trains, compares, persists, and serves the Heat-Risk Prediction model.
    Compares Ridge Baseline, Random Forest, and XGBoost (or GradientBoosting fallback),
    selecting the best model on the chronological validation split.
    """

    def __init__(self, model_dir: Optional[Path] = None) -> None:
        self.model_dir: Path = Path(model_dir) if model_dir else HEAT_MODEL_DIR
        self.model_path: Path = self.model_dir / "heat_model.joblib"
        self.meta_path: Path = self.model_dir / "heat_metadata.json"

        self.feature_names: List[str] = list(HEAT_MODEL_FEATURES)
        self.selected_model_name: Optional[str] = None
        self.model: Any = None
        self.candidate_metrics: Dict[str, Dict[str, float]] = {}
        self.training_feature_means: Dict[str, float] = {}
        self.training_target_mean: float = 0.0
        self.residual_std: float = 3.0
        self.is_trained: bool = False

    @staticmethod
    def _evaluate_predictions(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        y_pred_clipped = np.clip(y_pred, 0.0, 100.0)
        mse = float(mean_squared_error(y_true, y_pred_clipped))
        return {
            "MAE": round(float(mean_absolute_error(y_true, y_pred_clipped)), 4),
            "MSE": round(mse, 4),
            "RMSE": round(float(np.sqrt(mse)), 4),
            "R2": round(float(r2_score(y_true, y_pred_clipped)), 4),
        }

    def train_and_select(
        self,
        df_features: pd.DataFrame,
        target_col: str = "heat_risk_target",
        train_frac: float = 0.70,
        val_frac: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Perform chronological split (70% train, 15% validation, 15% test),
        train Baseline, Random Forest, and XGBoost/GradientBoosting, select best
        on validation RMSE, and evaluate on held-out test set.
        """
        df = df_features.copy()
        if target_col not in df.columns:
            df[target_col] = compute_heat_hazard_proxy(df)

        missing_feats = [f for f in self.feature_names if f not in df.columns]
        if missing_feats:
            raise ValueError(f"Missing required heat model features: {missing_feats}")

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
        self.training_target_mean = float(np.mean(y_train))

        # Candidate 1: Linear Ridge Baseline
        baseline = Ridge(alpha=1.0, random_state=RANDOM_SEED)
        baseline.fit(X_train, y_train)

        # Candidate 2: Random Forest Regressor
        rf_model = RandomForestRegressor(
            n_estimators=150,
            max_depth=10,
            min_samples_leaf=3,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        )
        rf_model.fit(X_train, y_train)

        # Candidate 3: XGBoost or GradientBoosting alternative
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
            "hazard": "heat",
            "selected_model": self.selected_model_name,
            "candidate_metrics": self.candidate_metrics,
            "feature_names": self.feature_names,
            "train_rows": int(len(X_train)),
            "val_rows": int(len(X_val)),
            "test_rows": int(len(X_test)),
        }

    def save(self) -> Path:
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save an untrained HeatRiskModel.")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "model": self.model,
            "selected_model_name": self.selected_model_name,
            "feature_names": self.feature_names,
            "candidate_metrics": self.candidate_metrics,
            "training_feature_means": self.training_feature_means,
            "training_target_mean": self.training_target_mean,
            "residual_std": self.residual_std,
            "version": MODEL_VERSION,
        }
        joblib.dump(payload, self.model_path)

        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "hazard": "heat",
                    "version": MODEL_VERSION,
                    "selected_model_name": self.selected_model_name,
                    "feature_names": self.feature_names,
                    "candidate_metrics": self.candidate_metrics,
                    "target_definition": "Meteorological Heat Hazard Proxy (0-100) based on NOAA Heat Index, Wet-Bulb Temperature, and IMD thermal anomalies.",
                    "scientific_disclaimer": "Environmental heat hazard estimate only; not a medically validated heat-illness or mortality forecast.",
                },
                f,
                indent=2,
            )
        return self.model_path

    def load(self) -> "HeatRiskModel":
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained HeatRiskModel artifact not found at '{self.model_path}'. "
                "Please run model training before inference."
            )
        payload = joblib.load(self.model_path)
        self.model = payload["model"]
        self.selected_model_name = payload["selected_model_name"]
        self.feature_names = payload["feature_names"]
        self.candidate_metrics = payload.get("candidate_metrics", {})
        self.training_feature_means = payload.get("training_feature_means", {})
        self.training_target_mean = payload.get("training_target_mean", 0.0)
        self.residual_std = payload.get("residual_std", 3.0)
        self.is_trained = True
        return self

    def predict(
        self,
        df_features: pd.DataFrame,
        missing_core_count: int = 0,
    ) -> Dict[str, Any]:
        """
        Generate calibrated 0-100 heat-risk prediction, risk category,
        confidence estimate, and top contributing features.
        """
        if not self.is_trained or self.model is None:
            self.load()

        if df_features is None or len(df_features) == 0:
            raise ValueError("HeatRiskModel.predict received empty feature DataFrame.")

        missing_cols = [c for c in self.feature_names if c not in df_features.columns]
        if missing_cols:
            raise ValueError(f"HeatRiskModel missing required features: {missing_cols}")

        row = df_features.iloc[-1]
        X_row = df_features[self.feature_names].iloc[[-1]].to_numpy(dtype=float)
        if np.isnan(X_row).any():
            raise ValueError("HeatRiskModel input contains NaN values after preprocessing.")

        raw_pred = float(self.model.predict(X_row)[0])
        calibrated_score = round(float(np.clip(raw_pred, 0.0, 100.0)), 2)

        # Confidence calculation from ensemble agreement and input completeness
        if hasattr(self.model, "estimators_"):
            # RandomForest or GradientBoosting ensemble dispersion
            if isinstance(self.model, RandomForestRegressor):
                tree_preds = np.array([est.predict(X_row)[0] for est in self.model.estimators_])
                dispersion = float(np.std(tree_preds))
            else:
                dispersion = self.residual_std
        else:
            dispersion = self.residual_std

        completeness_penalty = min(0.35, 0.08 * missing_core_count)
        confidence = round(float(np.clip(1.0 - (dispersion / 25.0) - completeness_penalty, 0.40, 0.98)), 2)

        # Top contributing factors using feature importance weighted by standardized deviation
        importances = getattr(self.model, "feature_importances_", np.ones(len(self.feature_names)) / len(self.feature_names))
        contributions: List[Tuple[str, float]] = []
        for idx, feat in enumerate(self.feature_names):
            imp = float(importances[idx])
            val = float(row[feat])
            mean_val = self.training_feature_means.get(feat, val)
            rel_dev = abs(val - mean_val) / (abs(mean_val) + 1.0)
            score_contrib = imp * (0.5 + 0.5 * min(rel_dev, 3.0))
            contributions.append((feat, score_contrib))

        contributions.sort(key=lambda item: item[1], reverse=True)
        top_factors = [feat for feat, _ in contributions[:4]]

        return {
            "heat_risk": calibrated_score,
            "risk_level": score_to_risk_level(calibrated_score),
            "confidence": confidence,
            "contributing_factors": top_factors,
            "model_used": self.selected_model_name,
            "methodology_note": "Meteorological heat-hazard proxy (0-100) calibrated on NOAA Heat Index, Wet-Bulb temperature, and IMD thermal anomalies.",
        }

