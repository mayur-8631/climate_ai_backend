"""
ClimateTwin AI — Deliverable 19: Final ML Demonstration Workflow
Module: ml_engine/demo_workflow.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026
Institute: AISSMS College of Engineering

Purpose:
Executes a comprehensive, competition-ready demonstration of the unified
ClimateTwin AI Intelligence Engine across:
1. Case Study A — Pune Pre-Monsoon Heatwave & Hydro-Climatic Water Stress (May)
2. Case Study B — Pune SW Monsoon Cloudburst & Flood-Hazard Proxy (July)
3. Case Study C — Pune Winter Inversion & CPCB Air-Quality Hazard (December)
4. Case Study D — Multi-City Generalization (Pune vs. Mumbai vs. Nagpur)
5. Case Study E — Missing Sensor Resilience & Weight Renormalization Policy
6. Case Study F — Policy & Climate Counterfactual What-If Simulations

Saves structured output to `evaluation/metrics/final_demo_outputs.json`.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from ml_engine.config import METRICS_DIR
from ml_engine.predict import (
    calculate_climate_risk_score,
    generate_complete_prediction,
    run_what_if_scenario,
)


def build_demo_scenarios() -> Dict[str, Dict[str, Any]]:
    """Return realistic, domain-grounded environmental payloads for demonstration."""
    return {
        "case_a_pune_summer_heatwave": {
            "description": "Pune Pre-Monsoon Heatwave & Soil Moisture Depletion (May)",
            "payload": {
                "location": "Pune",
                "timestamp": "2026-05-14T14:00:00",
                "temperature_c": 38.4,
                "temp_max_c": 42.6,
                "temp_min_c": 26.5,
                "humidity_pct": 28.0,
                "wind_speed_kmh": 7.5,
                "pressure_hpa": 946.5,
                "rainfall_mm": 0.0,
                "rainfall_intensity_mm_hr": 0.0,
                "soil_moisture": 0.12,
                "evapotranspiration_mm": 8.4,
                "pm25_ugm3": 58.0,
                "pm10_ugm3": 135.0,
                "no2_ugm3": 36.0,
                "so2_ugm3": 14.0,
                "co_mgm3": 1.0,
                "o3_ugm3": 78.0,
            },
            "what_if": {
                "temperature_delta_c": 2.5,
                "soil_moisture_change_percent": -20.0,
            },
        },
        "case_b_pune_monsoon_downpour": {
            "description": "Pune SW Monsoon Heavy Downpour on Saturated Soil (July)",
            "payload": {
                "location": "Pune",
                "timestamp": "2026-07-24T12:00:00",
                "temperature_c": 24.8,
                "temp_max_c": 27.6,
                "temp_min_c": 22.1,
                "humidity_pct": 92.0,
                "wind_speed_kmh": 22.0,
                "pressure_hpa": 941.0,
                "rainfall_mm": 112.0,
                "rainfall_intensity_mm_hr": 36.5,
                "cumulative_rainfall_3d_mm": 198.0,
                "cumulative_rainfall_7d_mm": 310.0,
                "soil_moisture": 0.86,
                "evapotranspiration_mm": 2.3,
                "pm25_ugm3": 18.0,
                "pm10_ugm3": 38.0,
                "no2_ugm3": 16.0,
                "so2_ugm3": 7.0,
                "co_mgm3": 0.5,
                "o3_ugm3": 24.0,
            },
            "what_if": {
                "rainfall_change_percent": 30.0,
            },
        },
        "case_c_pune_winter_inversion_smog": {
            "description": "Pune Winter Thermal Inversion & Particulate Accumulation (December)",
            "payload": {
                "location": "Pune",
                "timestamp": "2026-12-19T09:00:00",
                "temperature_c": 18.2,
                "temp_max_c": 27.4,
                "temp_min_c": 11.2,
                "humidity_pct": 64.0,
                "wind_speed_kmh": 3.2,
                "pressure_hpa": 954.0,
                "rainfall_mm": 0.0,
                "rainfall_intensity_mm_hr": 0.0,
                "soil_moisture": 0.34,
                "evapotranspiration_mm": 3.4,
                "pm25_ugm3": 154.0,
                "pm10_ugm3": 288.0,
                "no2_ugm3": 88.0,
                "so2_ugm3": 29.0,
                "co_mgm3": 2.4,
                "o3_ugm3": 52.0,
                "measured_aqi": 326.0,
            },
            "what_if": {
                "pm25_change_percent": -35.0,
                "pm10_change_percent": -35.0,
            },
        },
    }


def run_demonstration_workflow() -> Dict[str, Any]:
    """Execute all competition demonstration scenarios and print a formatted summary."""
    scenarios = build_demo_scenarios()
    demo_results: Dict[str, Any] = {"case_studies": {}, "multi_city": {}, "missing_hazard_policy": {}}

    print("=" * 84)
    print("CLIMATETWIN AI — FINAL ML INTELLIGENCE ENGINE DEMONSTRATION")
    print("Owner: Lokesh Joshi (AI/ML Lead) | Team PrithviNex | PCCOE Grand Challenge 2026")
    print("=" * 84)

    for key, item in scenarios.items():
        res = generate_complete_prediction(item["payload"], scenario=item["what_if"])
        demo_results["case_studies"][key] = {
            "description": item["description"],
            "result": res,
        }
        r = res["risks"]
        w = res["what_if"]
        top_factors = [
            f"{f['feature']} ({f['effect']}, {f['contribution_points']:+.1f} pts)"
            for f in res["explainability"]["explanation"]["primary_factors"][:3]
        ]
        print(f"\n[{item['description']}]")
        print(
            f"  Hazards (0-100) -> Heat: {r['heat']:5.2f} | Flood: {r['flood']:5.2f} | "
            f"Air Quality: {r['air_quality']:5.2f} | Water Stress: {r['water_stress']:5.2f}"
        )
        print(
            f"  Composite Climate Risk Score: {res['climate_risk_score']:5.2f}/100 "
            f"({res['risk_level']}) | Coverage: {res['data_coverage']:.0f}%"
        )
        print(f"  Top XAI Drivers: {', '.join(top_factors)}")
        print(
            f"  What-If {item['what_if']}: {w['baseline_score']:.2f} ({w['baseline_risk_level']}) "
            f"-> {w['scenario_score']:.2f} ({w['scenario_risk_level']}) "
            f"[Delta: {w['change']:+.2f} pts / {w['change_percentage']:+.2f}%]"
        )

    # Multi-city demonstration (Pune vs Mumbai vs Nagpur)
    city_payloads: List[Dict[str, Any]] = [
        {
            "location": "Pune",
            "timestamp": "2026-06-18T12:00:00",
            "temperature_c": 29.0,
            "humidity_pct": 78.0,
            "rainfall_mm": 65.0,
            "pm25_ugm3": 32.0,
        },
        {
            "location": "Mumbai",
            "timestamp": "2026-06-18T12:00:00",
            "temperature_c": 30.5,
            "humidity_pct": 88.0,
            "rainfall_mm": 145.0,
            "pm25_ugm3": 42.0,
        },
        {
            "location": "Nagpur",
            "timestamp": "2026-06-18T12:00:00",
            "temperature_c": 39.2,
            "humidity_pct": 34.0,
            "rainfall_mm": 2.0,
            "pm25_ugm3": 64.0,
        },
    ]
    print("\n[Multi-City Generalization Check (2026-06-18)]")
    for cp in city_payloads:
        c_res = generate_complete_prediction(cp, include_explainability=False)
        demo_results["multi_city"][cp["location"]] = c_res
        print(
            f"  {cp['location']:8s} -> Score: {c_res['climate_risk_score']:5.2f} ({c_res['risk_level']:8s}) | "
            f"Heat: {c_res['risks']['heat']:5.2f}, Flood: {c_res['risks']['flood']:5.2f}, "
            f"AQ: {c_res['risks']['air_quality']:5.2f}, Water: {c_res['risks']['water_stress']:5.2f}"
        )

    # Missing-hazard renormalization check
    partial_risk = calculate_climate_risk_score(
        {"heat": 74.0, "flood": None, "air_quality": 52.0, "water_stress": 68.0}
    )
    demo_results["missing_hazard_policy"] = partial_risk
    print("\n[Missing-Hazard Policy Verification (Flood sensor offline -> None)]")
    print(
        f"  Score: {partial_risk['climate_risk_score']:.2f} ({partial_risk['risk_level']}) | "
        f"Coverage: {partial_risk['data_coverage']:.1f}% | "
        f"Effective Weights: {partial_risk['effective_weights']}"
    )
    print("=" * 84)

    out_path: Path = METRICS_DIR / "final_demo_outputs.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(demo_results, f, indent=2)

    return demo_results


if __name__ == "__main__":
    run_demonstration_workflow()

