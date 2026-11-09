"""
Automated Unit Tests for Module 9: Explainable AI (XAI) Engine
File: tests/test_explainability.py
"""

import pandas as pd
import pytest

from ml_engine.explainability import ClimateExplainabilityEngine
from ml_engine.heat_model import HeatRiskModel
from ml_engine.predict import explain_prediction


def test_explainability_generation_and_structure():
    """Verify explain_prediction produces valid primary_factors, directional effect, and summary."""
    payload = {
        "timestamp": "2026-05-14T12:00:00",
        "location": "Pune",
        "temperature_c": 38.2,
        "temp_max_c": 42.6,
        "temp_min_c": 26.8,
        "humidity_pct": 52.0,
        "wind_speed_kmh": 8.0,
        "rainfall_mm": 0.0,
        "pm25_ugm3": 68.0,
        "pm10_ugm3": 140.0,
        "soil_moisture": 0.16,
    }
    res = explain_prediction(payload)
    assert "explanation" in res
    exp = res["explanation"]
    assert "primary_factors" in exp and len(exp["primary_factors"]) > 0
    assert "summary" in exp and isinstance(exp["summary"], str) and len(exp["summary"]) > 15
    assert "by_hazard" in exp

    for factor in exp["primary_factors"]:
        assert "feature" in factor
        assert factor["effect"] in {"increases_risk", "decreases_risk"}
        assert "importance" in factor and factor["importance"] is not None
        assert "contribution_points" in factor

    # For extreme summer heat (42.6°C max), heat primary factors should increase risk
    heat_factors = exp["by_hazard"]["heat"]["primary_factors"]
    assert any(f["effect"] == "increases_risk" for f in heat_factors)


def test_explainability_missing_or_empty_data_handling():
    """Verify explainability engine raises clear ValueError on empty input."""
    engine = ClimateExplainabilityEngine()
    heat_model = HeatRiskModel().load()
    with pytest.raises(ValueError, match="empty"):
        engine.explain_single_hazard("heat", heat_model, pd.DataFrame())

