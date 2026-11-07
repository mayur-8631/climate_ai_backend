from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Body
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.services.preprocessing.cleaner import DataCleaner
from app.services.preprocessing.feature_pipeline import FeaturePipeline
from app.services.ml_bridge.model_registry import registry
from app.api.v1.endpoints.weather import resolve_coordinates

router = APIRouter()
open_meteo_client = OpenMeteoClient()


@router.post("", response_model=PredictionResponse)
async def run_hazard_predictions(
    payload: Optional[PredictionRequest] = Body(default=None),
    location: str = Query("Pune"),
    ward: Optional[str] = Query(None)
):
    """
    Run hazard-specific ML prediction modules (Heat, Flood, Air Quality, Water Stress).
    Can ingest live telemetry or accept customized simulation features.
    """
    target_loc = payload.location if payload and payload.location else location
    target_ward = payload.ward if payload and payload.ward else ward
    lat_req = payload.latitude if payload else None
    lon_req = payload.longitude if payload else None

    lat, lon, resolved_ward = resolve_coordinates(target_ward, lat_req, lon_req)

    # 1. If explicit custom features are provided, use them directly
    if payload and payload.custom_features:
        features = payload.custom_features
    else:
        # 2. Ingest live environmental streams to formulate feature vectors
        try:
            raw_weather = await open_meteo_client.fetch_current_weather(latitude=lat, longitude=lon)
            raw_aqi = await open_meteo_client.fetch_current_air_quality(latitude=lat, longitude=lon)

            clean_w = DataCleaner.clean_weather_payload(raw_weather, location_name=target_loc, ward=resolved_ward)
            clean_aq = DataCleaner.clean_air_quality_payload(raw_aqi, location_name=target_loc, ward=resolved_ward)

            features = FeaturePipeline.extract_features(clean_w, clean_aq)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Feature extraction failed: {str(e)}")

    # 3. Execute ML model predictions
    predictions = registry.run_all_hazard_predictions(
        features=features,
        location=target_loc,
        ward=resolved_ward
    )

    return predictions

