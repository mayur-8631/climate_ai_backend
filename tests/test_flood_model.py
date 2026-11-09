"""
Automated Unit Tests for Module 4: Rainfall & Flood-Risk Prediction Model
File: tests/test_flood_model.py
"""

from pathlib import Path
import pandas as pd
import pytest

from ml_engine.flood_model import FloodRiskModel
from ml_engine.predict import predict_flood_risk


def test_flood_model_output_and_scientific_proxy_metadata():
    """Verify flood model returns 0-100 score, separated 24h rainfall forecast, and proxy disclaimer."""
    payload = {
        "timestamp": "2026-07-24T12:00:00",
        "location": "Pune",
        "temperature_c": 24.5,
        "humidity_pct": 89.0,
        "rainfall_mm": 92.0,
        "rainfall_intensity_mm_hr": 31.0,
        "soil_moisture": 0.84,
        "elevation_m": 555.0,
        "drainage_index": 0.45,
    }
    res = predict_flood_risk(payload)
    assert 0.0 <= res["flood_risk"] <= 100.0
    assert res["risk_level"] in {"Very Low", "Low", "Moderate", "High", "Very High"}
    assert 0.0 <= res["confidence"] <= 1.0
    assert isinstance(res["contributing_factors"], list) and len(res["contributing_factors"]) > 0
    assert "forecast_next_24h_rainfall_mm" in res
    assert res["is_proxy_hazard"] is True
    assert "limitations" in res and "High rainfall does not automatically mean flooding" in res["limitations"]


def test_flood_model_distinguishes_dry_vs_saturated_rain():
    """Verify intense monsoon rainfall on saturated soil yields higher flood risk than dry conditions."""
    dry_payload = {
        "timestamp": "2026-03-10T12:00:00",
        "location": "Pune",
        "rainfall_mm": 0.0,
        "rainfall_intensity_mm_hr": 0.0,
        "humidity_pct": 35.0,
        "soil_moisture": 0.14,
    }
    monsoon_flood_payload = {
        "timestamp": "2026-07-25T12:00:00",
        "location": "Pune",
        "rainfall_mm": 135.0,
        "rainfall_intensity_mm_hr": 44.0,
        "cumulative_rainfall_3d_mm": 240.0,
        "cumulative_rainfall_7d_mm": 360.0,
        "humidity_pct": 94.0,
        "soil_moisture": 0.88,
    }
    dry_res = predict_flood_risk(dry_payload)
    wet_res = predict_flood_risk(monsoon_flood_payload)
    assert wet_res["flood_risk"] > dry_res["flood_risk"] + 35.0


def test_flood_model_missing_artifact_error(tmp_path: Path):
    """Verify clear FileNotFoundError when flood model artifact is missing."""
    m = FloodRiskModel(model_dir=tmp_path / "missing_flood")
    with pytest.raises(FileNotFoundError, match="Trained FloodRiskModel artifact not found"):
        m.load()


def test_flood_model_insufficient_features_error():
    """Verify clear ValueError when required flood features are missing."""
    m = FloodRiskModel().load()
    with pytest.raises(ValueError, match="missing required features"):
        m.predict(pd.DataFrame([{"rainfall_mm": 25.0}]))

