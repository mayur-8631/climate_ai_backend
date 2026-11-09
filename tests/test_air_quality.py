"""
Automated Unit Tests for Module 5: Air-Quality Risk Prediction Model
File: tests/test_air_quality.py
"""

from pathlib import Path
import pandas as pd
import pytest

from ml_engine.air_quality_model import AirQualityRiskModel
from ml_engine.predict import predict_air_quality_risk


def test_air_quality_model_output_and_dominant_pollutants():
    """Verify air quality model returns 0-100 score, dominant pollutants, and CPCB AQI distinction."""
    payload = {
        "timestamp": "2026-12-18T12:00:00",
        "location": "Pune",
        "temperature_c": 19.5,
        "humidity_pct": 62.0,
        "wind_speed_kmh": 4.2,
        "pm25_ugm3": 142.0,
        "pm10_ugm3": 265.0,
        "no2_ugm3": 74.0,
        "so2_ugm3": 24.0,
        "co_mgm3": 2.1,
        "o3_ugm3": 38.0,
        "measured_aqi": 318.0,
    }
    res = predict_air_quality_risk(payload)
    assert 0.0 <= res["air_quality_risk"] <= 100.0
    assert res["risk_level"] in {"Very Low", "Low", "Moderate", "High", "Very High"}
    assert 0.0 <= res["confidence"] <= 1.0
    assert "PM2.5" in res["dominant_pollutants"]
    assert res["source_measured_aqi"] == 318.0
    assert res["aqi_source_distinction"] == "source_measured_aqi_and_ml_hazard_both_available"


def test_air_quality_clean_vs_polluted():
    """Verify clean monsoon air yields much lower risk than winter inversion smog."""
    clean_payload = {
        "timestamp": "2026-08-10T12:00:00",
        "location": "Pune",
        "temperature_c": 24.0,
        "humidity_pct": 85.0,
        "wind_speed_kmh": 18.0,
        "pm25_ugm3": 14.0,
        "pm10_ugm3": 32.0,
        "no2_ugm3": 12.0,
        "so2_ugm3": 6.0,
        "co_mgm3": 0.4,
        "o3_ugm3": 22.0,
    }
    polluted_payload = {
        "timestamp": "2026-12-20T12:00:00",
        "location": "Pune",
        "temperature_c": 18.0,
        "humidity_pct": 68.0,
        "wind_speed_kmh": 3.0,
        "pm25_ugm3": 165.0,
        "pm10_ugm3": 310.0,
        "no2_ugm3": 95.0,
        "so2_ugm3": 35.0,
        "co_mgm3": 2.8,
        "o3_ugm3": 55.0,
    }
    clean_res = predict_air_quality_risk(clean_payload)
    pol_res = predict_air_quality_risk(polluted_payload)
    assert pol_res["air_quality_risk"] > clean_res["air_quality_risk"] + 40.0


def test_air_quality_missing_artifact_error(tmp_path: Path):
    """Verify FileNotFoundError when air quality model artifact is missing."""
    m = AirQualityRiskModel(model_dir=tmp_path / "missing_aq")
    with pytest.raises(FileNotFoundError, match="Trained AirQualityRiskModel artifact not found"):
        m.load()


def test_air_quality_insufficient_features_error():
    """Verify ValueError when required air quality features are missing."""
    m = AirQualityRiskModel().load()
    with pytest.raises(ValueError, match="missing required features"):
        m.predict(pd.DataFrame([{"pm25_ugm3": 55.0}]))

