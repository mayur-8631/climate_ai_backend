from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Boolean
from app.db.session import Base


class HazardPredictionRecord(Base):
    __tablename__ = "hazard_predictions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_name = Column(String(100), nullable=False, index=True)
    ward_name = Column(String(100), nullable=True)
    evaluated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    model_version = Column(String(50), nullable=False)
    inference_mode = Column(String(50), nullable=False)

    heat_score = Column(Float, nullable=False)
    flood_score = Column(Float, nullable=False)
    air_quality_score = Column(Float, nullable=False)
    water_stress_score = Column(Float, nullable=False)

    feature_contributions = Column(JSON, nullable=True)


class RiskAssessmentRecord(Base):
    __tablename__ = "climate_risk_assessments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_name = Column(String(100), nullable=False, index=True)
    ward_name = Column(String(100), nullable=True)
    calculated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    climate_risk_score = Column(Integer, nullable=False)
    risk_level = Column(String(50), nullable=False)

    temperature_observed = Column(Float, nullable=True)
    rainfall_observed = Column(Float, nullable=True)
    aqi_observed = Column(Integer, nullable=True)

    heat_risk = Column(Float, nullable=False)
    flood_risk = Column(Float, nullable=False)
    air_quality_risk = Column(Float, nullable=False)
    water_stress_risk = Column(Float, nullable=False)

    is_simulation = Column(Boolean, default=False)

