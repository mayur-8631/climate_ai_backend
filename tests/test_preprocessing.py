"""
Unified Automated Unit Tests for Backend Ingestion Cleaning (`app.services.preprocessing`)
and ML Engine Data Preprocessing & Feature Engineering (`ml_engine.data_preprocessing` & `ml_engine.feature_engineering`)
File: tests/test_preprocessing.py
"""

import numpy as np
import pandas as pd
import pytest

from app.schemas.common import DataQuality
from app.services.preprocessing.cleaner import DataCleaner
from app.services.preprocessing.feature_pipeline import FeaturePipeline
from app.services.preprocessing.normalizer import EnvironmentalNormalizer
from ml_engine.data_preprocessing import EnvironmentalDataPreprocessor
from ml_engine.feature_engineering import EnvironmentalFeatureEngineer


# ============================================================================
# PART 1: BACKEND TELEMETRY CLEANER & NORMALIZER TESTS (Mayuresh Kamble)
# ============================================================================

def test_cleaner_preserves_measured_zero(sample_weather_raw):
    cleaned = DataCleaner.clean_weather_payload(sample_weather_raw, "Pune")
    assert cleaned.current.precipitation == 0.0
    assert cleaned.current.precipitation_unit == "mm"
    assert cleaned.provenance.quality_flag == DataQuality.GOOD


def test_cleaner_preserves_missing_data_as_none(sample_weather_raw):
    sample_weather_raw["current"]["precipitation"] = None
    cleaned = DataCleaner.clean_weather_payload(sample_weather_raw, "Pune")
    assert cleaned.current.precipitation is None
    assert cleaned.provenance.quality_flag == DataQuality.DEGRADED


def test_normalizer_heat_index():
    hi = EnvironmentalNormalizer.calculate_heat_index(35.0, 60.0)
    assert hi > 38.0
    assert hi < 55.0


def test_normalizer_scale_bounds():
    assert EnvironmentalNormalizer.normalize_to_scale(150.0, 0.0, 100.0) == 100.0
    assert EnvironmentalNormalizer.normalize_to_scale(-10.0, 0.0, 100.0) == 0.0
    assert EnvironmentalNormalizer.normalize_to_scale(50.0, 0.0, 100.0) == 50.0


def test_feature_pipeline_extraction(sample_weather_raw, sample_air_quality_raw):
    clean_w = DataCleaner.clean_weather_payload(sample_weather_raw, "Pune")
    clean_aq = DataCleaner.clean_air_quality_payload(sample_air_quality_raw, "Pune")

    features = FeaturePipeline.extract_features(clean_w, clean_aq)
    assert "temp_c" in features
    assert "humidity_pct" in features
    assert "heat_index_c" in features
    assert "precip_24h_sum_mm" in features
    assert "aqi" in features
    assert features["temp_c"] == 35.2
    assert features["aqi"] == 145


# ============================================================================
# PART 2: ML ENGINE DATA PREPROCESSING & FEATURE ENGINEERING TESTS (Lokesh Joshi)
# ============================================================================

def _make_sample_training_df() -> pd.DataFrame:
    dates = pd.date_range("2025-01-01", periods=30, freq="D")
    return pd.DataFrame(
        {
            "timestamp": [d.strftime("%Y-%m-%dT12:00:00") for d in dates],
            "location": ["Pune"] * 30,
            "temperature_c": np.linspace(22.0, 34.0, 30),
            "temp_max_c": np.linspace(28.0, 40.0, 30),
            "temp_min_c": np.linspace(15.0, 24.0, 30),
            "humidity_pct": np.linspace(40.0, 75.0, 30),
            "wind_speed_kmh": np.linspace(8.0, 18.0, 30),
            "rainfall_mm": np.concatenate([np.zeros(20), np.linspace(5.0, 80.0, 10)]),
            "pm25_ugm3": np.linspace(30.0, 90.0, 30),
            "pm10_ugm3": np.linspace(60.0, 180.0, 30),
            "soil_moisture": np.linspace(0.25, 0.65, 30),
            "evapotranspiration_mm": np.linspace(3.0, 6.5, 30),
        }
    )


def test_missing_values_never_replaced_with_zero():
    """Verify missing environmental observations are imputed with training medians, NEVER zero."""
    train_df = _make_sample_training_df()
    prep = EnvironmentalDataPreprocessor(preserve_missing_indicators=True)
    prep.fit(train_df)

    test_payload = {
        "timestamp": "2026-04-15T12:00:00",
        "location": "Pune",
        "temperature_c": None,
        "humidity_pct": np.nan,
        "pm25_ugm3": None,
    }
    clean_df, report = prep.transform(test_payload, return_report=True)
    assert clean_df["temperature_c"].iloc[0] > 15.0
    assert clean_df["humidity_pct"].iloc[0] > 20.0
    assert clean_df["pm25_ugm3"].iloc[0] > 10.0
    assert clean_df["temperature_c_is_missing"].iloc[0] == 1
    assert report["missing_counts_before_imputation"]["temperature_c"] == 1


def test_duplicate_records_removed():
    """Verify duplicate (location, timestamp) rows are deduplicated."""
    train_df = _make_sample_training_df()
    dup_df = pd.concat([train_df, train_df.iloc[[0, 1]]], ignore_index=True)
    prep = EnvironmentalDataPreprocessor()
    clean_df, report = prep.fit_transform(dup_df, return_report=True)
    assert len(clean_df) == len(train_df)
    assert report["duplicate_rows_removed"] == 2


def test_impossible_values_and_extreme_weather_preservation():
    """
    Verify physically impossible values (e.g., humidity=180%, temperature=250°C) are
    flagged and replaced with NaN -> imputed, while genuine extreme weather events
    (e.g., rainfall=160 mm, temp_max=44.5°C) are preserved and never deleted.
    """
    train_df = _make_sample_training_df()
    prep = EnvironmentalDataPreprocessor()
    prep.fit(train_df)

    records = [
        {
            "timestamp": "2026-05-10T12:00:00",
            "location": "Pune",
            "temperature_c": 250.0,
            "humidity_pct": 185.0,
            "rainfall_mm": -15.0,
            "pm25_ugm3": 45.0,
        },
        {
            "timestamp": "2026-07-20T12:00:00",
            "location": "Pune",
            "temperature_c": 43.5,
            "temp_max_c": 45.0,
            "humidity_pct": 88.0,
            "rainfall_mm": 165.0,
            "pm25_ugm3": 35.0,
        },
    ]
    clean_df, report = prep.transform(records, return_report=True)
    assert len(clean_df) == 2
    assert report["impossible_value_counts"]["temperature_c"] == 1
    assert report["impossible_value_counts"]["humidity_pct"] == 1
    assert report["impossible_value_counts"]["rainfall_mm"] == 1
    assert np.isclose(clean_df.iloc[1]["rainfall_mm"], 165.0)
    assert np.isclose(clean_df.iloc[1]["temp_max_c"], 45.0)
    assert clean_df.iloc[1]["is_climate_extreme"] == 1


def test_incorrect_data_types_and_unit_conversions():
    """Verify string numbers, malformed strings, and Kelvin/m-s units are handled properly."""
    train_df = _make_sample_training_df()
    prep = EnvironmentalDataPreprocessor()
    prep.fit(train_df)

    dirty_input = {
        "timestamp": "not-a-timestamp",
        "location": "Pune",
        "temperature_k": 308.15,
        "wind_speed_ms": 5.0,
        "humidity": "62.5",
        "pm25": "corrupted_sensor",
    }
    clean_df, report = prep.transform(dirty_input, return_report=True)
    assert report["invalid_timestamp_count"] == 1
    assert report["non_numeric_coercions"]["pm25_ugm3"] == 1
    assert np.isclose(clean_df["temperature_c"].iloc[0], 35.0, atol=0.1)
    assert np.isclose(clean_df["wind_speed_kmh"].iloc[0], 18.0, atol=0.1)
    assert np.isclose(clean_df["humidity_pct"].iloc[0], 62.5, atol=0.1)


def test_feature_engineering_causal_no_leakage():
    """Verify derived rolling and lagged features do not leak future rows into past rows."""
    train_df = _make_sample_training_df()
    prep = EnvironmentalDataPreprocessor()
    clean_df = prep.fit_transform(train_df)
    eng = EnvironmentalFeatureEngineer()

    feat_full = eng.transform(clean_df)
    feat_prefix = eng.transform(clean_df.iloc[:15])

    for col in ["temp_rolling_3d_mean", "rainfall_rolling_7d_sum", "heat_index_c", "cpcb_calculated_aqi"]:
        np.testing.assert_allclose(
            feat_full[col].iloc[:15].to_numpy(),
            feat_prefix[col].to_numpy(),
            rtol=1e-6,
        )
