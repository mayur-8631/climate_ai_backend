"""
Automated Unit Tests for Module 6: Water-Stress Analysis Model
File: tests/test_water_stress.py
"""

from pathlib import Path
import pandas as pd
import pytest

from ml_engine.predict import predict_water_stress
from ml_engine.water_stress_model import WaterStressModel


def test_water_stress_output_and_unmeasured_variable_reporting():
    """
    Verify water stress model reports when direct soil_moisture or evapotranspiration
    was not measured in the input payload, and includes the municipal water scope disclaimer.
    """
    payload_without_soil = {
        "timestamp": "2026-04-22T12:00:00",
        "location": "Pune",
        "temperature_c": 35.8,
        "temp_max_c": 40.5,
        "temp_min_c": 24.5,
        "humidity_pct": 24.0,
        "rainfall_mm": 0.0,
    }
    res = predict_water_stress(payload_without_soil)
    assert 0.0 <= res["water_stress_risk"] <= 100.0
    assert res["risk_level"] in {"Very Low", "Low", "Moderate", "High", "Very High"}
    assert 0.0 <= res["confidence"] <= 1.0
    assert isinstance(res["contributing_factors"], list) and len(res["contributing_factors"]) > 0
    assert any("soil_moisture" in note for note in res["data_status_notes"])
    assert "Municipal reservoir levels" in res["scope_disclaimer"]


def test_water_stress_arid_summer_vs_wet_monsoon():
    """Verify hot dry summer with depleted soil moisture yields higher water stress than wet monsoon."""
    arid_payload = {
        "timestamp": "2026-05-05T12:00:00",
        "location": "Pune",
        "temperature_c": 36.5,
        "temp_max_c": 41.2,
        "temp_min_c": 26.0,
        "humidity_pct": 20.0,
        "rainfall_mm": 0.0,
        "soil_moisture": 0.11,
        "evapotranspiration_mm": 8.2,
    }
    monsoon_payload = {
        "timestamp": "2026-08-12T12:00:00",
        "location": "Pune",
        "temperature_c": 24.0,
        "temp_max_c": 27.5,
        "temp_min_c": 21.5,
        "humidity_pct": 88.0,
        "rainfall_mm": 45.0,
        "soil_moisture": 0.82,
        "evapotranspiration_mm": 2.4,
    }
    arid_res = predict_water_stress(arid_payload)
    wet_res = predict_water_stress(monsoon_payload)
    assert arid_res["water_stress_risk"] > wet_res["water_stress_risk"] + 35.0


def test_water_stress_missing_artifact_error(tmp_path: Path):
    """Verify FileNotFoundError when water stress model artifact is missing."""
    m = WaterStressModel(model_dir=tmp_path / "missing_ws")
    with pytest.raises(FileNotFoundError, match="Trained WaterStressModel artifact not found"):
        m.load()


def test_water_stress_insufficient_features_error():
    """Verify ValueError when required water stress features are missing."""
    m = WaterStressModel().load()
    with pytest.raises(ValueError, match="missing required features"):
        m.predict(pd.DataFrame([{"soil_moisture": 0.35}]))

