from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from app.schemas.common import Coordinates, Provenance


class CurrentWeather(BaseModel):
    temperature: Optional[float] = Field(None, description="Air temperature in Celsius")
    temperature_unit: str = "celsius"
    apparent_temperature: Optional[float] = Field(None, description="Feels like temperature in Celsius")
    relative_humidity: Optional[float] = Field(None, ge=0, le=100, description="Relative humidity percentage")
    precipitation: Optional[float] = Field(None, ge=0, description="Precipitation in mm (strictly null if missing, 0.0 means measured zero)")
    precipitation_unit: str = "mm"
    rain: Optional[float] = Field(None, ge=0, description="Rainfall in mm")
    wind_speed: Optional[float] = Field(None, ge=0, description="Wind speed in km/h")
    wind_direction: Optional[float] = Field(None, ge=0, le=360, description="Wind direction in degrees")
    surface_pressure: Optional[float] = Field(None, description="Atmospheric pressure in hPa")
    cloud_cover: Optional[float] = Field(None, ge=0, le=100, description="Cloud cover percentage")
    weather_code: Optional[int] = Field(None, description="WMO weather interpretation code")
    weather_description: Optional[str] = Field(None, description="Human readable weather condition")


class HourlyWeatherPoint(BaseModel):
    timestamp: datetime
    temperature: Optional[float] = None
    relative_humidity: Optional[float] = None
    precipitation: Optional[float] = None
    precipitation_probability: Optional[float] = None
    wind_speed: Optional[float] = None


class DailyWeatherPoint(BaseModel):
    date: str
    temperature_max: Optional[float] = None
    temperature_min: Optional[float] = None
    precipitation_sum: Optional[float] = None
    precipitation_hours: Optional[float] = None
    wind_speed_max: Optional[float] = None


class WeatherResponse(BaseModel):
    location: str
    ward: Optional[str] = None
    coordinates: Coordinates
    observed_at: datetime
    provenance: Provenance
    current: CurrentWeather
    hourly_forecast: Optional[List[HourlyWeatherPoint]] = None
    daily_forecast: Optional[List[DailyWeatherPoint]] = None

