from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timezone
from app.schemas.common import DataQuality, Provenance, Coordinates
from app.schemas.weather import CurrentWeather, HourlyWeatherPoint, DailyWeatherPoint, WeatherResponse
from app.schemas.air_quality import AirQualityCurrent, PollutantDetail, AirQualityHourlyPoint, AirQualityResponse


WMO_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail"
}


class DataCleaner:
    """Sanitizes raw environmental streams, enforces data provenance, and flags missing entries without zero-masking."""

    @staticmethod
    def clean_weather_payload(
        raw: Dict[str, Any],
        location_name: str = "Pune",
        ward: Optional[str] = None
    ) -> WeatherResponse:
        current_data = raw.get("current", {})
        meta = raw.get("_metadata", {})

        # Determine data quality
        essential_fields = ["temperature_2m", "relative_humidity_2m", "precipitation"]
        missing_count = sum(1 for f in essential_fields if current_data.get(f) is None)

        if missing_count == 0:
            quality = DataQuality.GOOD
        elif missing_count < len(essential_fields):
            quality = DataQuality.DEGRADED
        else:
            quality = DataQuality.MISSING_SOURCE

        # Current weather parsing
        w_code = current_data.get("weather_code")
        current = CurrentWeather(
            temperature=current_data.get("temperature_2m"),
            temperature_unit="celsius",
            apparent_temperature=current_data.get("apparent_temperature"),
            relative_humidity=current_data.get("relative_humidity_2m"),
            precipitation=current_data.get("precipitation"),
            precipitation_unit="mm",
            rain=current_data.get("rain"),
            wind_speed=current_data.get("wind_speed_10m"),
            wind_direction=current_data.get("wind_direction_10m"),
            surface_pressure=current_data.get("surface_pressure"),
            cloud_cover=current_data.get("cloud_cover"),
            weather_code=w_code,
            weather_description=WMO_WEATHER_CODES.get(w_code, "Unknown") if w_code is not None else None
        )

        # Parse hourly forecast (up to 24 hours)
        hourly_points = []
        hourly_data = raw.get("hourly", {})
        times = hourly_data.get("time", [])[:24]
        temps = hourly_data.get("temperature_2m", [])
        humids = hourly_data.get("relative_humidity_2m", [])
        precips = hourly_data.get("precipitation", [])
        precip_probs = hourly_data.get("precipitation_probability", [])
        winds = hourly_data.get("wind_speed_10m", [])

        for i, t in enumerate(times):
            try:
                dt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
                hourly_points.append(HourlyWeatherPoint(
                    timestamp=dt,
                    temperature=temps[i] if i < len(temps) else None,
                    relative_humidity=humids[i] if i < len(humids) else None,
                    precipitation=precips[i] if i < len(precips) else None,
                    precipitation_probability=precip_probs[i] if i < len(precip_probs) else None,
                    wind_speed=winds[i] if i < len(winds) else None
                ))
            except Exception:
                continue

        # Parse daily forecast
        daily_points = []
        daily_data = raw.get("daily", {})
        dates = daily_data.get("time", [])
        t_maxs = daily_data.get("temperature_2m_max", [])
        t_mins = daily_data.get("temperature_2m_min", [])
        p_sums = daily_data.get("precipitation_sum", [])
        p_hours = daily_data.get("precipitation_hours", [])
        w_maxs = daily_data.get("wind_speed_10m_max", [])

        for i, d in enumerate(dates):
            daily_points.append(DailyWeatherPoint(
                date=d,
                temperature_max=t_maxs[i] if i < len(t_maxs) else None,
                temperature_min=t_mins[i] if i < len(t_mins) else None,
                precipitation_sum=p_sums[i] if i < len(p_sums) else None,
                precipitation_hours=p_hours[i] if i < len(p_hours) else None,
                wind_speed_max=w_maxs[i] if i < len(w_maxs) else None
            ))

        obs_time_raw = current_data.get("time")
        if obs_time_raw:
            try:
                observed_at = datetime.fromisoformat(obs_time_raw).replace(tzinfo=timezone.utc)
            except Exception:
                observed_at = datetime.now(timezone.utc)
        else:
            observed_at = datetime.now(timezone.utc)

        provenance = Provenance(
            source=meta.get("source", "Open-Meteo Weather API"),
            observed_at=observed_at,
            quality_flag=quality
        )

        return WeatherResponse(
            location=location_name,
            ward=ward,
            coordinates=Coordinates(
                latitude=raw.get("latitude", 18.5204),
                longitude=raw.get("longitude", 73.8567)
            ),
            observed_at=observed_at,
            provenance=provenance,
            current=current,
            hourly_forecast=hourly_points,
            daily_forecast=daily_points
        )

    @staticmethod
    def clean_air_quality_payload(
        raw: Dict[str, Any],
        location_name: str = "Pune",
        ward: Optional[str] = None
    ) -> AirQualityResponse:
        current_data = raw.get("current", {})
        meta = raw.get("_metadata", {})

        us_aqi = current_data.get("us_aqi")
        pm2_5_val = current_data.get("pm2_5")
        pm10_val = current_data.get("pm10")
        no2_val = current_data.get("nitrogen_dioxide")
        so2_val = current_data.get("sulphur_dioxide")
        co_val = current_data.get("carbon_monoxide")
        o3_val = current_data.get("ozone")

        # Map AQI Category
        if us_aqi is not None:
            if us_aqi <= 50:
                cat = "Good"
            elif us_aqi <= 100:
                cat = "Moderate"
            elif us_aqi <= 150:
                cat = "Unhealthy for Sensitive Groups"
            elif us_aqi <= 200:
                cat = "Unhealthy"
            elif us_aqi <= 300:
                cat = "Very Unhealthy"
            else:
                cat = "Hazardous"
        else:
            cat = "Unavailable"

        # Determine dominant pollutant
        dominant = "PM2.5" if (pm2_5_val or 0) > 30 else ("PM10" if (pm10_val or 0) > 60 else "Ozone")

        current = AirQualityCurrent(
            aqi=int(us_aqi) if us_aqi is not None else None,
            category=cat,
            dominant_pollutant=dominant if us_aqi is not None else None,
            pm2_5=PollutantDetail(value=pm2_5_val, status="MEASURED" if pm2_5_val is not None else "UNAVAILABLE"),
            pm10=PollutantDetail(value=pm10_val, status="MEASURED" if pm10_val is not None else "UNAVAILABLE"),
            no2=PollutantDetail(value=no2_val, status="MEASURED" if no2_val is not None else "UNAVAILABLE"),
            so2=PollutantDetail(value=so2_val, status="MEASURED" if so2_val is not None else "UNAVAILABLE"),
            co=PollutantDetail(value=co_val, status="MEASURED" if co_val is not None else "UNAVAILABLE"),
            o3=PollutantDetail(value=o3_val, status="MEASURED" if o3_val is not None else "UNAVAILABLE")
        )

        # Parse hourly trend
        hourly_trend = []
        hourly_data = raw.get("hourly", {})
        times = hourly_data.get("time", [])[:24]
        aqis = hourly_data.get("us_aqi", [])
        pm2_5s = hourly_data.get("pm2_5", [])
        pm10s = hourly_data.get("pm10", [])
        no2s = hourly_data.get("nitrogen_dioxide", [])

        for i, t in enumerate(times):
            try:
                dt = datetime.fromisoformat(t).replace(tzinfo=timezone.utc)
                hourly_trend.append(AirQualityHourlyPoint(
                    timestamp=dt,
                    aqi=aqis[i] if i < len(aqis) else None,
                    pm2_5=pm2_5s[i] if i < len(pm2_5s) else None,
                    pm10=pm10s[i] if i < len(pm10s) else None,
                    no2=no2s[i] if i < len(no2s) else None
                ))
            except Exception:
                continue

        obs_time_raw = current_data.get("time")
        if obs_time_raw:
            try:
                observed_at = datetime.fromisoformat(obs_time_raw).replace(tzinfo=timezone.utc)
            except Exception:
                observed_at = datetime.now(timezone.utc)
        else:
            observed_at = datetime.now(timezone.utc)

        provenance = Provenance(
            source=meta.get("source", "Open-Meteo Air Quality API"),
            observed_at=observed_at,
            quality_flag=DataQuality.GOOD if us_aqi is not None else DataQuality.DEGRADED
        )

        return AirQualityResponse(
            location=location_name,
            ward=ward,
            coordinates=Coordinates(
                latitude=raw.get("latitude", 18.5204),
                longitude=raw.get("longitude", 73.8567)
            ),
            observed_at=observed_at,
            provenance=provenance,
            current=current,
            hourly_trend=hourly_trend
        )

