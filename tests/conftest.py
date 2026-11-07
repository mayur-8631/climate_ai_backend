import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def sample_weather_raw():
    return {
        "latitude": 18.5204,
        "longitude": 73.8567,
        "_metadata": {
            "source": "Open-Meteo Weather API",
            "fetched_at": "2026-11-07T12:00:00Z"
        },
        "current": {
            "time": "2026-11-07T12:00:00Z",
            "temperature_2m": 35.2,
            "apparent_temperature": 38.0,
            "relative_humidity_2m": 45.0,
            "precipitation": 0.0,
            "rain": 0.0,
            "wind_speed_10m": 12.0,
            "surface_pressure": 952.0,
            "weather_code": 1
        },
        "hourly": {
            "time": ["2026-11-07T12:00:00Z", "2026-11-07T13:00:00Z"],
            "temperature_2m": [35.2, 36.0],
            "relative_humidity_2m": [45.0, 42.0],
            "precipitation": [0.0, 0.0],
            "wind_speed_10m": [12.0, 14.0]
        },
        "daily": {
            "time": ["2026-11-07"],
            "temperature_2m_max": [37.5],
            "temperature_2m_min": [22.0],
            "precipitation_sum": [0.0],
            "wind_speed_10m_max": [16.0]
        }
    }


@pytest.fixture
def sample_air_quality_raw():
    return {
        "latitude": 18.5204,
        "longitude": 73.8567,
        "_metadata": {
            "source": "Open-Meteo Air Quality API",
            "fetched_at": "2026-11-07T12:00:00Z"
        },
        "current": {
            "time": "2026-11-07T12:00:00Z",
            "us_aqi": 145,
            "pm10": 98.0,
            "pm2_5": 58.5,
            "carbon_monoxide": 450.0,
            "nitrogen_dioxide": 28.0,
            "sulphur_dioxide": 12.0,
            "ozone": 45.0
        },
        "hourly": {
            "time": ["2026-11-07T12:00:00Z"],
            "us_aqi": [145],
            "pm2_5": [58.5],
            "pm10": [98.0],
            "nitrogen_dioxide": [28.0]
        }
    }

