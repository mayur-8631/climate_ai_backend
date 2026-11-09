"""
ClimateTwin AI — Central Configuration & Schema Definitions
Module: ml_engine/config.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Defines:
- Directory paths for datasets, models, evaluation metrics, and plots
- Random seed and reproducibility constants
- Canonical feature schema shared with Mayuresh Kamble's FastAPI backend
- Physical plausibility bounds vs. extreme weather outlier thresholds
- Climatological monthly baselines (Pune pilot + multi-city fallback)
- Official Indian CPCB National Air Quality Index (NAQI) breakpoint table
- Configurable Climate Risk Score weights and category thresholds
"""

from pathlib import Path
from typing import Dict, List, Tuple, Any

# ============================================================================
# 1. PROJECT PATHS & REPRODUCIBILITY
# ============================================================================
BASE_DIR: Path = Path(__file__).resolve().parent.parent
DATASETS_DIR: Path = BASE_DIR / "datasets"
RAW_DATA_DIR: Path = DATASETS_DIR / "raw"
PROCESSED_DATA_DIR: Path = DATASETS_DIR / "processed"

MODELS_DIR: Path = BASE_DIR / "models"
HEAT_MODEL_DIR: Path = MODELS_DIR / "heat"
FLOOD_MODEL_DIR: Path = MODELS_DIR / "flood"
AIR_QUALITY_MODEL_DIR: Path = MODELS_DIR / "air_quality"
WATER_STRESS_MODEL_DIR: Path = MODELS_DIR / "water_stress"

EVALUATION_DIR: Path = BASE_DIR / "evaluation"
METRICS_DIR: Path = EVALUATION_DIR / "metrics"
PLOTS_DIR: Path = EVALUATION_DIR / "plots"

RANDOM_SEED: int = 42
MODEL_VERSION: str = "1.0.0"

# Ensure directories exist
for _dir in [
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    HEAT_MODEL_DIR,
    FLOOD_MODEL_DIR,
    AIR_QUALITY_MODEL_DIR,
    WATER_STRESS_MODEL_DIR,
    METRICS_DIR,
    PLOTS_DIR,
]:
    _dir.mkdir(parents=True, exist_ok=True)


# ============================================================================
# 2. CANONICAL ENVIRONMENTAL INPUT SCHEMA (INTEGRATION CONTRACT)
# ============================================================================
# Coordinated with Mayuresh Kamble (Backend) and Pravin Kamble (Frontend)
REQUIRED_METADATA_COLUMNS: List[str] = ["timestamp", "location"]

# Canonical numeric environmental columns and their standard units
CANONICAL_NUMERIC_FEATURES: Dict[str, str] = {
    # Weather
    "temperature_c": "°C",
    "temp_max_c": "°C",
    "temp_min_c": "°C",
    "humidity_pct": "%",
    "wind_speed_kmh": "km/h",
    "wind_direction_deg": "degrees (0-360)",
    "pressure_hpa": "hPa",
    # Rainfall & Hydrology
    "rainfall_mm": "mm (daily)",
    "rainfall_intensity_mm_hr": "mm/hr (peak hourly)",
    # Air Quality
    "pm25_ugm3": "µg/m³",
    "pm10_ugm3": "µg/m³",
    "no2_ugm3": "µg/m³",
    "so2_ugm3": "µg/m³",
    "co_mgm3": "mg/m³",
    "o3_ugm3": "µg/m³",
    "measured_aqi": "index (0-500, optional)",
    # Water Stress & Land Surface
    "soil_moisture": "volumetric fraction (0-1)",
    "evapotranspiration_mm": "mm/day",
    "water_availability_index": "normalized index (0-1, optional)",
    # Geographical / Topographical
    "latitude": "degrees North",
    "longitude": "degrees East",
    "elevation_m": "meters above MSL",
    "slope_deg": "degrees",
    "drainage_index": "normalized capacity (0-1)",
}

# Field aliases to normalize incoming payloads from diverse APIs or backend requests
COLUMN_ALIASES: Dict[str, str] = {
    "temp": "temperature_c",
    "temp_c": "temperature_c",
    "temperature": "temperature_c",
    "temperature_2m": "temperature_c",
    "tmax": "temp_max_c",
    "max_temperature": "temp_max_c",
    "temperature_2m_max": "temp_max_c",
    "tmin": "temp_min_c",
    "min_temperature": "temp_min_c",
    "temperature_2m_min": "temp_min_c",
    "humidity": "humidity_pct",
    "relative_humidity": "humidity_pct",
    "relative_humidity_2m": "humidity_pct",
    "wind_speed": "wind_speed_kmh",
    "wind_speed_10m": "wind_speed_kmh",
    "wind_direction": "wind_direction_deg",
    "pressure": "pressure_hpa",
    "surface_pressure": "pressure_hpa",
    "surface_pressure_hpa": "pressure_hpa",
    "rainfall": "rainfall_mm",
    "precipitation": "rainfall_mm",
    "daily_rainfall": "rainfall_mm",
    "precip_24h_sum_mm": "rainfall_mm",
    "rainfall_intensity": "rainfall_intensity_mm_hr",
    "precip_current_mm": "rainfall_intensity_mm_hr",
    "pm25": "pm25_ugm3",
    "pm2_5": "pm25_ugm3",
    "pm10": "pm10_ugm3",
    "no2": "no2_ugm3",
    "so2": "so2_ugm3",
    "co": "co_mgm3",
    "o3": "o3_ugm3",
    "aqi": "measured_aqi",
    "evapotranspiration": "evapotranspiration_mm",
    "et0": "evapotranspiration_mm",
    "elevation": "elevation_m",
    "slope": "slope_deg",
    "lat": "latitude",
    "lon": "longitude",
}


# ============================================================================
# 3. PHYSICAL PLAUSIBILITY BOUNDS vs. EXTREME WEATHER THRESHOLDS
# ============================================================================
# Values outside (min_valid, max_valid) are physically impossible sensor errors
# and are converted to NaN and flagged. Values inside valid bounds but beyond
# extreme thresholds are genuine climate extremes and MUST BE PRESERVED.
PHYSICAL_BOUNDS: Dict[str, Tuple[float, float]] = {
    "temperature_c": (-40.0, 60.0),
    "temp_max_c": (-35.0, 62.0),
    "temp_min_c": (-45.0, 50.0),
    "humidity_pct": (0.0, 100.0),
    "wind_speed_kmh": (0.0, 350.0),
    "wind_direction_deg": (0.0, 360.0),
    "pressure_hpa": (850.0, 1085.0),
    "rainfall_mm": (0.0, 1200.0),
    "rainfall_intensity_mm_hr": (0.0, 300.0),
    "pm25_ugm3": (0.0, 2000.0),
    "pm10_ugm3": (0.0, 3000.0),
    "no2_ugm3": (0.0, 1500.0),
    "so2_ugm3": (0.0, 1500.0),
    "co_mgm3": (0.0, 100.0),
    "o3_ugm3": (0.0, 1000.0),
    "measured_aqi": (0.0, 500.0),
    "soil_moisture": (0.0, 1.0),
    "evapotranspiration_mm": (0.0, 25.0),
    "water_availability_index": (0.0, 1.0),
    "latitude": (-90.0, 90.0),
    "longitude": (-180.0, 180.0),
    "elevation_m": (-450.0, 9000.0),
    "slope_deg": (0.0, 89.0),
    "drainage_index": (0.0, 1.0),
}

# Genuine climate extreme thresholds (flagged as extreme events, NEVER deleted)
CLIMATE_EXTREME_THRESHOLDS: Dict[str, Tuple[float, float]] = {
    "temperature_c": (5.0, 42.0),
    "temp_max_c": (15.0, 43.0),
    "rainfall_mm": (0.0, 115.0),          # IMD Heavy to Extremely Heavy rain >115.6 mm
    "rainfall_intensity_mm_hr": (0.0, 35.0),
    "pm25_ugm3": (0.0, 150.0),
    "pm10_ugm3": (0.0, 300.0),
}


# ============================================================================
# 4. PUNE PILOT CLIMATOLOGICAL BASELINES (IMD 30-Year Normal Reference)
# ============================================================================
# Monthly normal mean temperature (°C), max temperature (°C), and monthly rain (mm)
PUNE_MONTHLY_CLIMATOLOGY: Dict[int, Dict[str, float]] = {
    1:  {"temp_mean": 21.0, "temp_max": 29.9, "temp_min": 12.0, "rain_daily_avg": 0.1, "humidity": 52.0},
    2:  {"temp_mean": 23.2, "temp_max": 31.9, "temp_min": 13.8, "rain_daily_avg": 0.1, "humidity": 44.0},
    3:  {"temp_mean": 26.8, "temp_max": 35.4, "temp_min": 17.5, "rain_daily_avg": 0.2, "humidity": 37.0},
    4:  {"temp_mean": 29.5, "temp_max": 37.7, "temp_min": 21.0, "rain_daily_avg": 0.6, "humidity": 41.0},
    5:  {"temp_mean": 29.8, "temp_max": 36.9, "temp_min": 22.8, "rain_daily_avg": 1.5, "humidity": 54.0},
    6:  {"temp_mean": 26.6, "temp_max": 31.4, "temp_min": 22.9, "rain_daily_avg": 5.8, "humidity": 75.0},
    7:  {"temp_mean": 24.6, "temp_max": 28.1, "temp_min": 22.0, "rain_daily_avg": 7.9, "humidity": 83.0},
    8:  {"temp_mean": 24.1, "temp_max": 27.6, "temp_min": 21.4, "rain_daily_avg": 5.5, "humidity": 84.0},
    9:  {"temp_mean": 25.0, "temp_max": 29.4, "temp_min": 20.8, "rain_daily_avg": 5.1, "humidity": 79.0},
    10: {"temp_mean": 25.3, "temp_max": 31.4, "temp_min": 18.8, "rain_daily_avg": 2.8, "humidity": 65.0},
    11: {"temp_mean": 22.9, "temp_max": 30.1, "temp_min": 14.9, "rain_daily_avg": 0.8, "humidity": 58.0},
    12: {"temp_mean": 20.8, "temp_max": 28.9, "temp_min": 12.1, "rain_daily_avg": 0.2, "humidity": 55.0},
}

DEFAULT_LOCATION_METADATA: Dict[str, Dict[str, float]] = {
    "Pune": {
        "latitude": 18.5204,
        "longitude": 73.8567,
        "elevation_m": 560.0,
        "slope_deg": 2.4,
        "drainage_index": 0.58,
    },
    "Mumbai": {
        "latitude": 19.0760,
        "longitude": 72.8777,
        "elevation_m": 14.0,
        "slope_deg": 0.8,
        "drainage_index": 0.42,
    },
    "Nagpur": {
        "latitude": 21.1458,
        "longitude": 79.0882,
        "elevation_m": 310.0,
        "slope_deg": 1.5,
        "drainage_index": 0.62,
    },
}


# ============================================================================
# 5. OFFICIAL INDIAN CPCB NATIONAL AIR QUALITY INDEX (NAQI) BREAKPOINTS
# ============================================================================
# Format: Pollutant -> List of (C_low, C_high, I_low, I_high)
CPCB_AQI_BREAKPOINTS: Dict[str, List[Tuple[float, float, int, int]]] = {
    "pm25_ugm3": [
        (0.0, 30.0, 0, 50),
        (30.0, 60.0, 51, 100),
        (60.0, 90.0, 101, 200),
        (90.0, 120.0, 201, 300),
        (120.0, 250.0, 301, 400),
        (250.0, 2000.0, 401, 500),
    ],
    "pm10_ugm3": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 250.0, 101, 200),
        (250.0, 350.0, 201, 300),
        (350.0, 430.0, 301, 400),
        (430.0, 3000.0, 401, 500),
    ],
    "no2_ugm3": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 180.0, 101, 200),
        (180.0, 280.0, 201, 300),
        (280.0, 400.0, 301, 400),
        (400.0, 1500.0, 401, 500),
    ],
    "so2_ugm3": [
        (0.0, 40.0, 0, 50),
        (40.0, 80.0, 51, 100),
        (80.0, 380.0, 101, 200),
        (380.0, 800.0, 201, 300),
        (800.0, 1600.0, 301, 400),
        (1600.0, 3000.0, 401, 500),
    ],
    "co_mgm3": [
        (0.0, 1.0, 0, 50),
        (1.0, 2.0, 51, 100),
        (2.0, 10.0, 101, 200),
        (10.0, 17.0, 201, 300),
        (17.0, 34.0, 301, 400),
        (34.0, 100.0, 401, 500),
    ],
    "o3_ugm3": [
        (0.0, 50.0, 0, 50),
        (50.0, 100.0, 51, 100),
        (100.0, 168.0, 101, 200),
        (168.0, 208.0, 201, 300),
        (208.0, 748.0, 301, 400),
        (748.0, 1500.0, 401, 500),
    ],
}


# ============================================================================
# 6. CLIMATE RISK SCORE CONFIGURATION (MODULE 7)
# ============================================================================
# Default weights (illustrative starting assumptions; configurable at runtime)
DEFAULT_RISK_WEIGHTS: Dict[str, float] = {
    "heat": 0.25,
    "flood": 0.30,
    "air_quality": 0.20,
    "water_stress": 0.25,
}

# Risk category thresholds (0-100)
DEFAULT_RISK_THRESHOLDS: List[Tuple[float, float, str]] = [
    (0.0, 20.0, "Very Low"),
    (20.0, 40.0, "Low"),
    (40.0, 60.0, "Moderate"),
    (60.0, 80.0, "High"),
    (80.0, 100.0, "Very High"),
]

# Hazard-level 4-tier or 5-tier label mapping
def score_to_risk_level(score: float, thresholds: List[Tuple[float, float, str]] = None) -> str:
    """Convert a 0-100 hazard or composite score into a documented risk category."""
    active_thresholds = thresholds or DEFAULT_RISK_THRESHOLDS
    clamped = max(0.0, min(100.0, float(score)))
    for low, high, label in active_thresholds:
        if low <= clamped <= high:
            return label
    return "Very High" if clamped > 80.0 else "Very Low"

