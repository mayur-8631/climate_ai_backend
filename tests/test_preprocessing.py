from app.services.preprocessing.cleaner import DataCleaner
from app.services.preprocessing.normalizer import EnvironmentalNormalizer
from app.services.preprocessing.feature_pipeline import FeaturePipeline
from app.schemas.common import DataQuality


def test_cleaner_preserves_measured_zero(sample_weather_raw):
    cleaned = DataCleaner.clean_weather_payload(sample_weather_raw, "Pune")
    assert cleaned.current.precipitation == 0.0
    assert cleaned.current.precipitation_unit == "mm"
    assert cleaned.provenance.quality_flag == DataQuality.GOOD


def test_cleaner_preserves_missing_data_as_none(sample_weather_raw):
    # Set precipitation to None to simulate sensor failure
    sample_weather_raw["current"]["precipitation"] = None
    cleaned = DataCleaner.clean_weather_payload(sample_weather_raw, "Pune")

    # MUST NOT be 0.0 - Must remain None!
    assert cleaned.current.precipitation is None
    assert cleaned.provenance.quality_flag == DataQuality.DEGRADED


def test_normalizer_heat_index():
    # At 35C and 60% humidity, heat index should be significantly higher than ambient temp
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

