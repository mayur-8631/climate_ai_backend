"""
ClimateTwin AI — Module 6: Water-Stress Analysis Model
Module: ml_engine/water_stress_model.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Objective:
Estimate environmental hydro-climatic water-stress conditions (0-100 scale)
using cumulative rainfall history, temperature, relative humidity, root-zone
soil moisture, reference evapotranspiration, and cumulative water-balance deficits.

Scientific Distinction:
Estimates *environmental/climatic water stress* (moisture deficit and evaporative
demand). Does NOT claim knowledge of municipal reservoir storage, dam levels,
groundwater table depth, or piped water supply shortage unless explicitly measured.
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
    MODEL_VERSION,
    RANDOM_SEED,
    WATER_STRESS_MODEL_DIR,
    score_to_risk_level,
)
from ml_engine.reference_data import compute_water_stress_hazard_proxy


WATER_STRESS_MODEL_FEATURES: List[str] = [
    "rainfall_mm",
    "rainfall_rolling_7d_sum",
    "rainfall_rolling_14d_sum",
    "rainfall_rolling_30d_sum",
    "temperature_c",
    "temp_max_c",
    "humidity_pct",
    "vapor_pressure_deficit_kpa",
    "soil_moisture",
    "soil_moisture_lag_1d",
    "soil_moisture_rolling_7d_mean",
    "evapotranspiration_mm",
    "evap_rolling_7d_sum",
    "evap_rolling_30d_sum",
    "hydro_water_deficit_7d_mm",
    "hydro_water_deficit_30d_mm",
    "aridity_stress_index",
    "is_summer_season",
    "is_monsoon_season",
]


class WaterStressModel:
    """
    Trains, evaluates, persists, and serves the Environmental Water-Stress model.
    Compares Ridge Baseline, Random Forest, and XGBoost/GradientBoosting.
    """

    def __init__(self, model_dir: Optional[Path] = None) -> None:
        self.model_dir: Path = Path(model_dir) if model_dir else WATER_STRESS_MODEL_DIR
        self.model_path: Path = self.model_dir / "water_stress_model.joblib"
        self.meta_path: Path = self.model_dir / "water_stress_metadata.json"

        self.feature_names: List[str] = list(WATER_STRESS_MODEL_FEATURES)
        self.selected_model_name: Optional[str] = None
        self.model: Any = None
        self.candidate_metrics: Dict[str, Dict[str, float]] = {}
        self.training_feature_means: Dict[str, float] = {}
        self.residual_std: float = 2.8
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
        target_col: str = "water_stress_risk_target",
        train_frac: float = 0.70,
        val_frac: float = 0.15,
    ) -> Dict[str, Any]:
        """
        Perform chronological split, train Ridge Baseline, Random Forest, and
        XGBoost/GradientBoosting, compare on validation set, and evaluate on test set.
        """
        df = df_features.copy()
        if target_col not in df.columns:
            df[target_col] = compute_water_stress_hazard_proxy(df)

        missing_feats = [f for f in self.feature_names if f not in df.columns]
        if missing_feats:
            raise ValueError(f"Missing required water-stress model features: {missing_feats}")

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
            "hazard": "water_stress",
            "selected_model": self.selected_model_name,
            "candidate_metrics": self.candidate_metrics,
            "feature_names": self.feature_names,
            "train_rows": int(len(X_train)),
            "val_rows": int(len(X_val)),
            "test_rows": int(len(X_test)),
        }

    def save(self) -> Path:
        if not self.is_trained or self.model is None:
            raise RuntimeError("Cannot save an untrained WaterStressModel.")
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
                    "hazard": "water_stress",
                    "version": MODEL_VERSION,
                    "selected_model_name": self.selected_model_name,
                    "feature_names": self.feature_names,
                    "candidate_metrics": self.candidate_metrics,
                    "target_definition": "Environmental Hydro-Climatic Water-Stress Proxy (0-100) based on 30d ET-rainfall deficit and soil moisture depletion.",
                    "scientific_disclaimer": (
                        "Measures environmental moisture stress; does not measure municipal "
                        "reservoir storage, groundwater depth, or piped water supply shortage."
                    ),
                },
                f,
                indent=2,
            )
        return self.model_path

    def load(self) -> "WaterStressModel":
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Trained WaterStressModel artifact not found at '{self.model_path}'. "
                "Please run model training before inference."
            )
        payload = joblib.load(self.model_path)
        self.model = payload["model"]
        self.selected_model_name = payload["selected_model_name"]
        self.feature_names = payload["feature_names"]
        self.candidate_metrics = payload.get("candidate_metrics", {})
        self.training_feature_means = payload.get("training_feature_means", {})
        self.residual_std = payload.get("residual_std", 2.8)
        self.is_trained = True
        return self

    def predict(
        self,
        df_features: pd.DataFrame,
        soil_moisture_measured: bool = True,
        evapotranspiration_measured: bool = True,
    ) -> Dict[str, Any]:
        """
        Estimate environmental water-stress conditions (0-100), identify influential
        factors, and report when direct land-surface variables were unavailable.
        """
        if not self.is_trained or self.model is None:
            self.load()

        if df_features is None or len(df_features) == 0:
            raise ValueError("WaterStressModel.predict received empty feature DataFrame.")

        missing_cols = [c for c in self.feature_names if c not in df_features.columns]
        if missing_cols:
            raise ValueError(f"WaterStressModel missing required features: {missing_cols}")

        row = df_features.iloc[-1]
        X_row = df_features[self.feature_names].iloc[[-1]].to_numpy(dtype=float)

        raw_pred = float(self.model.predict(X_row)[0])
        calibrated_score = round(float(np.clip(raw_pred, 0.0, 100.0)), 2)

        if isinstance(self.model, RandomForestRegressor):
            tree_preds = np.array([est.predict(X_row)[0] for est in self.model.estimators_])
            dispersion = float(np.std(tree_preds))
        else:
            dispersion = self.residual_std

        unmeasured_penalty = (0.08 if not soil_moisture_measured else 0.0) + (
            0.05 if not evapotranspiration_measured else 0.0
        )
        confidence = round(float(np.clip(1.0 - (dispersion / 25.0) - unmeasured_penalty, 0.35, 0.98)), 2)

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

        missing_notes: List[str] = []
        if not soil_moisture_measured:
            missing_notes.append("Direct soil_moisture measurement unavailable; estimated via antecedent precipitation-humidity proxy.")
        if not evapotranspiration_measured:
            missing_notes.append("Direct evapotranspiration_mm unavailable; estimated via Hargreaves temperature-radiation formula.")

        return {
            "water_stress_risk": calibrated_score,
            "risk_level": score_to_risk_level(calibrated_score),
            "confidence": confidence,
            "contributing_factors": top_factors,
            "data_status_notes": missing_notes if missing_notes else ["All primary hydro-climatic inputs available."],
            "scope_disclaimer": (
                "Represents environmental/climatic water stress only. Municipal reservoir levels, "
                "groundwater depth, and piped water supply are not measured."
            ),
            "model_used": self.selected_model_name,
        }

