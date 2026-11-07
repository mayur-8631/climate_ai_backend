from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


def test_root_and_health(client: TestClient):
    res_root = client.get("/")
    assert res_root.status_code == 200
    assert "ClimateTwin" in res_root.json()["project"]

    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"


def test_locations_endpoint(client: TestClient):
    res = client.get("/api/v1/locations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["city"] == "Pune"
    assert len(data[0]["wards"]) >= 6
    ward_names = [w["name"] for w in data[0]["wards"]]
    assert "Shivajinagar" in ward_names


@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_weather")
@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_air_quality")
def test_wards_risk_map_contract(mock_aqi, mock_weather, client: TestClient, sample_weather_raw, sample_air_quality_raw):
    mock_weather.return_value = sample_weather_raw
    mock_aqi.return_value = sample_air_quality_raw

    res = client.get("/api/v1/risk-score/map")
    assert res.status_code == 200
    data = res.json()

    assert data["city"] == "Pune"
    assert "centroid" in data
    assert "total_wards" in data
    assert data["total_wards"] >= 6
    assert "citywide_average_risk" in data
    assert len(data["wards"]) >= 6

    # Verify first ward structure for Leaflet map integration
    w0 = data["wards"][0]
    assert "ward_code" in w0
    assert "name" in w0
    assert "coordinates" in w0
    assert "latitude" in w0["coordinates"]
    assert "longitude" in w0["coordinates"]
    assert "climate_risk_score" in w0
    assert "risk_level" in w0
    assert "marker_color" in w0
    assert w0["marker_color"].startswith("#")  # Valid hex color code
    assert "primary_hazard" in w0
    assert "risks" in w0


@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_weather")
@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_air_quality")
def test_risk_score_contract(mock_aqi, mock_weather, client: TestClient, sample_weather_raw, sample_air_quality_raw):
    mock_weather.return_value = sample_weather_raw
    mock_aqi.return_value = sample_air_quality_raw

    res = client.get("/api/v1/risk-score?location=Pune&ward=Shivajinagar")
    assert res.status_code == 200
    data = res.json()

    # Exact field contract verification for Pravin's Next.js Frontend
    assert data["location"] == "Pune"
    assert data["ward"] == "Shivajinagar"
    assert "temperature" in data
    assert "rainfall" in data
    assert "aqi" in data
    assert "risks" in data
    assert "heat" in data["risks"]
    assert "flood" in data["risks"]
    assert "air_quality" in data["risks"]
    assert "water_stress" in data["risks"]
    assert "climate_risk_score" in data
    assert "risk_level" in data
    assert 0 <= data["climate_risk_score"] <= 100
    assert data["risk_level"] in ["Low", "Moderate", "High", "Severe", "Extreme"]


def test_predict_endpoint_with_custom_features(client: TestClient):
    payload = {
        "location": "Pune",
        "custom_features": {
            "temp_c": 41.5,
            "humidity_pct": 55.0,
            "heat_index_c": 48.0,
            "precip_24h_sum_mm": 5.0,
            "precip_current_mm": 0.0,
            "aqi": 180,
            "pm2_5": 85.0,
            "wind_speed_kmh": 6.0,
            "month": 4
        }
    }

    res = client.post("/api/v1/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Pune"
    assert "hazards" in data
    assert data["hazards"]["heat"]["score"] > 70.0  # At 41.5C heat stress must be elevated
    assert data["model_version"] is not None


@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_weather")
@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_air_quality")
def test_recommendations_contract(mock_aqi, mock_weather, client: TestClient, sample_weather_raw, sample_air_quality_raw):
    mock_weather.return_value = sample_weather_raw
    mock_aqi.return_value = sample_air_quality_raw

    res = client.get("/api/v1/recommendations?location=Pune&stakeholder=municipal")
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Pune"
    assert data["stakeholder_filter"] == "municipal"
    assert "recommendations" in data
    for rec in data["recommendations"]:
        assert rec["stakeholder"] == "municipal"
        assert "title" in rec
        assert "description" in rec


@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_weather")
@patch("app.services.ingestion.open_meteo.OpenMeteoClient.fetch_current_air_quality")
def test_simulation_contract(mock_aqi, mock_weather, client: TestClient, sample_weather_raw, sample_air_quality_raw):
    mock_weather.return_value = sample_weather_raw
    mock_aqi.return_value = sample_air_quality_raw

    payload = {
        "location": "Pune",
        "ward": "Shivajinagar",
        "deltas": {
            "rainfall_pct": 30.0,
            "temperature_delta_c": 2.0,
            "aqi_pct": 10.0
        }
    }

    res = client.post("/api/v1/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["location"] == "Pune"
    assert "baseline_risk" in data
    assert "simulated_risk" in data
    assert "score_delta" in data
    assert "hazard_deltas" in data
    assert "disclaimer" in data
    assert "SCENARIO ESTIMATE" in data["disclaimer"]

