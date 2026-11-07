from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.session import get_db
from app.db.models.observation import WeatherObservation
from app.schemas.weather import WeatherResponse
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.services.preprocessing.cleaner import DataCleaner
from app.api.v1.endpoints.locations import PUNE_LOCATION

router = APIRouter()
open_meteo_client = OpenMeteoClient()


def resolve_coordinates(ward: Optional[str] = None, lat: Optional[float] = None, lon: Optional[float] = None):
    if lat is not None and lon is not None:
        return lat, lon, ward

    if ward:
        clean_ward = ward.lower().strip()
        for w in PUNE_LOCATION.wards:
            if clean_ward in w.name.lower() or clean_ward in w.ward_code.lower():
                return w.coordinates.latitude, w.coordinates.longitude, w.name

    # Default to Pune Centroid
    return settings.DEFAULT_LATITUDE, settings.DEFAULT_LONGITUDE, "Shivajinagar (Central)"


@router.get("", response_model=WeatherResponse)
async def get_weather(
    location: str = Query("Pune", description="Pilot city name"),
    ward: Optional[str] = Query(None, description="Specific ward, e.g., Shivajinagar, Kothrud, Hadapsar"),
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
):
    """
    Fetch real-time weather observations and short-term forecast for a selected location.
    Every observation includes explicit provenance and source tracking.
    """
    lat, lon, ward_name = resolve_coordinates(ward, latitude, longitude)

    try:
        raw_weather = await open_meteo_client.fetch_current_weather(latitude=lat, longitude=lon)
        cleaned = DataCleaner.clean_weather_payload(raw_weather, location_name=location, ward=ward_name)

        # Persist observation for historical audit without fabricating missing measurements
        obs_record = WeatherObservation(
            location_name=location,
            ward_name=ward_name,
            latitude=lat,
            longitude=lon,
            observed_at=cleaned.observed_at,
            source=cleaned.provenance.source,
            quality_flag=cleaned.provenance.quality_flag.value,
            temperature_c=cleaned.current.temperature,
            relative_humidity_pct=cleaned.current.relative_humidity,
            precipitation_mm=cleaned.current.precipitation,
            rain_mm=cleaned.current.rain,
            wind_speed_kmh=cleaned.current.wind_speed,
            surface_pressure_hpa=cleaned.current.surface_pressure,
            cloud_cover_pct=cleaned.current.cloud_cover,
            weather_code=cleaned.current.weather_code,
            raw_payload=raw_weather
        )
        db.add(obs_record)
        db.commit()

        return cleaned
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Failed to fetch environmental weather stream: {str(e)}")

