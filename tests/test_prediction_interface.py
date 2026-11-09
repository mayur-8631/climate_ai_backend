"""
Automated Integration Tests for Module 11: Backend Prediction Interface (`ml_engine/predict.py`)
File: tests/test_prediction_interface.py
"""

import json
import pytest

from ml_engine.predict import (
    calculate_climate_risk_score,
    explain_prediction,
    generate_complete_prediction,
    predict_air_quality_risk,
    predict_flood_risk,
    predict_heat_risk,
    predict_water_stress,
    preprocess_environmental_data,
    run_what_if_scenario,
)


def test_complete_prediction_json_contract_and_field_names():
    """
    Verify `generate_complete_prediction` returns a strictly JSON-serializable response
    matching the exact schema coordinated with Mayuresh Kamble and Pravin Kamble.
    """
    payload = {
        "location": "Pune",
        "timestamp": "2026-11-09T12:00:00",
        "temperature_c": 31.2,
        "temp_max_c": 35.8,
        "temp_min_c": 19.4,
        "humidity_pct": 54.0,
        "wind_speed_kmh": 11.0,
        "rainfall_mm": 12.5,
        "rainfall_intensity_mm_hr": 4.2,
        "soil_moisture": 0.42,
        "evapotranspiration_mm": 4.8,
        "pm25_ugm3": 64.0,
        "pm10_ugm3": 128.0,
        "no2_ugm3": 41.0,
        "so2_ugm3": 14.0,
        "co_mgm3": 1.1,
        "o3_ugm3": 48.0,
    }
    res = generate_complete_prediction(
        payload,
        scenario={"rainfall_change_percent": 30, "temperature_delta_c": 2.0},
    )

    # Must serialize cleanly to standard JSON without custom encoders
    serialized = json.dumps(res)
    parsed = json.loads(serialized)

    required_top_keys = {
        "location",
        "timestamp",
        "data_status",
        "risks",
        "hazard_details",
        "climate_risk_score",
        "risk_level",
        "data_coverage",
        "explainability",
        "what_if",
        "recommendations",
    }
    assert required_top_keys.issubset(parsed.keys())
    assert parsed["location"] == "Pune"
    assert parsed["data_status"] == "available"
    assert set(parsed["risks"].keys()) == {"heat", "flood", "air_quality", "water_stress"}
    for h_score in parsed["risks"].values():
        assert 0.0 <= h_score <= 100.0
    assert 0.0 <= parsed["climate_risk_score"] <= 100.0
    assert parsed["risk_level"] in {"Very Low", "Low", "Moderate", "High", "Very High"}
    assert parsed["data_coverage"] == 100.0
    assert "explanation" in parsed["explainability"]
    assert "baseline_score" in parsed["what_if"]


def test_all_required_entrypoint_functions_callable():
    """Verify all 9 required functions in `ml_engine/predict.py` work seamlessly."""
    sample = {
        "location": "Pune",
        "timestamp": "2026-06-20T12:00:00",
        "temperature": 29.0,
        "humidity": 78.0,
        "rainfall": 48.0,
        "pm25": 35.0,
    }
    df_feat = preprocess_environmental_data(sample)
    assert len(df_feat) == 1

    h_out = predict_heat_risk(sample)
    f_out = predict_flood_risk(sample)
    a_out = predict_air_quality_risk(sample)
    w_out = predict_water_stress(sample)

    c_out = calculate_climate_risk_score(
        {"heat": h_out, "flood": f_out, "air_quality": a_out, "water_stress": w_out}
    )
    assert 0.0 <= c_out["climate_risk_score"] <= 100.0

    e_out = explain_prediction(sample, c_out)
    assert "explanation" in e_out

    s_out = run_what_if_scenario(sample, {"rainfall_change_percent": 25})
    assert s_out["scenario_score"] >= 0.0


def test_error_handling_on_empty_or_invalid_payload():
    """Verify backend interface raises clear ValueError on empty or measurement-free payloads."""
    with pytest.raises(ValueError, match="cannot be None or empty"):
        generate_complete_prediction({})

    with pytest.raises(ValueError, match="Insufficient environmental data"):
        generate_complete_prediction({"location": "Pune", "timestamp": "2026-11-09T12:00:00"})

