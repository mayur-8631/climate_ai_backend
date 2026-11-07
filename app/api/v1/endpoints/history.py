from typing import List, Optional
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.db.models.observation import WeatherObservation
from app.services.ingestion.open_meteo import OpenMeteoClient
from app.api.v1.endpoints.weather import resolve_coordinates

router = APIRouter()
open_meteo_client = OpenMeteoClient()


class HistoricalDataPoint(BaseModel):
    date: str
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    precipitation_sum: Optional[float] = None
    wind_speed_max: Optional[float] = None
    source: str = "ERA5 Reanalysis"


class HistoryResponse(BaseModel):
    location: str
    ward: Optional[str] = None
    start_date: str
    end_date: str
    total_days: int
    data: List[HistoricalDataPoint]


@router.get("", response_model=HistoryResponse)
async def get_climate_history(
    location: str = Query("Pune", description="Pilot city name"),
    ward: Optional[str] = Query(None),
    days: int = Query(30, ge=7, le=365, description="Number of past days to retrieve"),
    db: Session = Depends(get_db)
):
    """
    Fetch historical climate records and multi-day trends for time-series charts.
    Uses verified historical reanalysis (ERA5) for baseline accuracy.
    """
    lat, lon, resolved_ward = resolve_coordinates(ward)

    end_dt = datetime.now(timezone.utc) - timedelta(days=2)  # ERA5 typically available with 2-day lag
    start_dt = end_dt - timedelta(days=days)

    start_str = start_dt.strftime("%Y-%m-%d")
    end_str = end_dt.strftime("%Y-%m-%d")

    try:
        raw_hist = await open_meteo_client.fetch_historical_weather(
            start_date=start_str,
            end_date=end_str,
            latitude=lat,
            longitude=lon
        )

        daily = raw_hist.get("daily", {})
        times = daily.get("time", [])
        t_maxs = daily.get("temperature_2m_max", [])
        t_mins = daily.get("temperature_2m_min", [])
        p_sums = daily.get("precipitation_sum", [])
        w_maxs = daily.get("wind_speed_10m_max", [])

        points = []
        for i, t in enumerate(times):
            points.append(HistoricalDataPoint(
                date=t,
                temperature_max=t_maxs[i] if i < len(t_maxs) else None,
                temperature_min=t_mins[i] if i < len(t_mins) else None,
                precipitation_sum=p_sums[i] if i < len(p_sums) else None,
                wind_speed_max=w_maxs[i] if i < len(w_maxs) else None,
                source="Open-Meteo ERA5 Archive"
            ))

        return HistoryResponse(
            location=location,
            ward=resolved_ward,
            start_date=start_str,
            end_date=end_str,
            total_days=len(points),
            data=points
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch historical archive data: {str(e)}")

