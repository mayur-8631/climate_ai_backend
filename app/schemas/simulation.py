from typing import Dict, Optional
from pydantic import BaseModel, Field
from app.schemas.risk_score import RiskScoreResponse, RisksBreakdown


class SimulationDeltas(BaseModel):
    rainfall_pct: float = Field(default=0.0, ge=-100.0, le=500.0, description="Percentage change in rainfall, e.g. +30.0%")
    temperature_delta_c: float = Field(default=0.0, ge=-10.0, le=15.0, description="Temperature increment in Celsius, e.g. +2.0C")
    aqi_pct: float = Field(default=0.0, ge=-100.0, le=300.0, description="Percentage change in AQI / pollutant levels")
    impervious_surface_delta_pct: float = Field(default=0.0, ge=-50.0, le=50.0, description="Urban density / concrete runoff delta")


class SimulationRequest(BaseModel):
    location: str = "Pune"
    ward: Optional[str] = None
    deltas: SimulationDeltas


class SimulationResponse(BaseModel):
    location: str
    ward: Optional[str] = None
    baseline_risk: RiskScoreResponse
    simulated_risk: RiskScoreResponse
    score_delta: int = Field(..., description="Change in Climate Risk Score (e.g. +8 points)")
    hazard_deltas: Dict[str, float] = Field(..., description="Delta for each hazard component")
    scenario_summary: str = Field(..., description="Human-readable explanation of simulation outcome")
    disclaimer: str = Field(
        default="SCENARIO ESTIMATE: These values are simulated projections based on perturbation modeling and do not constitute guaranteed weather forecasts."
    )

