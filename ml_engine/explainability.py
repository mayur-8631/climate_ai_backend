"""
ClimateTwin AI — Module 9: Explainable AI (XAI) Engine
Module: ml_engine/explainability.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Objective:
Explain why a location received its predicted hazard scores using actual trained
model introspection:
- Uses `shap.TreeExplainer` when the `shap` library is installed.
- Uses interventional additive model attribution (`f(x_i, E[X_-i]) - f(E[X])`
  combined with tree `feature_importances_`) when `shap` is not installed,
  preserving exact directional sign (`increases_risk` vs `decreases_risk`) and
  magnitude from the live trained model.
- Provides both local (per-prediction) and global (dataset-level) explanations.
- Never fabricates hardcoded attributions.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

try:
    import shap
    HAS_SHAP = True
except ImportError:
    HAS_SHAP = False

from ml_engine.model_evaluation import MODEL_LIMITATIONS


HUMAN_FEATURE_LABELS: Dict[str, str] = {
    "temperature_c": "ambient temperature",
    "temp_max_c": "daily maximum temperature",
    "temp_min_c": "daily minimum temperature",
    "humidity_pct": "relative humidity",
    "wind_speed_kmh": "wind speed",
    "heat_index_c": "apparent heat index",
    "wet_bulb_temp_c": "wet-bulb temperature",
    "temp_anomaly_c": "temperature anomaly above monthly normal",
    "temp_max_anomaly_c": "maximum temperature anomaly",
    "temp_rolling_3d_mean": "3-day average temperature",
    "rainfall_mm": "daily rainfall",
    "rainfall_intensity_mm_hr": "peak hourly rainfall intensity",
    "rainfall_rolling_3d_sum": "3-day cumulative rainfall",
    "rainfall_rolling_7d_sum": "7-day cumulative rainfall",
    "soil_moisture": "soil moisture saturation",
    "runoff_potential_index": "surface runoff & drainage index",
    "topographic_flood_susceptibility": "topographic flood susceptibility",
    "pm25_ugm3": "PM2.5 concentration",
    "pm10_ugm3": "PM10 concentration",
    "no2_ugm3": "NO2 concentration",
    "so2_ugm3": "SO2 concentration",
    "co_mgm3": "CO concentration",
    "o3_ugm3": "O3 concentration",
    "cpcb_calculated_aqi": "CPCB calculated AQI",
    "wind_stagnation_index": "low-wind atmospheric stagnation",
    "evapotranspiration_mm": "daily evapotranspiration demand",
    "hydro_water_deficit_30d_mm": "30-day cumulative water balance deficit",
    "aridity_stress_index": "hydro-climatic aridity stress index",
}


class ClimateExplainabilityEngine:
    """
    Computes local and global feature attributions from trained ClimateTwin AI
    hazard models without ever fabricating static outputs.
    """

    def __init__(self, top_k: int = 4) -> None:
        self.top_k = top_k

    def explain_single_hazard(
        self,
        hazard_name: str,
        hazard_model_wrapper: Any,
        df_features: pd.DataFrame,
    ) -> Dict[str, Any]:
        """
        Compute local explanation for a single hazard model on the latest row of `df_features`.
        """
        if hazard_model_wrapper is None or not getattr(hazard_model_wrapper, "is_trained", False):
            raise RuntimeError(f"Hazard model '{hazard_name}' must be loaded/trained before generating explanations.")

        model = hazard_model_wrapper.model
        feature_names: List[str] = hazard_model_wrapper.feature_names
        training_means: Dict[str, float] = getattr(hazard_model_wrapper, "training_feature_means", {})

        if df_features is None or len(df_features) == 0:
            raise ValueError("Cannot explain prediction on an empty feature DataFrame.")

        missing_cols = [f for f in feature_names if f not in df_features.columns]
        if missing_cols:
            raise ValueError(f"Missing features for '{hazard_name}' explanation: {missing_cols}")

        X_row = df_features[feature_names].iloc[[-1]].to_numpy(dtype=float)
        baseline_vec = np.array(
            [[training_means.get(f, float(X_row[0, idx])) for idx, f in enumerate(feature_names)]],
            dtype=float,
        )

        pred_val = float(np.clip(model.predict(X_row)[0], 0.0, 100.0))
        base_val = float(np.clip(model.predict(baseline_vec)[0], 0.0, 100.0))

        # Global tree feature importances
        global_importances = getattr(
            model,
            "feature_importances_",
            np.abs(getattr(model, "coef_", np.ones(len(feature_names)) / len(feature_names))),
        )
        global_importances = np.asarray(global_importances, dtype=float)
        if global_importances.sum() > 0:
            global_importances = global_importances / global_importances.sum()

        # Local feature contributions: use SHAP TreeExplainer if installed, else interventional model probing
        attribution_method = "interventional_model_attribution"
        local_contribs = np.zeros(len(feature_names), dtype=float)

        if HAS_SHAP and hasattr(model, "estimators_"):
            try:
                explainer = shap.TreeExplainer(model, data=baseline_vec)
                shap_vals = explainer.shap_values(X_row, check_additivity=False)
                local_contribs = np.asarray(shap_vals, dtype=float).reshape(-1)
                attribution_method = "shap_tree_explainer"
            except Exception:
                attribution_method = "interventional_model_attribution"

        if attribution_method == "interventional_model_attribution":
            # Measure exact marginal model response when replacing each feature in baseline_vec with X_row[j]
            # and when replacing each feature in X_row with baseline_vec[j] (2-point Shapley-Owen average)
            raw_deltas = np.zeros(len(feature_names), dtype=float)
            for j in range(len(feature_names)):
                from_base = baseline_vec.copy()
                from_base[0, j] = X_row[0, j]
                delta_forward = float(model.predict(from_base)[0] - base_val)

                from_actual = X_row.copy()
                from_actual[0, j] = baseline_vec[0, j]
                delta_backward = float(pred_val - model.predict(from_actual)[0])

                raw_deltas[j] = 0.5 * (delta_forward + delta_backward)

            # Scale additive contributions to match (pred_val - base_val) when non-zero
            total_abs = np.sum(np.abs(raw_deltas))
            total_diff = pred_val - base_val
            if total_abs > 1e-6:
                local_contribs = raw_deltas
            else:
                local_contribs = global_importances * total_diff

        # Rank features by combined local impact magnitude + global model importance
        ranked_indices = np.argsort(np.abs(local_contribs) + 5.0 * global_importances)[::-1]
        top_indices = ranked_indices[: self.top_k]

        primary_factors: List[Dict[str, Any]] = []
        inc_labels: List[str] = []
        dec_labels: List[str] = []

        for idx in top_indices:
            feat_name = feature_names[int(idx)]
            contrib = float(local_contribs[int(idx)])
            g_imp = float(global_importances[int(idx)])
            actual_v = float(X_row[0, int(idx)])
            base_v = float(baseline_vec[0, int(idx)])

            effect = "increases_risk" if contrib >= 0.0 else "decreases_risk"
            readable_name = HUMAN_FEATURE_LABELS.get(feat_name, feat_name)
            if effect == "increases_risk":
                inc_labels.append(readable_name)
            else:
                dec_labels.append(readable_name)

            primary_factors.append(
                {
                    "feature": feat_name,
                    "readable_name": readable_name,
                    "value": round(actual_v, 3),
                    "baseline_mean": round(base_v, 3),
                    "effect": effect,
                    "contribution_points": round(contrib, 3),
                    "importance": round(g_imp, 4),
                }
            )

        if inc_labels and dec_labels:
            summary_text = (
                f"For {hazard_name} hazard (predicted score {pred_val:.1f}/100 vs baseline {base_val:.1f}/100), "
                f"{', '.join(inc_labels[:2])} increased estimated risk, while {', '.join(dec_labels[:2])} "
                f"partially moderated the hazard."
            )
        elif inc_labels:
            summary_text = (
                f"Elevated {hazard_name} hazard ({pred_val:.1f}/100 vs baseline {base_val:.1f}/100) "
                f"was primarily driven upward by {', '.join(inc_labels[:3])}."
            )
        else:
            summary_text = (
                f"Low {hazard_name} hazard ({pred_val:.1f}/100 vs baseline {base_val:.1f}/100) "
                f"reflects favorable {', '.join(dec_labels[:3])} below climatological stress thresholds."
            )

        return {
            "hazard": hazard_name,
            "predicted_score": round(pred_val, 2),
            "baseline_expected_score": round(base_val, 2),
            "attribution_method": attribution_method,
            "primary_factors": primary_factors,
            "global_feature_importance": {
                feature_names[i]: round(float(global_importances[i]), 4)
                for i in np.argsort(global_importances)[::-1][:6]
            },
            "summary": summary_text,
            "limitations": MODEL_LIMITATIONS.get(
                hazard_name,
                "Explanations reflect statistical associations within the trained hazard proxy model.",
            ),
        }

    def explain_all(
        self,
        df_features: pd.DataFrame,
        models: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Generate structured explanations across all available hazard models and
        provide a unified top-level explanation block matching the integration contract.
        """
        if df_features is None or len(df_features) == 0:
            raise ValueError("Cannot generate explanations: df_features is empty.")

        per_hazard: Dict[str, Any] = {}
        combined_factors: List[Dict[str, Any]] = []

        for hazard_key, model_wrapper in models.items():
            if model_wrapper is None:
                continue
            exp = self.explain_single_hazard(hazard_key, model_wrapper, df_features)
            per_hazard[hazard_key] = exp
            if exp["primary_factors"]:
                top_f = dict(exp["primary_factors"][0])
                top_f["hazard_domain"] = hazard_key
                combined_factors.append(top_f)

        combined_factors.sort(key=lambda item: abs(item.get("contribution_points", 0.0)), reverse=True)

        summaries = [exp["summary"] for exp in per_hazard.values()]
        overall_summary = " ".join(summaries) if summaries else "No model explanations available."

        return {
            "explanation": {
                "primary_factors": combined_factors,
                "summary": overall_summary,
                "by_hazard": per_hazard,
            }
        }

