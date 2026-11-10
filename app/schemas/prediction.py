from typing import Dict, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class HazardDetail(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Hazard-specific risk score from 0 (negligible) to 100 (extreme)")
    status: str = Field(default="AVAILABLE", description="AVAILABLE or UNAVAILABLE")
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Model prediction confidence metric")
    primary_driver: str = Field(..., description="Key environmental driver, e.g. 'Sustained temperature above 40C'")
    feature_contributions: Optional[Dict[str, float]] = Field(default=None, description="SHAP or feature importance breakdown")


class HazardPredictions(BaseModel):
    heat: HazardDetail
    flood: HazardDetail
    air_quality: HazardDetail
    water_stress: HazardDetail


class PredictionRequest(BaseModel):
    location: str = "Pune"
    ward: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    custom_features: Optional[Dict[str, float]] = None


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    location: str
    ward: Optional[str] = None
    evaluated_at: datetime
    prediction_horizon: str = "24h"
    hazards: HazardPredictions
    model_version: str = "1.0.0-rf-baseline"
    inference_mode: str = Field(default="ml_trained", description="ml_trained or calibrated_heuristic")

