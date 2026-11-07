from typing import Generic, Optional, TypeVar, Any
from datetime import datetime, timezone
from enum import Enum
from pydantic import BaseModel, Field


class DataQuality(str, Enum):
    EXCELLENT = "EXCELLENT"      # Ground-validated or high-precision multi-sensor match
    GOOD = "GOOD"                # Standard API stream with all fields present
    DEGRADED = "DEGRADED"        # Non-critical fields missing, fallback used
    MISSING_SOURCE = "MISSING_SOURCE"  # Sensor/API failed; explicit nulls recorded


class Coordinates(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Longitude in decimal degrees")


class LocationMeta(BaseModel):
    name: str = Field(..., description="Location name, e.g., Pune")
    ward: Optional[str] = Field(None, description="Ward or sub-region, e.g., Shivajinagar")
    coordinates: Coordinates
    elevation: Optional[float] = Field(None, description="Elevation in meters above sea level")


class Provenance(BaseModel):
    source: str = Field(..., description="Data provider or sensor network name")
    observed_at: datetime = Field(..., description="Observation timestamp in UTC")
    ingested_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    quality_flag: DataQuality = Field(default=DataQuality.GOOD)


T = TypeVar("T")


class StandardResponse(BaseModel, Generic[T]):
    success: bool = True
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: Optional[T] = None
    meta: Optional[dict[str, Any]] = None
    error: Optional[str] = None

