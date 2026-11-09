"""
ClimateTwin AI — Module 11: Central FastAPI Backend Integration Entry Point
Module: ml_engine/predict.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026
Backend Integration Partner: Mayuresh Kamble
Frontend Integration Partner: Pravin Kamble

Responsibilities:
- Provide a clean, stateless-to-caller, JSON-serializable inference API for FastAPI.
- Keep model loading strictly separated from model training (models are loaded from
  persisted artifacts in `models/` and `datasets/processed/preprocessor.joblib`).
- Expose all 9 required contract functions:
  1. `preprocess_environmental_data(data)`
  2. `predict_heat_risk(data)`
  3. `predict_flood_risk(data)`
  4. `predict_air_quality_risk(data)`
  5. `predict_water_stress(data)`
  6. `calculate_climate_risk_score(predictions)`
  7. `explain_prediction(data, predictions)`
  8. `run_what_if_scenario(data, scenario)`
  9. `generate_complete_prediction(data)`
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd

from ml_engine.air_quality_model import AirQualityRiskModel
from ml_engine.config import PROCESSED_DATA_DIR
from ml_engine.data_preprocessing import EnvironmentalDataPreprocessor
from ml_engine.explainability import ClimateExplainabilityEngine
from ml_engine.feature_engineering import EnvironmentalFeatureEngineer
from ml_engine.flood_model import FloodRiskModel
from ml_engine.heat_model import HeatRiskModel
from ml_engine.risk_score import ClimateRiskScoreEngine
from ml_engine.water_stress_model import WaterStressModel
from ml_engine.what_if import WhatIfSimulationEngine


def _to_json_compatible(obj: Any) -> Any:
    """Recursively convert NumPy/Pandas scalars and containers to native Python JSON types."""
    if isinstance(obj, dict):
        return {str(k): _to_json_compatible(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_json_compatible(v) for v in obj]
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.floating, float)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, pd.Timestamp):
        return obj.strftime("%Y-%m-%dT%H:%M:%S")
    if isinstance(obj, np.ndarray):
        return _to_json_compatible(obj.tolist())
    return obj


class _InferenceBundle:
    """
    Lazy singleton loader for fitted preprocessor and trained hazard models.
    Ensures models are loaded once into memory for fast FastAPI request handling,
    and never re-trains on incoming inference requests.
    """

    def __init__(self) -> None:
        self.preprocessor: Optional[EnvironmentalDataPreprocessor] = None
        self.feature_engineer: EnvironmentalFeatureEngineer = EnvironmentalFeatureEngineer()
        self.heat_model: Optional[HeatRiskModel] = None
        self.flood_model: Optional[FloodRiskModel] = None
        self.air_quality_model: Optional[AirQualityRiskModel] = None
        self.water_stress_model: Optional[WaterStressModel] = None
        self.risk_engine: ClimateRiskScoreEngine = ClimateRiskScoreEngine()
        self.explainer: ClimateExplainabilityEngine = ClimateExplainabilityEngine()

    def ensure_loaded(self) -> None:
        if self.preprocessor is None:
            self.preprocessor = EnvironmentalDataPreprocessor.load(
                PROCESSED_DATA_DIR / "preprocessor.joblib"
            )
        if self.heat_model is None:
            self.heat_model = HeatRiskModel().load()
        if self.flood_model is None:
            self.flood_model = FloodRiskModel().load()
        if self.air_quality_model is None:
            self.air_quality_model = AirQualityRiskModel().load()
        if self.water_stress_model is None:
            self.water_stress_model = WaterStressModel().load()

    def reload(self) -> None:
        """Force reload of all persisted artifacts (useful after retraining in tests)."""
        self.preprocessor = None
        self.heat_model = None
        self.flood_model = None
        self.air_quality_model = None
        self.water_stress_model = None
        self.ensure_loaded()


_BUNDLE = _InferenceBundle()


def reload_inference_models() -> None:
    """Reload trained models and preprocessor from disk."""
    _BUNDLE.reload()


# ============================================================================
# REQUIRED BACKEND INTEGRATION FUNCTIONS
# ============================================================================

def preprocess_environmental_data(
    data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
    return_metadata: bool = False,
) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict[str, Any]]]:
    """
    Validate, clean, impute, and engineer environmental features using the
    pre-fitted training preprocessor.
    """
    if data is None or (isinstance(data, (dict, list, pd.DataFrame)) and len(data) == 0):
        raise ValueError("Environmental input data cannot be None or empty.")

    _BUNDLE.ensure_loaded()
    assert _BUNDLE.preprocessor is not None

    # Standardize aliases first to inspect raw provided columns
    raw_df = _BUNDLE.preprocessor._to_dataframe(data)
    std_df, _ = _BUNDLE.preprocessor.standardize_units_and_columns(raw_df)

    # Check if at least one environmental measurement is present
    env_cols = [
        c for c in std_df.columns
        if c not in ("location", "timestamp", "latitude", "longitude", "elevation_m", "slope_deg", "drainage_index")
    ]
    if not env_cols or std_df[env_cols].isna().all(axis=None):
        raise ValueError(
            "Insufficient environmental data: payload contains no valid weather, rainfall, "
            "air-quality, or water-stress measurements."
        )

    soil_measured = "soil_moisture" in std_df.columns and bool(std_df["soil_moisture"].notna().any())
    et_measured = "evapotranspiration_mm" in std_df.columns and bool(std_df["evapotranspiration_mm"].notna().any())
    measured_aqi_val = (
        float(std_df["measured_aqi"].dropna().iloc[-1])
        if ("measured_aqi" in std_df.columns and std_df["measured_aqi"].notna().any())
        else None
    )

    clean_df, prep_report = _BUNDLE.preprocessor.transform(raw_df, return_report=True)
    feat_df, feat_report = _BUNDLE.feature_engineer.transform(clean_df, return_report=True)

    meta = {
        "preprocessing_report": prep_report,
        "feature_report": feat_report,
        "soil_moisture_measured": soil_measured,
        "evapotranspiration_measured": et_measured,
        "measured_aqi_supplied": measured_aqi_val,
    }
    if return_metadata:
        return feat_df, meta
    return feat_df


def predict_heat_risk(data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Generate heat-risk prediction (0-100) from raw or preprocessed environmental data."""
    _BUNDLE.ensure_loaded()
    assert _BUNDLE.heat_model is not None

    if isinstance(data, pd.DataFrame) and set(_BUNDLE.heat_model.feature_names).issubset(data.columns):
        feat_df = data
        missing_cnt = 0
    else:
        feat_df, meta = preprocess_environmental_data(data, return_metadata=True)
        missing_map = meta["preprocessing_report"].get("missing_counts_before_imputation", {})
        missing_cnt = sum(1 for k in ["temperature_c", "humidity_pct", "wind_speed_kmh"] if missing_map.get(k, 1) > 0)

    return _to_json_compatible(_BUNDLE.heat_model.predict(feat_df, missing_core_count=missing_cnt))


def predict_flood_risk(data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Generate rainfall & flood-hazard prediction (0-100) from raw or preprocessed data."""
    _BUNDLE.ensure_loaded()
    assert _BUNDLE.flood_model is not None

    if isinstance(data, pd.DataFrame) and set(_BUNDLE.flood_model.feature_names).issubset(data.columns):
        feat_df = data
        missing_cnt = 0
        soil_measured = True
    else:
        feat_df, meta = preprocess_environmental_data(data, return_metadata=True)
        missing_map = meta["preprocessing_report"].get("missing_counts_before_imputation", {})
        missing_cnt = sum(1 for k in ["rainfall_mm", "humidity_pct"] if missing_map.get(k, 1) > 0)
        soil_measured = bool(meta["soil_moisture_measured"])

    return _to_json_compatible(
        _BUNDLE.flood_model.predict(
            feat_df,
            missing_core_count=missing_cnt,
            soil_moisture_measured=soil_measured,
        )
    )


def predict_air_quality_risk(data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Generate air-quality hazard prediction (0-100) from raw or preprocessed data."""
    _BUNDLE.ensure_loaded()
    assert _BUNDLE.air_quality_model is not None

    if isinstance(data, pd.DataFrame) and set(_BUNDLE.air_quality_model.feature_names).issubset(data.columns):
        feat_df = data
        missing_pol = 0
        measured_aqi = None
    else:
        feat_df, meta = preprocess_environmental_data(data, return_metadata=True)
        missing_map = meta["preprocessing_report"].get("missing_counts_before_imputation", {})
        pol_cols = ["pm25_ugm3", "pm10_ugm3", "no2_ugm3", "so2_ugm3", "co_mgm3", "o3_ugm3"]
        missing_pol = sum(1 for k in pol_cols if missing_map.get(k, 1) > 0)
        measured_aqi = meta["measured_aqi_supplied"]

    return _to_json_compatible(
        _BUNDLE.air_quality_model.predict(
            feat_df,
            missing_pollutant_count=missing_pol,
            measured_aqi_supplied=measured_aqi,
        )
    )


def predict_water_stress(data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Generate environmental water-stress prediction (0-100) from raw or preprocessed data."""
    _BUNDLE.ensure_loaded()
    assert _BUNDLE.water_stress_model is not None

    if isinstance(data, pd.DataFrame) and set(_BUNDLE.water_stress_model.feature_names).issubset(data.columns):
        feat_df = data
        soil_measured = True
        et_measured = True
    else:
        feat_df, meta = preprocess_environmental_data(data, return_metadata=True)
        soil_measured = bool(meta["soil_moisture_measured"])
        et_measured = bool(meta["evapotranspiration_measured"])

    return _to_json_compatible(
        _BUNDLE.water_stress_model.predict(
            feat_df,
            soil_moisture_measured=soil_measured,
            evapotranspiration_measured=et_measured,
        )
    )


def calculate_climate_risk_score(
    predictions: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """Combine hazard-specific predictions into a localized Climate Risk Score (0-100)."""
    return _to_json_compatible(_BUNDLE.risk_engine.calculate(predictions, custom_weights=weights))


def explain_prediction(
    data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
    predictions: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Generate SHAP / model-based feature attributions for all hazard predictions."""
    _BUNDLE.ensure_loaded()
    if isinstance(data, pd.DataFrame) and "aridity_stress_index" in data.columns:
        feat_df = data
    else:
        feat_df = preprocess_environmental_data(data)

    models_dict = {
        "heat": _BUNDLE.heat_model,
        "flood": _BUNDLE.flood_model,
        "air_quality": _BUNDLE.air_quality_model,
        "water_stress": _BUNDLE.water_stress_model,
    }
    exp_out = _BUNDLE.explainer.explain_all(feat_df, models_dict)
    return _to_json_compatible(exp_out)


def run_what_if_scenario(
    data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
    scenario: Dict[str, Any],
) -> Dict[str, Any]:
    """Run a counterfactual What-If climate simulation without mutating original input."""
    sim_engine = WhatIfSimulationEngine(
        prediction_fn=lambda d: generate_complete_prediction(d, include_explainability=False)
    )
    return _to_json_compatible(sim_engine.simulate(data, scenario))


def _generate_stakeholder_recommendations(risks: Dict[str, float], composite_score: float) -> List[Dict[str, str]]:
    """Generate actionable, domain-grounded recommendations for Pravin's frontend dashboard."""
    recs: List[Dict[str, str]] = []
    if risks.get("heat", 0.0) >= 60.0:
        recs.append({
            "hazard": "heat",
            "priority": "High" if risks["heat"] < 80.0 else "Critical",
            "action": "Issue outdoor worker heat-hydration advisory between 12:00–16:00 and activate urban cooling shelters.",
        })
    if risks.get("flood", 0.0) >= 60.0:
        recs.append({
            "hazard": "flood",
            "priority": "High" if risks["flood"] < 80.0 else "Critical",
            "action": "Monitor low-lying drainage bottlenecks and pre-position stormwater pumping units.",
        })
    if risks.get("air_quality", 0.0) >= 60.0:
        recs.append({
            "hazard": "air_quality",
            "priority": "High" if risks["air_quality"] < 80.0 else "Critical",
            "action": "Enforce dust-suppression misting at construction corridors and advise N95 masks for sensitive groups.",
        })
    if risks.get("water_stress", 0.0) >= 60.0:
        recs.append({
            "hazard": "water_stress",
            "priority": "High" if risks["water_stress"] < 80.0 else "Critical",
            "action": "Optimize agricultural drip-irrigation scheduling and prioritize soil-moisture conservation mulching.",
        })
    if not recs:
        recs.append({
            "hazard": "overall",
            "priority": "Routine",
            "action": f"Environmental conditions within manageable range (Score {composite_score:.1f}/100); continue routine telemetry monitoring.",
        })
    return recs


def generate_complete_prediction(
    environmental_data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
    scenario: Optional[Dict[str, Any]] = None,
    weights: Optional[Dict[str, float]] = None,
    include_explainability: bool = True,
) -> Dict[str, Any]:
    """
    Central orchestration entry point for Mayuresh's FastAPI backend (`/api/predict`).
    1. Validates & preprocesses input data.
    2. Engineers causal environmental features.
    3. Executes Heat, Flood, Air-Quality, and Water-Stress hazard models.
    4. Computes the composite Climate Risk Score (0-100).
    5. Computes Explainable AI feature attributions.
    6. Optionally executes a What-If counterfactual scenario.
    7. Returns a strictly JSON-compatible response matching the team Integration Contract.
    """
    feat_df, meta = preprocess_environmental_data(environmental_data, return_metadata=True)
    latest_row = feat_df.iloc[-1]

    location = str(latest_row.get("location", "Pune"))
    ts_val = pd.to_datetime(latest_row.get("timestamp")).strftime("%Y-%m-%dT%H:%M:%S")

    missing_map = meta["preprocessing_report"].get("missing_counts_before_imputation", {})
    heat_missing = sum(1 for k in ["temperature_c", "humidity_pct", "wind_speed_kmh"] if missing_map.get(k, 1) > 0)
    flood_missing = sum(1 for k in ["rainfall_mm", "humidity_pct"] if missing_map.get(k, 1) > 0)
    pol_cols = ["pm25_ugm3", "pm10_ugm3", "no2_ugm3", "so2_ugm3", "co_mgm3", "o3_ugm3"]
    pol_missing = sum(1 for k in pol_cols if missing_map.get(k, 1) > 0)

    _BUNDLE.ensure_loaded()
    assert _BUNDLE.heat_model is not None
    assert _BUNDLE.flood_model is not None
    assert _BUNDLE.air_quality_model is not None
    assert _BUNDLE.water_stress_model is not None

    heat_out = _BUNDLE.heat_model.predict(feat_df, missing_core_count=heat_missing)
    flood_out = _BUNDLE.flood_model.predict(
        feat_df,
        missing_core_count=flood_missing,
        soil_moisture_measured=bool(meta["soil_moisture_measured"]),
    )
    aq_out = _BUNDLE.air_quality_model.predict(
        feat_df,
        missing_pollutant_count=pol_missing,
        measured_aqi_supplied=meta["measured_aqi_supplied"],
    )
    ws_out = _BUNDLE.water_stress_model.predict(
        feat_df,
        soil_moisture_measured=bool(meta["soil_moisture_measured"]),
        evapotranspiration_measured=bool(meta["evapotranspiration_measured"]),
    )

    risks_summary = {
        "heat": round(float(heat_out["heat_risk"]), 2),
        "flood": round(float(flood_out["flood_risk"]), 2),
        "air_quality": round(float(aq_out["air_quality_risk"]), 2),
        "water_stress": round(float(ws_out["water_stress_risk"]), 2),
    }

    composite_out = calculate_climate_risk_score(risks_summary, weights=weights)

    explain_out = (
        explain_prediction(feat_df, risks_summary)
        if include_explainability
        else {}
    )

    what_if_out = (
        run_what_if_scenario(copy.deepcopy(environmental_data), scenario)
        if scenario is not None
        else {}
    )

    recommendations = _generate_stakeholder_recommendations(
        risks_summary,
        float(composite_out["climate_risk_score"]),
    )

    response = {
        "location": location,
        "timestamp": ts_val,
        "data_status": "available",
        "risks": risks_summary,
        "hazard_details": {
            "heat": heat_out,
            "flood": flood_out,
            "air_quality": aq_out,
            "water_stress": ws_out,
        },
        "climate_risk_score": composite_out["climate_risk_score"],
        "risk_level": composite_out["risk_level"],
        "weights": composite_out["weights"],
        "data_coverage": composite_out["data_coverage"],
        "input_feature_coverage_pct": meta["preprocessing_report"].get("data_coverage_pct", 100.0),
        "explainability": explain_out,
        "what_if": what_if_out,
        "recommendations": recommendations,
    }
    return _to_json_compatible(response)

