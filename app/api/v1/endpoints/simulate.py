from typing import Optional
from fastapi import APIRouter, Body, HTTPException
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.services.preprocessing.cleaner import DataCleaner
from app.services.preprocessing.normalizer import EnvironmentalNormalizer
from app.services.preprocessing.feature_pipeline import FeaturePipeline
from app.services.ml_bridge.model_registry import registry
from app.services.risk_engine.calculator import ClimateRiskEngine
from app.api.v1.endpoints.weather import resolve_coordinates

router = APIRouter()
open_meteo_client = OpenMeteoClient()


@router.post("", response_model=SimulationResponse)
async def simulate_what_if_scenario(payload: SimulationRequest = Body(...)):
    """
    Simulate what-if climate scenarios (e.g. +30% rainfall, +2.5°C temperature rise)
    and compute projected shifts in localized risk scores.
    """
    lat, lon, resolved_ward = resolve_coordinates(payload.ward)

    try:
        raw_weather = await open_meteo_client.fetch_current_weather(latitude=lat, longitude=lon)
        raw_aqi = await open_meteo_client.fetch_current_air_quality(latitude=lat, longitude=lon)

        clean_w = DataCleaner.clean_weather_payload(raw_weather, location_name=payload.location, ward=resolved_ward)
        clean_aq = DataCleaner.clean_air_quality_payload(raw_aqi, location_name=payload.location, ward=resolved_ward)

        # Baseline features & risk
        base_features = FeaturePipeline.extract_features(clean_w, clean_aq)
        base_pred = registry.run_all_hazard_predictions(base_features, location=payload.location, ward=resolved_ward)
        baseline_risk = ClimateRiskEngine.build_risk_response(
            location=payload.location,
            ward=resolved_ward,
            temperature=clean_w.current.temperature,
            rainfall=base_features.get("precip_24h_sum_mm"),
            aqi=clean_aq.current.aqi,
            hazards=base_pred.hazards,
            provenance=clean_w.provenance
        )

        # Perturb features according to deltas
        sim_features = dict(base_features)

        # Temperature delta
        if payload.deltas.temperature_delta_c != 0.0:
            sim_features["temp_c"] += payload.deltas.temperature_delta_c
            sim_features["heat_index_c"] = EnvironmentalNormalizer.calculate_heat_index(
                sim_features["temp_c"], sim_features["humidity_pct"]
            )

        # Rainfall delta (%)
        if payload.deltas.rainfall_pct != 0.0:
            multiplier = 1.0 + (payload.deltas.rainfall_pct / 100.0)
            sim_features["precip_24h_sum_mm"] = max(0.0, sim_features["precip_24h_sum_mm"] * multiplier)
            sim_features["precip_current_mm"] = max(0.0, sim_features["precip_current_mm"] * multiplier)

        # AQI delta (%)
        if payload.deltas.aqi_pct != 0.0:
            aqi_mult = 1.0 + (payload.deltas.aqi_pct / 100.0)
            sim_features["aqi"] = int(max(0, sim_features["aqi"] * aqi_mult))
            sim_features["pm2_5"] = max(0.0, sim_features["pm2_5"] * aqi_mult)

        # Run simulated predictions
        sim_pred = registry.run_all_hazard_predictions(sim_features, location=payload.location, ward=resolved_ward)
        simulated_risk = ClimateRiskEngine.build_risk_response(
            location=payload.location,
            ward=resolved_ward,
            temperature=sim_features["temp_c"],
            rainfall=sim_features["precip_24h_sum_mm"],
            aqi=sim_features["aqi"],
            hazards=sim_pred.hazards,
            provenance=clean_w.provenance
        )

        score_delta = simulated_risk.climate_risk_score - baseline_risk.climate_risk_score

        hazard_deltas = {
            "heat": round(simulated_risk.risks.heat - baseline_risk.risks.heat, 1),
            "flood": round(simulated_risk.risks.flood - baseline_risk.risks.flood, 1),
            "air_quality": round(simulated_risk.risks.air_quality - baseline_risk.risks.air_quality, 1),
            "water_stress": round(simulated_risk.risks.water_stress - baseline_risk.risks.water_stress, 1)
        }

        # Compose summary explanation
        summary_parts = []
        if payload.deltas.rainfall_pct > 0:
            summary_parts.append(f"A {payload.deltas.rainfall_pct}% increase in rainfall shifts flood risk by {hazard_deltas['flood']:+} pts.")
        if payload.deltas.temperature_delta_c > 0:
            summary_parts.append(f"A +{payload.deltas.temperature_delta_c}°C warming anomaly elevates heat stress risk by {hazard_deltas['heat']:+} pts.")
        if payload.deltas.aqi_pct > 0:
            summary_parts.append(f"A {payload.deltas.aqi_pct}% increase in AQI raises air quality risk by {hazard_deltas['air_quality']:+} pts.")

        summary_text = " ".join(summary_parts) if summary_parts else "No significant parameter changes applied."

        return SimulationResponse(
            location=payload.location,
            ward=resolved_ward,
            baseline_risk=baseline_risk,
            simulated_risk=simulated_risk,
            score_delta=score_delta,
            hazard_deltas=hazard_deltas,
            scenario_summary=summary_text
        )

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Simulation calculation failed: {str(e)}")

