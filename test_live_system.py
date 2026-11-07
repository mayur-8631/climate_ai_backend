"""
ClimateTwin AI - End-to-End System Test Script
Run this script to test all backend subsystems, ML inferences, and API contracts.
Usage:
    python test_live_system.py
"""

import sys
import json
from fastapi.testclient import TestClient
from app.main import app

def print_separator(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def run_tests():
    client = TestClient(app)
    
    # 1. Health Check
    print_separator("1. SYSTEM HEALTH CHECK")
    res = client.get("/health")
    print(f"Status Code: {res.status_code}")
    print(f"Response: {json.dumps(res.json(), indent=2)}")
    assert res.status_code == 200

    # 2. Supported Locations & Wards
    print_separator("2. LOCATIONS & MICRO-WARDS (Pune Pilot)")
    res = client.get("/api/v1/locations")
    print(f"Status Code: {res.status_code}")
    locations = res.json()
    pune = locations[0]
    print(f"City: {pune['city']}, State: {pune['state']}")
    print("Configured Wards:")
    for w in pune["wards"]:
        print(f" - [{w['ward_code']}] {w['name']} (Lat: {w['coordinates']['latitude']}, Lon: {w['coordinates']['longitude']})")
    assert len(pune["wards"]) >= 6

    # 3. Weather Ingestion
    print_separator("3. WEATHER INGESTION (/api/v1/weather)")
    res = client.get("/api/v1/weather?location=Pune&ward=Shivajinagar")
    print(f"Status Code: {res.status_code}")
    w_data = res.json()
    print(f"Location: {w_data['location']} ({w_data['ward']})")
    print(f"Data Source: {w_data['provenance']['source']}")
    print(f"Observation Time: {w_data['observed_at']}")
    print(f"Quality Flag: {w_data['provenance']['quality_flag']}")
    print(f"Temperature: {w_data['current']['temperature']} °C")
    print(f"Relative Humidity: {w_data['current']['relative_humidity']} %")
    print(f"Precipitation: {w_data['current']['precipitation']} mm")
    print(f"Wind Speed: {w_data['current']['wind_speed']} km/h")
    assert res.status_code == 200

    # 4. Air Quality Ingestion
    print_separator("4. AIR QUALITY INGESTION (/api/v1/air-quality)")
    res = client.get("/api/v1/air-quality?location=Pune&ward=Shivajinagar")
    print(f"Status Code: {res.status_code}")
    aq_data = res.json()
    print(f"Location: {aq_data['location']} ({aq_data['ward']})")
    print(f"Data Source: {aq_data['provenance']['source']}")
    print(f"AQI: {aq_data['current']['aqi']} ({aq_data['current']['category']})")
    print(f"Dominant Pollutant: {aq_data['current']['dominant_pollutant']}")
    print(f"PM2.5: {aq_data['current']['pm2_5']['value']} ug/m3")
    print(f"PM10: {aq_data['current']['pm10']['value']} ug/m3")
    assert res.status_code == 200

    # 5. ML Hazard Predictions
    print_separator("5. ML HAZARD PREDICTIONS (/api/v1/predict)")
    res = client.post("/api/v1/predict?location=Pune&ward=Shivajinagar")
    print(f"Status Code: {res.status_code}")
    pred_data = res.json()
    print(f"Inference Mode: {pred_data['inference_mode']}")
    print(f"Model Version: {pred_data['model_version']}")
    print("Hazard Breakdown:")
    for hazard, detail in pred_data["hazards"].items():
        print(f" - {hazard.upper():12}: Score = {detail['score']:5.1f} | Driver = {detail['primary_driver']}")
    assert res.status_code == 200

    # 6. Flagship Climate Risk Score
    print_separator("6. FLAGSHIP CLIMATE RISK SCORE (/api/v1/risk-score)")
    res = client.get("/api/v1/risk-score?location=Pune&ward=Shivajinagar")
    print(f"Status Code: {res.status_code}")
    risk_data = res.json()
    print(f"Location: {risk_data['location']} ({risk_data['ward']})")
    print(f"Temperature: {risk_data['temperature']} °C")
    print(f"Rainfall (24h): {risk_data['rainfall']} mm")
    print(f"AQI: {risk_data['aqi']}")
    print(f"Risks -> Heat: {risk_data['risks']['heat']}, Flood: {risk_data['risks']['flood']}, AQ: {risk_data['risks']['air_quality']}, Water: {risk_data['risks']['water_stress']}")
    print(f"\n>>> COMPOSITE CLIMATE RISK SCORE: {risk_data['climate_risk_score']} / 100 <<<")
    print(f">>> RISK CATEGORY: {risk_data['risk_level']} <<<")
    assert res.status_code == 200

    # 7. Multi-Ward Interactive Map API
    print_separator("7. MULTI-WARD RISK MAP (/api/v1/risk-score/map)")
    res = client.get("/api/v1/risk-score/map")
    print(f"Status Code: {res.status_code}")
    map_data = res.json()
    print(f"City: {map_data['city']} | Total Wards: {map_data['total_wards']} | Citywide Avg Risk: {map_data['citywide_average_risk']}")
    for w in map_data["wards"]:
        print(f" - [{w['ward_code']}] {w['name']:20} -> Score: {w['climate_risk_score']:2d} ({w['risk_level']:8}) | Marker: {w['marker_color']} | Primary: {w['primary_hazard']}")
    assert res.status_code == 200

    # 8. Stakeholder Recommendations
    print_separator("8. STAKEHOLDER RECOMMENDATIONS (/api/v1/recommendations)")
    res = client.get("/api/v1/recommendations?location=Pune&stakeholder=municipal")
    print(f"Status Code: {res.status_code}")
    recs = res.json()
    print(f"Total Municipal Actions Generated: {recs['total_recommendations']}")
    for r in recs["recommendations"]:
        print(f" - [{r['urgency']}] {r['title']}")
        print(f"   Impact: {r['estimated_impact']}")
    assert res.status_code == 200

    # 9. What-If Climate Simulation
    print_separator("9. WHAT-IF CLIMATE SIMULATION (/api/v1/simulate)")
    sim_payload = {
        "location": "Pune",
        "ward": "Shivajinagar",
        "deltas": {
            "rainfall_pct": 30.0,
            "temperature_delta_c": 2.5
        }
    }
    res = client.post("/api/v1/simulate", json=sim_payload)
    print(f"Status Code: {res.status_code}")
    sim_data = res.json()
    print(f"Baseline Score:  {sim_data['baseline_risk']['climate_risk_score']}")
    print(f"Simulated Score: {sim_data['simulated_risk']['climate_risk_score']} (Delta: {sim_data['score_delta']:+d} pts)")
    print(f"Hazard Shifts:   {sim_data['hazard_deltas']}")
    print(f"Summary:         {sim_data['scenario_summary']}")
    print(f"Disclaimer:      {sim_data['disclaimer']}")
    assert res.status_code == 200

    print("\n" + "=" * 65)
    print(" ALL BACKEND SUBSYSTEM TESTS COMPLETED SUCCESSFULLY! ")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_tests()

