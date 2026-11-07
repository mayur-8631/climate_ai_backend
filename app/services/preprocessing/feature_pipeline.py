from typing import Any, Dict
from datetime import datetime, timezone
from app.schemas.weather import WeatherResponse
from app.schemas.air_quality import AirQualityResponse
from app.services.preprocessing.normalizer import EnvironmentalNormalizer


class FeaturePipeline:
    """Prepares structured feature matrices for Lokesh's hazard prediction models."""

    @staticmethod
    def extract_features(
        weather: WeatherResponse,
        air_quality: AirQualityResponse
    ) -> Dict[str, Any]:
        temp = weather.current.temperature if weather.current.temperature is not None else 28.0
        humid = weather.current.relative_humidity if weather.current.relative_humidity is not None else 50.0
        heat_idx = EnvironmentalNormalizer.calculate_heat_index(temp, humid)

        # Calculate 24h precipitation sum from hourly forecast if available
        precip_current = weather.current.precipitation if weather.current.precipitation is not None else 0.0
        precip_sum_24h = 0.0
        if weather.hourly_forecast:
            precip_sum_24h = sum(
                pt.precipitation for pt in weather.hourly_forecast[:24] if pt.precipitation is not None
            )
        elif weather.daily_forecast and len(weather.daily_forecast) > 0:
            precip_sum_24h = weather.daily_forecast[0].precipitation_sum or precip_current
        else:
            precip_sum_24h = precip_current

        now = datetime.now(timezone.utc)
        month = now.month

        # Pune climatological seasons:
        # Monsoon: June (6) to Sept (9)
        # Summer/Pre-monsoon: March (3) to May (5)
        # Winter/Post-monsoon: Oct (10) to Feb (2)
        is_monsoon = 1 if 6 <= month <= 9 else 0
        is_summer = 1 if 3 <= month <= 5 else 0

        aqi_val = air_quality.current.aqi if air_quality.current.aqi is not None else 80
        pm2_5_val = air_quality.current.pm2_5.value if air_quality.current.pm2_5.value is not None else 35.0
        pm10_val = air_quality.current.pm10.value if air_quality.current.pm10.value is not None else 65.0
        no2_val = air_quality.current.no2.value if air_quality.current.no2.value is not None else 20.0

        return {
            "temp_c": temp,
            "humidity_pct": humid,
            "heat_index_c": heat_idx,
            "apparent_temp_c": weather.current.apparent_temperature or temp,
            "precip_current_mm": precip_current,
            "precip_24h_sum_mm": round(precip_sum_24h, 2),
            "wind_speed_kmh": weather.current.wind_speed or 10.0,
            "surface_pressure_hpa": weather.current.surface_pressure or 950.0,
            "aqi": aqi_val,
            "pm2_5": pm2_5_val,
            "pm10": pm10_val,
            "no2": no2_val,
            "is_monsoon_season": is_monsoon,
            "is_summer_season": is_summer,
            "month": month,
            "hour": now.hour
        }

