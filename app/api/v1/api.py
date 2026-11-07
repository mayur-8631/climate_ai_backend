from fastapi import APIRouter
from app.api.v1.endpoints import (
    locations,
    weather,
    air_quality,
    predict,
    risk_score,
    history,
    recommendations,
    simulate
)

api_router = APIRouter()

api_router.include_router(locations.router, prefix="/locations", tags=["Locations & Wards"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather Ingestion"])
api_router.include_router(air_quality.router, prefix="/air-quality", tags=["Air Quality Ingestion"])
api_router.include_router(predict.router, prefix="/predict", tags=["Hazard ML Predictions"])
api_router.include_router(risk_score.router, prefix="/risk-score", tags=["Climate Risk Score Engine"])
api_router.include_router(history.router, prefix="/history", tags=["Historical Climate Baselines"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["Actionable Recommendations"])
api_router.include_router(simulate.router, prefix="/simulate", tags=["What-If Climate Simulation"])

