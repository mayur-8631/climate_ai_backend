from typing import Any, Dict, Optional
from datetime import datetime, timezone
from app.core.config import settings
from app.core.logging import logger
from app.services.ingestion.base_client import ResilientHTTPClient


class CPCBWAQIClient:
    """Client for ground-station air quality data across Pune micro-monitoring stations."""

    PUNE_GROUND_STATIONS = {
        "shivajinagar": {"station_id": "@8756", "name": "Shivajinagar, Pune CPCB"},
        "karve_road": {"station_id": "@8757", "name": "Karve Road, Pune CPCB"},
        "hadapsar": {"station_id": "@8758", "name": "Hadapsar, Pune CPCB"},
        "bhosari": {"station_id": "@8759", "name": "Bhosari, PCMC CPCB"},
        "katraj": {"station_id": "@8760", "name": "Katraj, Pune CPCB"}
    }

    def __init__(self):
        self.http = ResilientHTTPClient()
        self.token = settings.WAQI_API_TOKEN

    async def fetch_station_aqi(self, ward: str = "shivajinagar") -> Optional[Dict[str, Any]]:
        """Fetch ground monitor data from WAQI / CPCB if token is configured."""
        if not self.token:
            logger.info("WAQI_API_TOKEN not configured; using Open-Meteo as primary ground source.")
            return None

        station_key = ward.lower().strip()
        station = self.PUNE_GROUND_STATIONS.get(station_key, self.PUNE_GROUND_STATIONS["shivajinagar"])
        url = f"https://api.waqi.info/feed/{station['station_id']}/"

        try:
            res = await self.http.get(url, params={"token": self.token})
            if res.get("status") == "ok":
                return {
                    "source": f"CPCB Ground Station ({station['name']})",
                    "observed_at": res.get("data", {}).get("time", {}).get("iso", datetime.now(timezone.utc).isoformat()),
                    "aqi": res.get("data", {}).get("aqi"),
                    "dominant_pollutant": res.get("data", {}).get("dominentpol"),
                    "iaqi": res.get("data", {}).get("iaqi", {})
                }
            return None
        except Exception as e:
            logger.warning(f"Failed to fetch ground monitor data for station {station['name']}: {e}")
            return None

