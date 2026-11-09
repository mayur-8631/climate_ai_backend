"""
ClimateTwin AI — Pune Pilot Climatological Reference Dataset & Target Proxy Definitions
Module: ml_engine/reference_data.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Scientific Transparency Statement:
----------------------------------
In offline environments where live API fetches (Open-Meteo / NASA POWER / CPCB) are
unavailable, this module generates a deterministic, physically consistent multi-year
daily environmental dataset for Pune, Maharashtra (2022-01-01 to 2026-10-31, 1,765 days)
anchored to IMD 30-year monthly climatological normals (`PUNE_MONTHLY_CLIMATOLOGY`) and
CPCB seasonal air-quality profiles.

Target Proxy Formulations (0-100 scale):
1. `heat_risk_target`: Meteorological Heat Hazard Proxy combining NOAA Apparent Temperature
   (Heat Index), IMD heatwave anomaly above monthly normal, wet-bulb thermal stress,
   and 3-day thermal persistence.
2. `flood_risk_target`: Hydrometeorological Rainfall-Runoff Flood Hazard Proxy combining
   daily rainfall, peak hourly rainfall intensity, 3-day and 7-day antecedent rainfall,
   surface soil saturation, and topographic drainage impedance.
3. `air_quality_risk_target`: Official Indian CPCB National Air Quality Index (NAQI)
   mapped to a 0-100 hazard scale alongside dispersion stagnation effects.
4. `water_stress_risk_target`: Surface Hydro-Climatic Water-Stress Proxy combining
   30-day cumulative evapotranspiration-precipitation deficit, root-zone soil moisture
   depletion, and vapor pressure deficit.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from ml_engine.config import (
    DEFAULT_LOCATION_METADATA,
    PUNE_MONTHLY_CLIMATOLOGY,
    RANDOM_SEED,
    RAW_DATA_DIR,
)
from ml_engine.feature_engineering import (
    EnvironmentalFeatureEngineer,
    compute_heat_index_celsius,
    compute_wet_bulb_stull,
)


def compute_heat_hazard_proxy(df: pd.DataFrame) -> pd.Series:
    """
    Documented Meteorological Heat Hazard Proxy (0-100).
    NOTE: Represents environmental thermal hazard, NOT medically validated illness/mortality.
    """
    hi = compute_heat_index_celsius(df["temp_max_c"], df["humidity_pct"])
    wb = compute_wet_bulb_stull(df["temperature_c"], df["humidity_pct"])
    months = pd.to_datetime(df["timestamp"]).dt.month
    clim_max = months.map(lambda m: PUNE_MONTHLY_CLIMATOLOGY[int(m)]["temp_max"])
    tmax_anom = (df["temp_max_c"] - clim_max).clip(lower=-5.0)

    # 3-day persistence of high temperatures
    tmax_3d = df["temp_max_c"].rolling(window=3, min_periods=1).mean()

    # Component scores mapped to 0-100
    hi_score = ((hi - 24.0) / (48.0 - 24.0) * 100.0).clip(0.0, 100.0)
    tmax_score = (( tmax_3d - 26.0) / (44.0 - 26.0) * 100.0).clip(0.0, 100.0)
    wb_score = ((wb - 16.0) / (31.0 - 16.0) * 100.0).clip(0.0, 100.0)
    anom_bonus = (tmax_anom * 3.2).clip(-8.0, 22.0)
    wind_cooling = ((df["wind_speed_kmh"] - 10.0) * 0.25).clip(-3.0, 5.0)

    raw_score = 0.42 * hi_score + 0.33 * tmax_score + 0.25 * wb_score + anom_bonus - wind_cooling
    return raw_score.clip(0.0, 100.0).round(2)


def compute_flood_hazard_proxy(df: pd.DataFrame) -> pd.Series:
    """
    Documented Hydrometeorological Rainfall-Runoff Flood Hazard Proxy (0-100).
    NOTE: High rainfall alone does not guarantee flooding. This proxy combines
    current rainfall, hourly intensity, 3d/7d cumulative antecedent rainfall,
    soil moisture saturation, and local drainage/topography.
    """
    rain_1d = df["rainfall_mm"].clip(lower=0.0)
    rain_int = df["rainfall_intensity_mm_hr"].clip(lower=0.0)
    rain_3d = rain_1d.rolling(window=3, min_periods=1).sum()
    rain_7d = rain_1d.rolling(window=7, min_periods=1).sum()
    soil_m = df["soil_moisture"].clip(0.05, 0.98)
    drainage = df.get("drainage_index", pd.Series(0.58, index=df.index)).clip(0.1, 0.95)

    # Non-linear runoff response: moderate rain on dry soil -> low hazard;
    # intense rain on saturated soil with poor drainage -> high hazard.
    direct_rain_score = (100.0 * (1.0 - np.exp(-rain_1d / 75.0))).clip(0.0, 100.0)
    intensity_score = (100.0 * (1.0 - np.exp(-rain_int / 32.0))).clip(0.0, 100.0)
    antecedent_score = (100.0 * (1.0 - np.exp(-rain_3d / 140.0)) * 0.65 + 100.0 * (1.0 - np.exp(-rain_7d / 240.0)) * 0.35).clip(0.0, 100.0)

    saturation_multiplier = 0.55 + 0.70 * (soil_m ** 1.3)
    drainage_multiplier = 0.75 + 0.55 * (1.0 - drainage)

    combined = (
        0.30 * direct_rain_score
        + 0.30 * intensity_score
        + 0.40 * antecedent_score
    ) * saturation_multiplier * drainage_multiplier

    return combined.clip(0.0, 100.0).round(2)


def compute_air_quality_hazard_proxy(df: pd.DataFrame) -> pd.Series:
    """
    Documented CPCB NAQI-Calibrated Air Quality Hazard Score (0-100).
    Maps official Indian CPCB National Air Quality Index (0-500) into a 0-100
    hazard scale with piecewise sensitivity for Moderate/Poor/Very Poor/Severe regimes.
    """
    eng = EnvironmentalFeatureEngineer()
    enriched = eng.transform(df)
    cpcb_aqi = enriched["cpcb_calculated_aqi"].clip(0.0, 500.0)
    multi_pol = enriched["pollutant_load_index"].clip(0.0, 1.0) * 100.0
    stagnation = enriched["wind_stagnation_index"]

    # Piecewise linear mapping from 0-500 NAQI to 0-100 risk score:
    # NAQI 0-50 (Good) -> 0-18
    # NAQI 51-100 (Satisfactory) -> 18-36
    # NAQI 101-200 (Moderate) -> 36-62
    # NAQI 201-300 (Poor) -> 62-82
    # NAQI 301-500 (Very Poor / Severe) -> 82-100
    aqi_hazard = np.interp(
        cpcb_aqi.to_numpy(dtype=float),
        [0.0, 50.0, 100.0, 200.0, 300.0, 500.0],
        [0.0, 18.0, 36.0, 62.0, 82.0, 100.0],
    )
    score = 0.82 * pd.Series(aqi_hazard, index=df.index) + 0.14 * multi_pol + 4.0 * stagnation
    return score.clip(0.0, 100.0).round(2)


def compute_water_stress_hazard_proxy(df: pd.DataFrame) -> pd.Series:
    """
    Documented Environmental Hydro-Climatic Water-Stress Proxy (0-100).
    NOTE: Reflects environmental moisture deficit & evaporative demand, NOT municipal
    reservoir storage or piped water supply shortage.
    """
    rain_30d = df["rainfall_mm"].clip(lower=0.0).rolling(window=30, min_periods=1).sum()
    et_30d = df["evapotranspiration_mm"].clip(lower=0.5).rolling(window=30, min_periods=1).sum()
    soil_m = df["soil_moisture"].clip(0.05, 0.95)
    rh = df["humidity_pct"].clip(5.0, 100.0)
    tmax = df["temp_max_c"]

    # Soil moisture deficit (0 when soil_m >= 0.65, up to 100 when soil_m -> 0.08)
    soil_deficit_score = ((0.62 - soil_m) / 0.54 * 100.0).clip(0.0, 100.0)

    # 30-day climatic water balance deficit (ET_30d - Rain_30d)
    net_deficit_30d = (et_30d - rain_30d).clip(lower=-50.0, upper=220.0)
    balance_score = ((net_deficit_30d + 20.0) / 220.0 * 100.0).clip(0.0, 100.0)

    # Atmospheric evaporative stress
    atm_stress = (((tmax - 24.0) / 20.0 * 60.0) + ((65.0 - rh) / 55.0 * 40.0)).clip(0.0, 100.0)

    score = 0.45 * soil_deficit_score + 0.35 * balance_score + 0.20 * atm_stress
    return score.clip(0.0, 100.0).round(2)


def generate_pune_climatological_dataset(
    save_path: Optional[Path] = None,
    seed: int = RANDOM_SEED,
    inject_realistic_missingness: bool = False,
) -> pd.DataFrame:
    """
    Generate or load the Pune Pilot Climatological Reference Dataset (2022-01-01 to 2026-10-31).
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2022-01-01", "2026-10-31", freq="D")
    n = len(dates)

    meta = DEFAULT_LOCATION_METADATA["Pune"]
    records = []

    # Autoregressive state variables for realistic day-to-day weather persistence
    temp_anom_state = 0.0
    soil_moisture_state = 0.35
    pm25_state = 45.0

    for dt in dates:
        m = int(dt.month)
        clim = PUNE_MONTHLY_CLIMATOLOGY[m]

        # AR(1) thermal anomaly with occasional summer heatwave pulses
        heatwave_pulse = rng.choice([0.0, 3.2, 5.0], p=[0.90, 0.07, 0.03]) if m in (3, 4, 5) else 0.0
        temp_anom_state = 0.68 * temp_anom_state + rng.normal(0.0, 1.1) + 0.32 * heatwave_pulse

        temp_c = round(clim["temp_mean"] + temp_anom_state, 2)
        dtr = max(4.0, rng.normal(clim["temp_max"] - clim["temp_min"], 1.4))
        temp_max_c = round(temp_c + 0.52 * dtr + rng.normal(0.0, 0.5), 2)
        temp_min_c = round(temp_c - 0.48 * dtr + rng.normal(0.0, 0.5), 2)

        # Rainfall generation (continuous mixture across light, heavy 25-85mm, and extreme >85mm spells)
        if m in (6, 7, 8, 9):
            wet_prob = 0.74 if m in (7, 8) else 0.58
            if rng.random() < wet_prob:
                u_spell = rng.random()
                if u_spell < 0.06:
                    rain_mm = float(rng.uniform(85.0, 190.0))
                elif u_spell < 0.24:
                    rain_mm = float(rng.uniform(25.0, 85.0))
                else:
                    rain_mm = float(rng.gamma(shape=1.5, scale=clim["rain_daily_avg"] * 1.5))
            else:
                rain_mm = 0.0
        elif m in (5, 10, 11):
            rain_mm = float(rng.gamma(1.1, clim["rain_daily_avg"] * 2.5)) if rng.random() < 0.22 else 0.0
        else:
            rain_mm = float(rng.exponential(2.5)) if rng.random() < 0.04 else 0.0

        rain_mm = round(max(0.0, rain_mm), 2)
        # Peak hourly intensity (convective pre/post-monsoon bursts vs steady monsoon rain)
        if rain_mm > 0:
            convective_factor = rng.uniform(0.24, 0.48) if m in (5, 6, 9, 10) else rng.uniform(0.18, 0.35)
            rain_intensity = round(rain_mm * convective_factor, 2)
        else:
            rain_intensity = 0.0

        # Relative humidity coupled to climatology and rainfall
        rh_boost = min(22.0, rain_mm * 0.35) - temp_anom_state * 1.8
        humidity_pct = round(float(np.clip(clim["humidity"] + rh_boost + rng.normal(0.0, 5.5), 14.0, 99.0)), 2)

        # Wind speed & pressure
        base_wind = 15.5 if m in (6, 7, 8) else (11.0 if m in (3, 4, 5) else 7.2)
        wind_speed_kmh = round(float(np.clip(rng.gamma(shape=2.4, scale=base_wind / 2.4), 1.2, 58.0)), 2)
        wind_direction_deg = round(float(rng.normal(255.0, 25.0) if m in (6, 7, 8, 9) else rng.uniform(45.0, 315.0)) % 360.0, 1)
        pressure_hpa = round(float(948.0 - 0.12 * rain_mm + (5.0 if m in (12, 1) else -3.5 if m in (6, 7) else 0.0) + rng.normal(0.0, 1.8)), 2)

        # Evapotranspiration (mm/day) and Soil Moisture (0-1 water balance)
        et_mm = round(
            float(
                np.clip(
                    0.0023 * 15.2 * (temp_c + 17.8) * np.sqrt(max(temp_max_c - temp_min_c, 2.0))
                    * (1.0 + 0.012 * wind_speed_kmh)
                    * (1.15 - 0.004 * humidity_pct),
                    1.2,
                    9.8,
                )
            ),
            2,
        )
        soil_moisture_state = float(
            np.clip(
                0.93 * soil_moisture_state + 0.0055 * rain_mm - 0.0048 * et_mm + rng.normal(0.0, 0.01),
                0.08,
                0.92,
            )
        )
        soil_moisture = round(soil_moisture_state, 3)

        # Air Quality Pollutants (Winter inversion buildup vs Monsoon wet scavenging)
        seasonal_pm25_base = 76.0 if m in (11, 12, 1, 2) else (48.0 if m in (3, 4, 5, 10) else 22.0)
        wet_scavenging = np.exp(-rain_mm / 25.0)
        wind_ventilation = 1.0 / (1.0 + 0.03 * (wind_speed_kmh - 8.0))
        target_pm25 = seasonal_pm25_base * wet_scavenging * np.clip(wind_ventilation, 0.55, 1.55)
        pm25_state = float(np.clip(0.55 * pm25_state + 0.45 * target_pm25 + rng.normal(0.0, 8.5), 6.0, 290.0))

        pm25_ugm3 = round(pm25_state, 2)
        pm10_ugm3 = round(float(np.clip(pm25_ugm3 * rng.uniform(1.65, 2.35) + (18.0 if m in (3, 4, 5) else 5.0), 15.0, 520.0)), 2)
        no2_ugm3 = round(float(np.clip(18.0 + 0.38 * pm25_ugm3 + rng.normal(0.0, 6.0), 6.0, 165.0)), 2)
        so2_ugm3 = round(float(np.clip(8.0 + 0.12 * pm25_ugm3 + rng.normal(0.0, 3.0), 3.0, 85.0)), 2)
        co_mgm3 = round(float(np.clip(0.45 + 0.014 * pm25_ugm3 + rng.normal(0.0, 0.18), 0.2, 6.5)), 2)
        o3_ugm3 = round(float(np.clip(22.0 + 1.8 * max(temp_max_c - 25.0, 0.0) - 0.25 * rain_mm + rng.normal(0.0, 7.0), 8.0, 155.0)), 2)

        records.append(
            {
                "timestamp": dt.strftime("%Y-%m-%dT12:00:00"),
                "location": "Pune",
                "latitude": meta["latitude"],
                "longitude": meta["longitude"],
                "elevation_m": meta["elevation_m"],
                "slope_deg": meta["slope_deg"],
                "drainage_index": meta["drainage_index"],
                "temperature_c": temp_c,
                "temp_max_c": temp_max_c,
                "temp_min_c": temp_min_c,
                "humidity_pct": humidity_pct,
                "wind_speed_kmh": wind_speed_kmh,
                "wind_direction_deg": wind_direction_deg,
                "pressure_hpa": pressure_hpa,
                "rainfall_mm": rain_mm,
                "rainfall_intensity_mm_hr": rain_intensity,
                "soil_moisture": soil_moisture,
                "evapotranspiration_mm": et_mm,
                "pm25_ugm3": pm25_ugm3,
                "pm10_ugm3": pm10_ugm3,
                "no2_ugm3": no2_ugm3,
                "so2_ugm3": so2_ugm3,
                "co_mgm3": co_mgm3,
                "o3_ugm3": o3_ugm3,
            }
        )

    df = pd.DataFrame(records)

    # Compute transparent hazard proxy targets on the clean physical series
    df["heat_risk_target"] = compute_heat_hazard_proxy(df)
    df["flood_risk_target"] = compute_flood_hazard_proxy(df)
    df["air_quality_risk_target"] = compute_air_quality_hazard_proxy(df)
    df["water_stress_risk_target"] = compute_water_stress_hazard_proxy(df)

    if inject_realistic_missingness:
        # Inject ~1.5% realistic sensor dropouts in raw features (never in targets)
        for col in ["humidity_pct", "wind_speed_kmh", "pm25_ugm3", "so2_ugm3", "soil_moisture"]:
            drop_idx = rng.choice(n, size=int(0.015 * n), replace=False)
            df.loc[drop_idx, col] = np.nan

    target_file = save_path or (RAW_DATA_DIR / "pune_environmental_timeseries.csv")
    target_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(target_file, index=False)
    return df


def load_or_create_pilot_dataset(csv_path: Optional[Path] = None) -> pd.DataFrame:
    """Load the Pune pilot environmental dataset from disk or create it if absent."""
    target_file = csv_path or (RAW_DATA_DIR / "pune_environmental_timeseries.csv")
    if target_file.exists():
        return pd.read_csv(target_file)
    return generate_pune_climatological_dataset(save_path=target_file)
