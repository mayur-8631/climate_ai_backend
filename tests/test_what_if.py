"""
Automated Unit Tests for Module 10: What-If Climate Scenario Engine
File: tests/test_what_if.py
"""

import copy
import pytest

from ml_engine.predict import run_what_if_scenario


def test_what_if_rainfall_increase_and_input_preservation():
    """
    Verify increasing rainfall by +30% increases flood risk and recalculates
    the overall Climate Risk Score without mutating the original input dict.
    """
    original_data = {
        "timestamp": "2026-07-18T12:00:00",
        "location": "Pune",
        "temperature_c": 26.5,
        "temp_max_c": 30.0,
        "temp_min_c": 22.5,
        "humidity_pct": 85.0,
        "wind_speed_kmh": 14.0,
        "rainfall_mm": 85.0,
        "rainfall_intensity_mm_hr": 24.0,
        "soil_moisture": 0.76,
        "pm25_ugm3": 28.0,
        "pm10_ugm3": 55.0,
    }
    snapshot_before = copy.deepcopy(original_data)
    scenario = {"rainfall_change_percent": 30}

    res = run_what_if_scenario(original_data, scenario)

    # Original input must never be mutated
    assert original_data == snapshot_before
    assert "baseline_score" in res
    assert "scenario_score" in res
    assert "change" in res
    assert "change_percentage" in res
    assert res["scenario"] == {"rainfall_change_percent": 30}
    assert res["hazard_comparison"]["flood"]["scenario"] > res["hazard_comparison"]["flood"]["baseline"]
    assert res["scenario_score"] >= res["baseline_score"]


def test_what_if_unsupported_and_unrealistic_scenario_handling():
    """Verify unsupported scenario parameters or impossible percentages raise ValueError."""
    base_data = {
        "timestamp": "2026-05-10T12:00:00",
        "location": "Pune",
        "temperature_c": 34.0,
        "humidity_pct": 45.0,
        "rainfall_mm": 10.0,
    }
    with pytest.raises(ValueError, match="Unsupported scenario parameter"):
        run_what_if_scenario(base_data, {"solar_flare_percent": 50})

    with pytest.raises(ValueError, match="Unrealistic percentage change"):
        run_what_if_scenario(base_data, {"rainfall_change_percent": -150})

    with pytest.raises(ValueError, match="violates physical bounds"):
        run_what_if_scenario(base_data, {"humidity_pct": 145.0})

