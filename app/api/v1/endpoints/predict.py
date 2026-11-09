from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Query, Body
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.services.preprocessing.cleaner import DataCleaner
from app.services.preprocessing.feature_pipeline import FeaturePipeline
from app.services.ml_bridge.model_registry import registry
from app.api.v1.endpoints.weather import resolve_coordinates
from ml_engine.predict import generate_complete_prediction

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


@router.post("/intelligence", response_model=Dict[str, Any])
async def run_complete_ml_intelligence(
    environmental_data: Dict[str, Any] = Body(...),
    scenario: Optional[Dict[str, Any]] = Body(default=None),
):
    """
    Execute Lokesh Joshi's unified ClimateTwin AI Intelligence Engine (`ml_engine.predict.generate_complete_prediction`),
    returning multi-hazard predictions, localized Climate Risk Score (0-100), XAI attributions,
    What-If counterfactual simulation, and stakeholder recommendations.
    """
    try:
        return generate_complete_prediction(environmental_data, scenario=scenario)
    except ValueError as err:
        raise HTTPException(status_code=422, detail=str(err))
    except Exception as err:
        raise HTTPException(status_code=500, detail=f"ML Intelligence Engine error: {str(err)}")

