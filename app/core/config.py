from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "ClimateTwin AI Backend"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "https://climatetwin.ai",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        return v

    # Database Settings (PostgreSQL / Supabase / SQLite)
    DATABASE_URL: str = "sqlite:///./climatetwin.db"

    # External Environmental API Endpoints
    OPEN_METEO_BASE_URL: str = "https://api.open-meteo.com/v1"
    OPEN_METEO_AIR_QUALITY_URL: str = "https://air-quality-api.open-meteo.com/v1"
    OPEN_METEO_ARCHIVE_URL: str = "https://archive-api.open-meteo.com/v1"

    # Optional Fallback API Tokens
    OPENWEATHERMAP_API_KEY: str = ""
    WAQI_API_TOKEN: str = ""

    # Pune Pilot Benchmark Coordinates
    DEFAULT_LOCATION_NAME: str = "Pune"
    DEFAULT_LATITUDE: float = 18.5204
    DEFAULT_LONGITUDE: float = 73.8567
    DEFAULT_ELEVATION: float = 560.0

    # HTTP Client Configuration
    REQUEST_TIMEOUT_SECONDS: float = 10.0
    CACHE_TTL_SECONDS: int = 300

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


settings = Settings()

