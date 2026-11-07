from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from app.schemas.common import Provenance, Coordinates


class RiskLevel(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"
    SEVERE = "Severe"
    EXTREME = "Extreme"


class RisksBreakdown(BaseModel):
    heat: float = Field(..., ge=0.0, le=100.0, description="Heat hazard risk (0-100)")
    flood: float = Field(..., ge=0.0, le=100.0, description="Flood hazard risk (0-100)")
    air_quality: float = Field(..., ge=0.0, le=100.0, description="Air quality hazard risk (0-100)")
    water_stress: float = Field(..., ge=0.0, le=100.0, description="Water stress hazard risk (0-100)")


class RiskScoreResponse(BaseModel):
    location: str
    ward: Optional[str] = None
    temperature: Optional[float] = Field(None, description="Observed current temperature in Celsius")
    rainfall: Optional[float] = Field(None, description="Observed 24h precipitation in mm")
    aqi: Optional[int] = Field(None, description="Observed AQI")
    risks: RisksBreakdown
    climate_risk_score: int = Field(..., ge=0, le=100, description="Composite Climate Risk Score (0-100)")
    risk_level: RiskLevel = Field(..., description="Categorical risk tier: Low, Moderate, High, Severe, Extreme")
    breakdown_weights: Dict[str, float] = Field(
        default_factory=lambda: {"heat": 0.30, "flood": 0.30, "air_quality": 0.20, "water_stress": 0.20}
    )
    provenance: Optional[Provenance] = None


class WardRiskMapPoint(BaseModel):
    ward_code: str
    name: str
    coordinates: Coordinates
    elevation_m: float
    climate_risk_score: int
    risk_level: RiskLevel
    marker_color: str = Field(..., description="Hex color: #22C55E (Low), #F59E0B (Moderate), #EF4444 (High), #7F1D1D (Extreme)")
    primary_hazard: str
    temperature: Optional[float] = None
    rainfall: Optional[float] = None
    aqi: Optional[int] = None
    risks: RisksBreakdown


class WardsRiskMapResponse(BaseModel):
    city: str = "Pune"
    state: str = "Maharashtra"
    country: str = "India"
    centroid: Coordinates
    timestamp: datetime
    total_wards: int
    citywide_average_risk: int
    wards: List[WardRiskMapPoint]

