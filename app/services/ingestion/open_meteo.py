from typing import Any, Dict, Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.core.logging import logger
from app.core.exceptions import DataIngestionError
from app.services.ingestion.base_client import ResilientHTTPClient
from app.services.ingestion.offline_fallback import PuneBaselineFallback


class OpenMeteoClient:
    """Client for fetching live and forecasted weather & air quality data from Open-Meteo."""

    def __init__(self):
        self.http = ResilientHTTPClient()
        self.weather_url = f"{settings.OPEN_METEO_BASE_URL}/forecast"
        self.aqi_url = f"{settings.OPEN_METEO_AIR_QUALITY_URL}/air-quality"
        self.archive_url = f"{settings.OPEN_METEO_ARCHIVE_URL}/archive"

    async def fetch_current_weather(
        self,
        latitude: float = settings.DEFAULT_LATITUDE,
        longitude: float = settings.DEFAULT_LONGITUDE
    ) -> Dict[str, Any]:
        """Fetch current weather and 24h forecast for given coordinates."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "temperature_2m",
                "relative_humidity_2m",
                "apparent_temperature",
                "precipitation",
                "rain",
                "weather_code",
                "surface_pressure",
                "wind_speed_10m",
                "wind_direction_10m"
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation_probability",
                "precipitation",
                "wind_speed_10m"
            ],
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "precipitation_hours",
                "wind_speed_10m_max"
            ],
            "timezone": "Asia/Kolkata",
            "forecast_days": 3
        }

        try:
            data = await self.http.get(self.weather_url, params=params)
            data["_metadata"] = {
                "source": "Open-Meteo Weather API",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "latitude": latitude,
                "longitude": longitude
            }
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch live Open-Meteo weather for ({latitude}, {longitude}): {e}; engaging IMD Pune Climatological Baseline fallback.")
            return PuneBaselineFallback.get_weather_fallback(latitude=latitude, longitude=longitude)

    async def fetch_current_air_quality(
        self,
        latitude: float = settings.DEFAULT_LATITUDE,
        longitude: float = settings.DEFAULT_LONGITUDE
    ) -> Dict[str, Any]:
        """Fetch current atmospheric composition and air quality metrics."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": [
                "us_aqi",
                "pm10",
                "pm2_5",
                "carbon_monoxide",
                "nitrogen_dioxide",
                "sulphur_dioxide",
                "ozone"
            ],
            "hourly": [
                "us_aqi",
                "pm2_5",
                "pm10",
                "nitrogen_dioxide",
                "ozone"
            ],
            "timezone": "Asia/Kolkata",
            "forecast_days": 2
        }

        try:
            data = await self.http.get(self.aqi_url, params=params)
            data["_metadata"] = {
                "source": "Open-Meteo Air Quality API",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "latitude": latitude,
                "longitude": longitude
            }
            return data
        except Exception as e:
            logger.warning(f"Failed to fetch live Open-Meteo air quality for ({latitude}, {longitude}): {e}; engaging CPCB Pune Climatological Baseline fallback.")
            return PuneBaselineFallback.get_air_quality_fallback(latitude=latitude, longitude=longitude)

    async def fetch_historical_weather(
        self,
        start_date: str,
        end_date: str,
        latitude: float = settings.DEFAULT_LATITUDE,
        longitude: float = settings.DEFAULT_LONGITUDE
    ) -> Dict[str, Any]:
        """Fetch historical reanalysis data (ERA5) for baseline comparisons."""
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date,
            "end_date": end_date,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "wind_speed_10m_max"
            ],
            "timezone": "Asia/Kolkata"
        }

        try:
            return await self.http.get(self.archive_url, params=params)
        except Exception as e:
            logger.warning(f"Failed to fetch historical archive for ({latitude}, {longitude}): {e}; returning baseline climate trend.")
            from datetime import datetime, timedelta
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            days_count = max(1, (end_dt - start_dt).days + 1)
            date_list = [(start_dt + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days_count)]
            return {
                "latitude": latitude,
                "longitude": longitude,
                "daily": {
                    "time": date_list,
                    "temperature_2m_max": [31.5] * len(date_list),
                    "temperature_2m_min": [18.2] * len(date_list),
                    "precipitation_sum": [0.0] * len(date_list),
                    "wind_speed_10m_max": [12.0] * len(date_list)
                }
            }

