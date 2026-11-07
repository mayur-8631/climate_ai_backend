from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import Coordinates, Provenance


class PollutantDetail(BaseModel):
    value: Optional[float] = Field(None, description="Concentration value (null if not measured)")
    unit: str = "ug/m3"
    status: str = "MEASURED"  # MEASURED, ESTIMATED, UNAVAILABLE


class AirQualityCurrent(BaseModel):
    aqi: Optional[int] = Field(None, ge=0, description="Calculated Air Quality Index")
    category: str = Field(..., description="Good, Moderate, Unhealthy for Sensitive Groups, Unhealthy, Very Unhealthy, Hazardous")
    dominant_pollutant: Optional[str] = Field(None, description="Primary pollutant responsible for AQI")
    pm2_5: PollutantDetail
    pm10: PollutantDetail
    no2: PollutantDetail
    so2: PollutantDetail
    co: PollutantDetail
    o3: PollutantDetail


class AirQualityHourlyPoint(BaseModel):
    timestamp: datetime
    aqi: Optional[int] = None
    pm2_5: Optional[float] = None
    pm10: Optional[float] = None
    no2: Optional[float] = None


class AirQualityResponse(BaseModel):
    location: str
    ward: Optional[str] = None
    coordinates: Coordinates
    observed_at: datetime
    provenance: Provenance
    current: AirQualityCurrent
    hourly_trend: Optional[List[AirQualityHourlyPoint]] = None

