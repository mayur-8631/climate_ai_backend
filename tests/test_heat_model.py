"""
Automated Unit Tests for Module 3: Heat-Risk Prediction Model
File: tests/test_heat_model.py
"""

from pathlib import Path
import pandas as pd
import pytest

from ml_engine.heat_model import HeatRiskModel
from ml_engine.predict import predict_heat_risk


def test_heat_model_output_range_and_structure():
    """Verify heat model returns 0-100 score, valid risk_level, confidence, and contributing_factors."""
    payload = {
        "timestamp": "2026-05-12T12:00:00",
        "location": "Pune",
        "temperature_c": 37.5,
        "temp_max_c": 41.8,
        "temp_min_c": 26.2,
        "humidity_pct": 44.0,
        "wind_speed_kmh": 9.5,
    }
    res = predict_heat_risk(payload)
    assert "heat_risk" in res
    assert "risk_level" in res
    assert "confidence" in res
    assert "contributing_factors" in res
    assert 0.0 <= res["heat_risk"] <= 100.0
    assert res["risk_level"] in {"Very Low", "Low", "Moderate", "High", "Very High"}
    assert 0.0 <= res["confidence"] <= 1.0
    assert isinstance(res["contributing_factors"], list) and len(res["contributing_factors"]) > 0


def test_heat_model_monotonic_sensitivity():
    """Verify extreme summer heat produces a significantly higher heat_risk than cool winter weather."""
    cool_payload = {
        "timestamp": "2026-01-15T12:00:00",
        "location": "Pune",
        "temperature_c": 19.5,
        "temp_max_c": 26.0,
        "temp_min_c": 11.5,
        "humidity_pct": 45.0,
        "wind_speed_kmh": 14.0,
    }
    hot_payload = {
        "timestamp": "2026-05-15T12:00:00",
        "location": "Pune",
        "temperature_c": 38.5,
        "temp_max_c": 43.2,
        "temp_min_c": 28.0,
        "humidity_pct": 55.0,
        "wind_speed_kmh": 6.0,
    }
    cool_res = predict_heat_risk(cool_payload)
    hot_res = predict_heat_risk(hot_payload)
    assert hot_res["heat_risk"] > cool_res["heat_risk"] + 25.0


def test_heat_model_missing_artifact_error(tmp_path: Path):
    """Verify clear FileNotFoundError when loading a model from an empty directory."""
    untrained_model = HeatRiskModel(model_dir=tmp_path / "nonexistent_heat")
    with pytest.raises(FileNotFoundError, match="Trained HeatRiskModel artifact not found"):
        untrained_model.load()


def test_heat_model_insufficient_features_error():
    """Verify clear ValueError when calling predict() with missing required features."""
    model = HeatRiskModel().load()
    incomplete_df = pd.DataFrame([{"temperature_c": 32.0}])
    with pytest.raises(ValueError, match="missing required features"):
        model.predict(incomplete_df)

