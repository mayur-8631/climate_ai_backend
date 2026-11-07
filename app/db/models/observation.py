from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
from app.db.session import Base


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_name = Column(String(100), nullable=False, index=True)
    ward_name = Column(String(100), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observed_at = Column(DateTime, nullable=False, index=True)
    ingested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(String(100), nullable=False)
    quality_flag = Column(String(50), nullable=False, default="GOOD")

    # Environmental metrics (Explicitly Nullable - never fake 0!)
    temperature_c = Column(Float, nullable=True)
    relative_humidity_pct = Column(Float, nullable=True)
    precipitation_mm = Column(Float, nullable=True)
    rain_mm = Column(Float, nullable=True)
    wind_speed_kmh = Column(Float, nullable=True)
    surface_pressure_hpa = Column(Float, nullable=True)
    cloud_cover_pct = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)

    raw_payload = Column(JSON, nullable=True)


class AirQualityObservation(Base):
    __tablename__ = "air_quality_observations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    location_name = Column(String(100), nullable=False, index=True)
    ward_name = Column(String(100), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    observed_at = Column(DateTime, nullable=False, index=True)
    ingested_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    source = Column(String(100), nullable=False)
    quality_flag = Column(String(50), nullable=False, default="GOOD")

    # Pollutant metrics (Explicitly Nullable)
    aqi_value = Column(Integer, nullable=True)
    aqi_category = Column(String(50), nullable=True)
    dominant_pollutant = Column(String(20), nullable=True)
    pm2_5_ugm3 = Column(Float, nullable=True)
    pm10_ugm3 = Column(Float, nullable=True)
    no2_ugm3 = Column(Float, nullable=True)
    so2_ugm3 = Column(Float, nullable=True)
    co_ugm3 = Column(Float, nullable=True)
    o3_ugm3 = Column(Float, nullable=True)

    raw_payload = Column(JSON, nullable=True)

