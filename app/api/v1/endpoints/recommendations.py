from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.recommendation import RecommendationsResponse, StakeholderType
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.services.preprocessing.cleaner import DataCleaner
from app.services.preprocessing.feature_pipeline import FeaturePipeline
from app.services.ml_bridge.model_registry import registry
from app.services.risk_engine.calculator import ClimateRiskEngine
from app.services.recommendation.engine import RecommendationEngine
from app.api.v1.endpoints.weather import resolve_coordinates

router = APIRouter()
open_meteo_client = OpenMeteoClient()


@router.get("", response_model=RecommendationsResponse)
async def get_stakeholder_recommendations(
    location: str = Query("Pune", description="Pilot city name"),
    ward: Optional[str] = Query(None),
    stakeholder: StakeholderType = Query(StakeholderType.ALL, description="Filter by stakeholder"),
    db: Session = Depends(get_db)
):
    """
    Return targeted, actionable climate adaptation recommendations for specific stakeholders.
    """
    lat, lon, resolved_ward = resolve_coordinates(ward)

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

        recommendations = RecommendationEngine.generate_recommendations(
            risk=risk_response,
            stakeholder_filter=stakeholder
        )

        return recommendations
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to generate recommendations: {str(e)}")

