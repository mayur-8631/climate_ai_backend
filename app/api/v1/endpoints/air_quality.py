from typing import Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.observation import AirQualityObservation
from app.schemas.air_quality import AirQualityResponse
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.services.preprocessing.cleaner import DataCleaner
from app.api.v1.endpoints.weather import resolve_coordinates

router = APIRouter()
open_meteo_client = OpenMeteoClient()


@router.get("", response_model=AirQualityResponse)
async def get_air_quality(
    location: str = Query("Pune", description="Pilot city name"),
    ward: Optional[str] = Query(None, description="Specific ward, e.g., Shivajinagar, Kothrud, Hadapsar"),
    latitude: Optional[float] = Query(None, ge=-90.0, le=90.0),
    longitude: Optional[float] = Query(None, ge=-180.0, le=180.0),
    db: Session = Depends(get_db)
):
    """
    Fetch real-time air quality metrics (AQI, PM2.5, PM10, NO2, SO2, CO, O3) for a selected location.
    Explicitly tracks data completeness and pollutant attribution.
    """
    lat, lon, ward_name = resolve_coordinates(ward, latitude, longitude)

    try:
        raw_aqi = await open_meteo_client.fetch_current_air_quality(latitude=lat, longitude=lon)
        cleaned = DataCleaner.clean_air_quality_payload(raw_aqi, location_name=location, ward=ward_name)

        # Persist observation for historical audit
        obs_record = AirQualityObservation(
            location_name=location,
            ward_name=ward_name,
            latitude=lat,
            longitude=lon,
            observed_at=cleaned.observed_at,
            source=cleaned.provenance.source,
            quality_flag=cleaned.provenance.quality_flag.value,
            aqi_value=cleaned.current.aqi,
            aqi_category=cleaned.current.category,
            dominant_pollutant=cleaned.current.dominant_pollutant,
            pm2_5_ugm3=cleaned.current.pm2_5.value,
            pm10_ugm3=cleaned.current.pm10.value,
            no2_ugm3=cleaned.current.no2.value,
            so2_ugm3=cleaned.current.so2.value,
            co_ugm3=cleaned.current.co.value,
            o3_ugm3=cleaned.current.o3.value,
            raw_payload=raw_aqi
        )
        db.add(obs_record)
        db.commit()

        return cleaned
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=502, detail=f"Failed to fetch air quality stream: {str(e)}")

