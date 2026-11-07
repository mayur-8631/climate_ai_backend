"""
ClimateTwin AI - Database Seeder
Seeds initial Pune pilot locations, micro-wards, and historical baseline records
into the database (Supabase PostgreSQL / SQLite).
Usage:
    python scripts/seed_database.py
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timezone, timedelta
from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.models.location import Location
from app.db.models.observation import WeatherObservation, AirQualityObservation
from app.db.models.prediction import RiskAssessmentRecord
from app.api.v1.endpoints.locations import PUNE_LOCATION


def seed_database():
    print("=" * 60)
    print("  ClimateTwin AI - Initializing Database Seeder")
    print("=" * 60)

    # 1. Ensure tables exist
    print("[1/3] Creating tables if not already present...")
    Base.metadata.create_all(bind=engine)
    print(" -> Table schemas verified.")

    db = SessionLocal()
    try:
        # 2. Seed Locations & Wards
        print("[2/3] Checking pilot locations and micro-wards...")
        existing_count = db.query(Location).filter(Location.name == "Pune").count()
        if existing_count == 0:
            print(f" -> Seeding {len(PUNE_LOCATION.wards)} Pune micro-wards...")
            for w in PUNE_LOCATION.wards:
                loc = Location(
                    name="Pune",
                    ward_name=w.name,
                    latitude=w.coordinates.latitude,
                    longitude=w.coordinates.longitude,
                    elevation_m=w.elevation_m,
                    is_pilot=True,
                    created_at=datetime.now(timezone.utc)
                )
                db.add(loc)
            db.commit()
            print(" -> Micro-wards seeded successfully.")
        else:
            print(f" -> Locations already seeded ({existing_count} records found).")

        # 3. Seed Initial Baseline Observations
        print("[3/3] Checking baseline observations...")
        obs_count = db.query(WeatherObservation).count()
        if obs_count == 0:
            print(" -> Seeding initial baseline observations for Pune...")
            now = datetime.now(timezone.utc)
            for w in PUNE_LOCATION.wards:
                w_obs = WeatherObservation(
                    location_name="Pune",
                    ward_name=w.name,
                    latitude=w.coordinates.latitude,
                    longitude=w.coordinates.longitude,
                    observed_at=now,
                    source="IMD Pune Climatological Baseline",
                    quality_flag="GOOD",
                    temperature_c=28.5,
                    relative_humidity_pct=48.0,
                    precipitation_mm=0.0,
                    rain_mm=0.0,
                    wind_speed_kmh=12.0,
                    surface_pressure_hpa=951.0,
                    cloud_cover_pct=20.0,
                    weather_code=1
                )
                aq_obs = AirQualityObservation(
                    location_name="Pune",
                    ward_name=w.name,
                    latitude=w.coordinates.latitude,
                    longitude=w.coordinates.longitude,
                    observed_at=now,
                    source="CPCB Ground Monitor Baseline",
                    quality_flag="GOOD",
                    aqi_value=145,
                    aqi_category="Moderate",
                    dominant_pollutant="PM2.5",
                    pm2_5_ugm3=55.0,
                    pm10_ugm3=105.0,
                    no2_ugm3=24.0,
                    so2_ugm3=11.0,
                    co_ugm3=450.0,
                    o3_ugm3=38.0
                )
                risk_rec = RiskAssessmentRecord(
                    location_name="Pune",
                    ward_name=w.name,
                    calculated_at=now,
                    climate_risk_score=26,
                    risk_level="Moderate",
                    temperature_observed=28.5,
                    rainfall_observed=0.0,
                    aqi_observed=145,
                    heat_risk=18.5,
                    flood_risk=5.0,
                    air_quality_risk=60.0,
                    water_stress_risk=32.0,
                    is_simulation=False
                )
                db.add(w_obs)
                db.add(aq_obs)
                db.add(risk_rec)
            db.commit()
            print(" -> Baseline observations and assessments seeded.")
        else:
            print(f" -> Observations already present ({obs_count} records found).")

        print("=" * 60)
        print(" Database Seeding Completed Successfully! ")
        print("=" * 60)

    except Exception as e:
        db.rollback()
        print(f"ERROR: Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
