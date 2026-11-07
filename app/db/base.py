from app.db.session import Base
from app.db.models.location import Location
from app.db.models.observation import WeatherObservation, AirQualityObservation
from app.db.models.prediction import HazardPredictionRecord, RiskAssessmentRecord
from app.db.models.recommendation import RecommendationRecord

__all__ = [
    "Base",
    "Location",
    "WeatherObservation",
    "AirQualityObservation",
    "HazardPredictionRecord",
    "RiskAssessmentRecord",
    "RecommendationRecord",
]

