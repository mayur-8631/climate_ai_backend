"""
ClimateTwin AI - Database Connection Diagnostic Tool
Tests connection to the configured database (SQLite or Supabase PostgreSQL)
and verifies table schema accessibility.
Usage:
    python scripts/test_db_connection.py
"""

import os
import sys

# Ensure repository root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import inspect, text
from app.core.config import settings
from app.db.session import engine, SessionLocal
from app.db.models.location import Location
from app.db.models.observation import WeatherObservation, AirQualityObservation


def test_connection():
    print("=" * 60)
    print("  ClimateTwin AI - Database Diagnostic Check")
    print("=" * 60)

    db_url = settings.DATABASE_URL
    # Mask password for security display
    if "@" in db_url and "://" in db_url:
        protocol_user, host_part = db_url.split("@")
        masked_url = protocol_user.split(":")[0] + "://***:***@" + host_part
    else:
        masked_url = db_url

    print(f"Target Database URL: {masked_url}")

    try:
        # 1. Test basic connectivity
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1")).scalar()
            print(" -> Connection Test: SUCCESS (SELECT 1 returned 1)")

        # 2. Inspect created tables
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f" -> Found {len(tables)} tables in database:")
        for t in tables:
            print(f"    • {t}")

        # 3. Query record counts
        db = SessionLocal()
        try:
            loc_count = db.query(Location).count()
            weather_count = db.query(WeatherObservation).count()
            aq_count = db.query(AirQualityObservation).count()

            print("\nRecord Counts:")
            print(f" • Locations (Wards): {loc_count}")
            print(f" • Weather Observations: {weather_count}")
            print(f" • Air Quality Observations: {aq_count}")
        finally:
            db.close()

        print("\n" + "=" * 60)
        print(" DATABASE IS FULLY OPERATIONAL AND READY! ")
        print("=" * 60)

    except Exception as e:
        print(f"\nERROR: Database connection failed: {e}")
        print("\nTroubleshooting:")
        print(" 1. For SQLite: Ensure write permissions in the local directory.")
        print(" 2. For Supabase PostgreSQL: Check that your connection string in .env includes your password and is in URI format.")
        sys.exit(1)


if __name__ == "__main__":
    test_connection()

