from typing import Optional, List
import asyncio
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.prediction import RiskAssessmentRecord
from app.schemas.risk_score import RiskScoreResponse, WardRiskMapPoint, WardsRiskMapResponse, RiskLevel
from app.schemas.common import Coordinates
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.services.preprocessing.cleaner import DataCleaner
from app.services.preprocessing.feature_pipeline import FeaturePipeline
from app.services.ml_bridge.model_registry import registry
from app.services.risk_engine.calculator import ClimateRiskEngine
from app.api.v1.endpoints.weather import resolve_coordinates
from app.api.v1.endpoints.locations import PUNE_LOCATION

router = APIRouter()
open_meteo_client = OpenMeteoClient()


def get_marker_color(risk_level: RiskLevel) -> str:
    if risk_level == RiskLevel.LOW:
        return "#22C55E"
    elif risk_level == RiskLevel.MODERATE:
        return "#F59E0B"
    elif risk_level == RiskLevel.HIGH:
        return "#EF4444"
    elif risk_level == RiskLevel.SEVERE:
        return "#DC2626"
    return "#7F1D1D"


def determine_primary_hazard(risks) -> str:
    h_map = {
        "Heat": risks.heat,
        "Flood": risks.flood,
        "Air Quality": risks.air_quality,
        "Water Stress": risks.water_stress
    }
    return max(h_map, key=h_map.get)


async def _evaluate_single_ward(ward) -> Optional[WardRiskMapPoint]:
    lat = ward.coordinates.latitude
    lon = ward.coordinates.longitude
    try:
        raw_weather = await open_meteo_client.fetch_current_weather(latitude=lat, longitude=lon)
        raw_aqi = await open_meteo_client.fetch_current_air_quality(latitude=lat, longitude=lon)

        clean_w = DataCleaner.clean_weather_payload(raw_weather, location_name="Pune", ward=ward.name)
        clean_aq = DataCleaner.clean_air_quality_payload(raw_aqi, location_name="Pune", ward=ward.name)

        features = FeaturePipeline.extract_features(clean_w, clean_aq)
        predictions = registry.run_all_hazard_predictions(features, location="Pune", ward=ward.name)

        risk_resp = ClimateRiskEngine.build_risk_response(
            location="Pune",
            ward=ward.name,
            temperature=clean_w.current.temperature,
            rainfall=features.get("precip_24h_sum_mm"),
            aqi=clean_aq.current.aqi,
            hazards=predictions.hazards,
            provenance=clean_w.provenance
        )

        primary_h = determine_primary_hazard(risk_resp.risks)
        marker_c = get_marker_color(risk_resp.risk_level)

        return WardRiskMapPoint(
            ward_code=ward.ward_code,
            name=ward.name,
            coordinates=ward.coordinates,
            elevation_m=ward.elevation_m,
            climate_risk_score=risk_resp.climate_risk_score,
            risk_level=risk_resp.risk_level,
            marker_color=marker_c,
            primary_hazard=primary_h,
            temperature=risk_resp.temperature,
            rainfall=risk_resp.rainfall,
            aqi=risk_resp.aqi,
            risks=risk_resp.risks
        )
    except Exception:
        return None


@router.get("/map", response_model=WardsRiskMapResponse)
async def get_wards_risk_map():
    """
    Returns real-time risk scores, primary hazard drivers, and color codes
    for all 6 Pune micro-wards simultaneously for Pravin's Leaflet interactive map.
    """
    now = datetime.now(timezone.utc)
    results = await asyncio.gather(*[_evaluate_single_ward(w) for w in PUNE_LOCATION.wards])
    ward_points = [p for p in results if p is not None]

    total_score = sum(p.climate_risk_score for p in ward_points)
    city_avg = int(round(total_score / len(ward_points))) if ward_points else 30

    return WardsRiskMapResponse(
        city="Pune",
        state="Maharashtra",
        country="India",
        centroid=PUNE_LOCATION.coordinates,
        timestamp=now,
        total_wards=len(ward_points),
        citywide_average_risk=city_avg,
        wards=ward_points
    )


@router.get("", response_model=RiskScoreResponse)
async def get_climate_risk_score(
    location: str = Query("Pune", description="Pilot city name"),
    ward: Optional[str] = Query(None, description="Specific ward, e.g., Shivajinagar, Kothrud, Hadapsar"),
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
):
    """
    Flagship Climate Risk Score calculation for ClimateTwin AI.
    Combines live multi-source environmental telemetry, ML hazard inferences,
    and returns the standardized risk contract for Pravin's Next.js dashboard.
    """
    lat, lon, resolved_ward = resolve_coordinates(ward, latitude, longitude)

    try:
        raw_weather = await open_meteo_client.fetch_current_weather(latitude=lat, longitude=lon)
        raw_aqi = await open_meteo_client.fetch_current_air_quality(latitude=lat, longitude=lon)

        clean_w = DataCleaner.clean_weather_payload(raw_weather, location_name=location, ward=resolved_ward)
        clean_aq = DataCleaner.clean_air_quality_payload(raw_aqi, location_name=location, ward=resolved_ward)

        features = FeaturePipeline.extract_features(clean_w, clean_aq)
        predictions = registry.run_all_hazard_predictions(features, location=location, ward=resolved_ward)

        risk_response = ClimateRiskEngine.build_risk_response(
            location=location,
            ward=resolved_ward,
            temperature=clean_w.current.temperature,
            rainfall=features.get("precip_24h_sum_mm"),
            aqi=clean_aq.current.aqi,
            hazards=predictions.hazards,
            provenance=clean_w.provenance
        )

        # Store assessment in database
        db_record = RiskAssessmentRecord(
            location_name=location,
            ward_name=resolved_ward,
            climate_risk_score=risk_response.climate_risk_score,
            risk_level=risk_response.risk_level.value,
            temperature_observed=risk_response.temperature,
            rainfall_observed=risk_response.rainfall,
            aqi_observed=risk_response.aqi,
            heat_risk=risk_response.risks.heat,
            flood_risk=risk_response.risks.flood,
            air_quality_risk=risk_response.risks.air_quality,
            water_stress_risk=risk_response.risks.water_stress,
            is_simulation=False
        )
        db.add(db_record)
        db.commit()

        return risk_response

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Failed to calculate climate risk score: {str(e)}")

