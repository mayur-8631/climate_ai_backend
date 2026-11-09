"""
ClimateTwin AI — Module 2: Environmental Feature Engineering
Module: ml_engine/feature_engineering.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Responsibilities:
- Derive physically grounded meteorological, hydrological, atmospheric, and
  hydro-climatic features from validated environmental observations.
- Prevent target leakage in lagged and rolling time-series features (strictly causal).
- Gracefully handle single-row real-time API payloads as well as multi-year
  historical time-series DataFrames.
- Maintain a transparent feature availability and calculation catalog.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from ml_engine.config import CPCB_AQI_BREAKPOINTS, PUNE_MONTHLY_CLIMATOLOGY


# ============================================================================
# DOCUMENTED FEATURE CATALOG
# ============================================================================
FEATURE_CATALOG: Dict[str, str] = {
    # Thermal & Heat Features
    "diurnal_temp_range_c": "temp_max_c - temp_min_c (°C)",
    "heat_index_c": "NOAA Rothfusz/Steadman apparent temperature combining temperature_c and humidity_pct (°C)",
    "wet_bulb_temp_c": "Stull (2011) empirical psychrometric wet-bulb temperature (°C)",
    "vapor_pressure_deficit_kpa": "Saturation vapor pressure minus actual vapor pressure via Tetens equation (kPa)",
    "temp_anomaly_c": "temperature_c minus monthly climatological normal mean temperature (°C)",
    "temp_max_anomaly_c": "temp_max_c minus monthly climatological normal maximum temperature (°C)",
    "temp_lag_1d": "1-day lagged mean temperature (°C, strictly causal)",
    "temp_lag_3d": "3-day lagged mean temperature (°C, strictly causal)",
    "temp_rolling_3d_mean": "Causal 3-day trailing moving average of temperature_c (°C)",
    "temp_rolling_7d_mean": "Causal 7-day trailing moving average of temperature_c (°C)",
    "temp_max_rolling_3d_mean": "Causal 3-day trailing moving average of temp_max_c (°C)",
    # Rainfall & Hydrological Features
    "rainfall_lag_1d": "1-day lagged daily rainfall (mm, strictly causal)",
    "rainfall_lag_3d": "3-day lagged daily rainfall (mm, strictly causal)",
    "rainfall_rolling_3d_sum": "Causal 3-day cumulative rainfall accumulation (mm)",
    "rainfall_rolling_7d_sum": "Causal 7-day cumulative rainfall accumulation (mm)",
    "rainfall_rolling_14d_sum": "Causal 14-day cumulative rainfall accumulation (mm)",
    "rainfall_rolling_30d_sum": "Causal 30-day cumulative rainfall accumulation (mm)",
    "rainfall_anomaly_mm": "Daily rainfall minus monthly climatological daily average rainfall (mm)",
    "rainfall_intensity_ratio": "Peak hourly rainfall_intensity_mm_hr divided by max(daily rainfall_mm / 24, 0.5)",
    "runoff_potential_index": "Composite surface saturation & drainage impedance proxy: (rainfall_rolling_3d_sum * (0.5 + soil_moisture)) / (0.3 + drainage_index)",
    "topographic_flood_susceptibility": "Low-elevation & low-drainage vulnerability factor: (1 - drainage_index) * exp(-max(elevation_m - 500, 0) / 400)",
    # Air Quality & Dispersion Features
    "pm_ratio_25_to_10": "Ratio of fine-to-coarse particulate matter: pm25_ugm3 / max(pm10_ugm3, 1.0)",
    "pm25_lag_1d": "1-day lagged PM2.5 concentration (µg/m³, strictly causal)",
    "pm25_rolling_3d_mean": "Causal 3-day trailing moving average of PM2.5 (µg/m³)",
    "wind_stagnation_index": "Atmospheric stagnation proxy: 1.0 / (1.0 + 0.15 * wind_speed_kmh)",
    "cpcb_calculated_aqi": "Official Indian CPCB National Air Quality Index (0-500) computed from available pollutant sub-indices",
    "pollutant_load_index": "Normalized multi-pollutant burden combining PM2.5, PM10, NO2, SO2, CO, and O3",
    # Water Stress & Drought Features
    "soil_moisture_lag_1d": "1-day lagged volumetric soil moisture (0-1, strictly causal)",
    "soil_moisture_rolling_7d_mean": "Causal 7-day trailing moving average of soil moisture (0-1)",
    "evap_rolling_7d_sum": "Causal 7-day cumulative reference evapotranspiration (mm)",
    "evap_rolling_30d_sum": "Causal 30-day cumulative reference evapotranspiration (mm)",
    "hydro_water_deficit_7d_mm": "7-day cumulative evapotranspiration minus 7-day cumulative rainfall (mm)",
    "hydro_water_deficit_30d_mm": "30-day cumulative evapotranspiration minus 30-day cumulative rainfall (mm)",
    "aridity_stress_index": "Normalized evaporative demand vs moisture supply ratio",
    # Seasonal & Calendar Features
    "month": "Calendar month (1-12)",
    "day_of_year": "Day of year (1-366)",
    "sin_day_of_year": "Cyclical annual sine encoding: sin(2 * pi * day_of_year / 365.25)",
    "cos_day_of_year": "Cyclical annual cosine encoding: cos(2 * pi * day_of_year / 365.25)",
    "is_summer_season": "Binary indicator for Indian Pre-Monsoon / Summer season (March-May)",
    "is_monsoon_season": "Binary indicator for Indian SW Monsoon season (June-September)",
    "is_winter_inversion": "Binary indicator for Winter thermal inversion season (November-February)",
}


def compute_cpcb_sub_index(value: float, breakpoints: List[Tuple[float, float, int, int]]) -> float:
    """Compute official CPCB sub-index for a single pollutant observation."""
    if pd.isna(value) or value < 0:
        return np.nan
    for c_low, c_high, i_low, i_high in breakpoints:
        if c_low <= value <= c_high:
            return float(((i_high - i_low) / (c_high - c_low)) * (value - c_low) + i_low)
    # If above highest breakpoint
    _, _, _, max_i = breakpoints[-1]
    return float(max_i)


def compute_heat_index_celsius(temp_c: pd.Series, rh_pct: pd.Series) -> pd.Series:
    """
    Calculate NOAA/Steadman Apparent Temperature (Heat Index) in Celsius.
    Valid across all temperature ranges (uses Steadman simple formula below 26.7°C
    and Rothfusz regression with low/high RH adjustments at or above 26.7°C).
    """
    t_f = temp_c * 1.8 + 32.0
    rh = rh_pct.clip(0.0, 100.0)

    # Steadman simple approximation
    hi_simple = 0.5 * (t_f + 61.0 + ((t_f - 68.0) * 1.2) + (rh * 0.094))

    # Full Rothfusz regression
    hi_full = (
        -42.379
        + 2.04901523 * t_f
        + 10.14333127 * rh
        - 0.22475541 * t_f * rh
        - 0.00683783 * (t_f ** 2)
        - 0.05481717 * (rh ** 2)
        + 0.00122874 * (t_f ** 2) * rh
        + 0.00085282 * t_f * (rh ** 2)
        - 0.00000199 * (t_f ** 2) * (rh ** 2)
    )

    # Low humidity adjustment (RH < 13% and 80°F <= T <= 112°F)
    low_rh_mask = (rh < 13.0) & (t_f >= 80.0) & (t_f <= 112.0)
    adj_low = ((13.0 - rh) / 4.0) * np.sqrt((17.0 - (t_f - 95.0).abs().clip(upper=17.0)) / 17.0)
    hi_full = np.where(low_rh_mask, hi_full - adj_low, hi_full)

    # High humidity adjustment (RH > 85% and 80°F <= T <= 87°F)
    high_rh_mask = (rh > 85.0) & (t_f >= 80.0) & (t_f <= 87.0)
    adj_high = ((rh - 85.0) / 10.0) * ((87.0 - t_f) / 5.0)
    hi_full = np.where(high_rh_mask, hi_full + adj_high, hi_full)

    hi_f = np.where(hi_simple < 80.0, hi_simple, hi_full)
    return pd.Series((hi_f - 32.0) * (5.0 / 9.0), index=temp_c.index)


def compute_wet_bulb_stull(temp_c: pd.Series, rh_pct: pd.Series) -> pd.Series:
    """
    Calculate wet-bulb temperature (°C) using Stull (2011), Journal of Applied
    Meteorology and Climatology.
    """
    rh = rh_pct.clip(1.0, 100.0)
    t = temp_c
    tw = (
        t * np.arctan(0.151977 * np.sqrt(rh + 8.313659))
        + np.arctan(t + rh)
        - np.arctan(rh - 1.676331)
        + 0.00391838 * (rh ** 1.5) * np.arctan(0.023101 * rh)
        - 4.686035
    )
    return pd.Series(tw, index=temp_c.index)


class EnvironmentalFeatureEngineer:
    """
    Extracts domain-specific environmental features while tracking feature availability
    and preventing temporal target leakage.
    """

    def __init__(self, climatology: Optional[Dict[int, Dict[str, float]]] = None) -> None:
        self.climatology = climatology or PUNE_MONTHLY_CLIMATOLOGY
        self.last_availability_report_: Dict[str, Any] = {}

    def transform(
        self,
        df: pd.DataFrame,
        return_report: bool = False,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]] | pd.DataFrame:
        """
        Compute derived meteorological, hydrological, air-quality, and water-stress
        features on a validated DataFrame.
        Strictly causal: uses only current and past rows (`t-k ... t`), never `t+1`.
        """
        feat_df = df.copy()

        # Track raw input column availability before deriving features
        raw_present = [col for col in feat_df.columns if feat_df[col].notna().any()]

        # Ensure timestamp is datetime and sort chronologically within each location
        feat_df["timestamp"] = pd.to_datetime(feat_df["timestamp"], errors="coerce").fillna(
            pd.Timestamp("2026-11-09T12:00:00")
        )
        original_index = feat_df.index
        feat_df = feat_df.sort_values(["location", "timestamp"])

        # ------------------------------------------------------------------
        # 1. SEASONAL & CALENDAR FEATURES
        # ------------------------------------------------------------------
        feat_df["month"] = feat_df["timestamp"].dt.month.astype(int)
        feat_df["day_of_year"] = feat_df["timestamp"].dt.dayofyear.astype(int)
        feat_df["sin_day_of_year"] = np.sin(2.0 * np.pi * feat_df["day_of_year"] / 365.25)
        feat_df["cos_day_of_year"] = np.cos(2.0 * np.pi * feat_df["day_of_year"] / 365.25)
        feat_df["is_summer_season"] = feat_df["month"].isin([3, 4, 5]).astype(int)
        feat_df["is_monsoon_season"] = feat_df["month"].isin([6, 7, 8, 9]).astype(int)
        feat_df["is_winter_inversion"] = feat_df["month"].isin([11, 12, 1, 2]).astype(int)

        # Monthly climatological normals
        clim_temp_mean = feat_df["month"].map(lambda m: self.climatology[int(m)]["temp_mean"])
        clim_temp_max = feat_df["month"].map(lambda m: self.climatology[int(m)]["temp_max"])
        clim_rain_daily = feat_df["month"].map(lambda m: self.climatology[int(m)]["rain_daily_avg"])

        # Ensure core numeric columns exist (with sensible climatological fallback if totally absent)
        if "temperature_c" not in feat_df.columns:
            feat_df["temperature_c"] = clim_temp_mean
        if "temp_max_c" not in feat_df.columns:
            feat_df["temp_max_c"] = feat_df["temperature_c"] + 5.0
        if "temp_min_c" not in feat_df.columns:
            feat_df["temp_min_c"] = feat_df["temperature_c"] - 5.0
        if "humidity_pct" not in feat_df.columns:
            feat_df["humidity_pct"] = feat_df["month"].map(lambda m: self.climatology[int(m)]["humidity"])
        if "wind_speed_kmh" not in feat_df.columns:
            feat_df["wind_speed_kmh"] = 10.0
        if "pressure_hpa" not in feat_df.columns:
            feat_df["pressure_hpa"] = 950.0
        if "rainfall_mm" not in feat_df.columns:
            feat_df["rainfall_mm"] = 0.0
        if "rainfall_intensity_mm_hr" not in feat_df.columns:
            # Estimate peak hourly intensity when only daily rainfall is provided
            feat_df["rainfall_intensity_mm_hr"] = (feat_df["rainfall_mm"] * 0.28).clip(lower=0.0)

        # ------------------------------------------------------------------
        # 2. THERMAL & HEAT-HAZARD FEATURES
        # ------------------------------------------------------------------
        feat_df["diurnal_temp_range_c"] = (feat_df["temp_max_c"] - feat_df["temp_min_c"]).clip(lower=0.0)
        feat_df["heat_index_c"] = compute_heat_index_celsius(feat_df["temp_max_c"], feat_df["humidity_pct"])
        feat_df["wet_bulb_temp_c"] = compute_wet_bulb_stull(feat_df["temperature_c"], feat_df["humidity_pct"])

        # Saturation & actual vapor pressure (Tetens formula, kPa)
        es_kpa = 0.61078 * np.exp((17.27 * feat_df["temperature_c"]) / (feat_df["temperature_c"] + 237.3))
        ea_kpa = es_kpa * (feat_df["humidity_pct"].clip(0.0, 100.0) / 100.0)
        feat_df["vapor_pressure_deficit_kpa"] = (es_kpa - ea_kpa).clip(lower=0.0)

        # Climatological temperature anomalies
        feat_df["temp_anomaly_c"] = feat_df["temperature_c"] - clim_temp_mean
        feat_df["temp_max_anomaly_c"] = feat_df["temp_max_c"] - clim_temp_max

        # Causal lagged & rolling temperature features (grouped by location)
        grp_temp = feat_df.groupby("location")["temperature_c"]
        grp_tmax = feat_df.groupby("location")["temp_max_c"]

        feat_df["temp_lag_1d"] = grp_temp.shift(1).fillna(feat_df["temperature_c"])
        feat_df["temp_lag_3d"] = grp_temp.shift(3).fillna(feat_df["temp_lag_1d"])
        feat_df["temp_rolling_3d_mean"] = (
            grp_temp.transform(lambda s: s.rolling(window=3, min_periods=1).mean())
        )
        feat_df["temp_rolling_7d_mean"] = (
            grp_temp.transform(lambda s: s.rolling(window=7, min_periods=1).mean())
        )
        feat_df["temp_max_rolling_3d_mean"] = (
            grp_tmax.transform(lambda s: s.rolling(window=3, min_periods=1).mean())
        )

        # ------------------------------------------------------------------
        # 3. RAINFALL & FLOOD-HAZARD FEATURES
        # ------------------------------------------------------------------
        grp_rain = feat_df.groupby("location")["rainfall_mm"]
        feat_df["rainfall_lag_1d"] = grp_rain.shift(1).fillna(0.0)
        feat_df["rainfall_lag_3d"] = grp_rain.shift(3).fillna(0.0)

        # Support single-row API payloads that supply pre-aggregated cumulative rainfall
        if "cumulative_rainfall_3d_mm" in feat_df.columns:
            feat_df["rainfall_rolling_3d_sum"] = feat_df["cumulative_rainfall_3d_mm"]
        else:
            feat_df["rainfall_rolling_3d_sum"] = grp_rain.transform(
                lambda s: s.rolling(window=3, min_periods=1).sum()
            )

        if "cumulative_rainfall_7d_mm" in feat_df.columns:
            feat_df["rainfall_rolling_7d_sum"] = feat_df["cumulative_rainfall_7d_mm"]
        else:
            feat_df["rainfall_rolling_7d_sum"] = grp_rain.transform(
                lambda s: s.rolling(window=7, min_periods=1).sum()
            )

        feat_df["rainfall_rolling_14d_sum"] = grp_rain.transform(
            lambda s: s.rolling(window=14, min_periods=1).sum()
        )
        feat_df["rainfall_rolling_30d_sum"] = grp_rain.transform(
            lambda s: s.rolling(window=30, min_periods=1).sum()
        )

        # If single-row inference only supplied rainfall_mm, scale 3d/7d/30d reasonably from current + climatology
        if len(feat_df) == 1:
            if "cumulative_rainfall_3d_mm" not in df.columns:
                feat_df["rainfall_rolling_3d_sum"] = (
                    feat_df["rainfall_mm"] * 1.35 + 2.0 * clim_rain_daily
                )
            if "cumulative_rainfall_7d_mm" not in df.columns:
                feat_df["rainfall_rolling_7d_sum"] = (
                    feat_df["rainfall_mm"] * 1.85 + 6.0 * clim_rain_daily
                )
            if "cumulative_rainfall_30d_mm" not in df.columns:
                feat_df["rainfall_rolling_30d_sum"] = (
                    feat_df["rainfall_rolling_7d_sum"] + 23.0 * clim_rain_daily
                )

        feat_df["rainfall_anomaly_mm"] = feat_df["rainfall_mm"] - clim_rain_daily
        feat_df["rainfall_intensity_ratio"] = feat_df["rainfall_intensity_mm_hr"] / np.maximum(
            feat_df["rainfall_mm"] / 24.0, 0.5
        )

        # Soil moisture and evapotranspiration estimation when missing from source API
        if "soil_moisture" not in feat_df.columns or feat_df["soil_moisture"].isna().all():
            # Physically grounded antecedent precipitation & humidity soil wetness proxy (0.08 - 0.92)
            wetness_from_rain = np.tanh(feat_df["rainfall_rolling_7d_sum"] / 90.0) * 0.55
            wetness_from_rh = (feat_df["humidity_pct"] / 100.0) * 0.35
            feat_df["soil_moisture"] = (0.08 + wetness_from_rain + wetness_from_rh).clip(0.05, 0.95)

        if "evapotranspiration_mm" not in feat_df.columns or feat_df["evapotranspiration_mm"].isna().all():
            # Hargreaves-inspired daily reference evapotranspiration (mm/day)
            feat_df["evapotranspiration_mm"] = (
                0.0023
                * 15.0
                * (feat_df["temperature_c"] + 17.8)
                * np.sqrt(feat_df["diurnal_temp_range_c"].clip(lower=2.0))
            ).clip(1.0, 12.0)

        # Topographical & hydrological interaction features
        elevation = feat_df.get("elevation_m", pd.Series(560.0, index=feat_df.index))
        drainage = feat_df.get("drainage_index", pd.Series(0.58, index=feat_df.index)).clip(0.1, 0.95)
        slope = feat_df.get("slope_deg", pd.Series(2.4, index=feat_df.index)).clip(0.1, 45.0)
        feat_df["elevation_m"] = elevation
        feat_df["drainage_index"] = drainage
        feat_df["slope_deg"] = slope

        feat_df["runoff_potential_index"] = (
            feat_df["rainfall_rolling_3d_sum"] * (0.5 + feat_df["soil_moisture"])
        ) / (0.3 + drainage)
        feat_df["topographic_flood_susceptibility"] = (1.0 - drainage) * np.exp(
            -np.maximum(elevation - 500.0, 0.0) / 400.0
        )

        # ------------------------------------------------------------------
        # 4. AIR-QUALITY & ATMOSPHERIC DISPERSION FEATURES
        # ------------------------------------------------------------------
        pollutant_defaults = {
            "pm25_ugm3": 38.0,
            "pm10_ugm3": 78.0,
            "no2_ugm3": 28.0,
            "so2_ugm3": 12.0,
            "co_mgm3": 0.9,
            "o3_ugm3": 42.0,
        }
        # If measured_aqi is supplied but individual pollutants are missing, infer approximate PM2.5/PM10
        if "measured_aqi" in feat_df.columns and feat_df["measured_aqi"].notna().any():
            aqi_val = feat_df["measured_aqi"]
            if "pm25_ugm3" not in feat_df.columns or feat_df["pm25_ugm3"].isna().all():
                feat_df["pm25_ugm3"] = (aqi_val * 0.45).clip(5.0, 500.0)
            if "pm10_ugm3" not in feat_df.columns or feat_df["pm10_ugm3"].isna().all():
                feat_df["pm10_ugm3"] = (aqi_val * 0.95).clip(10.0, 800.0)

        for pol_col, default_val in pollutant_defaults.items():
            if pol_col not in feat_df.columns:
                feat_df[pol_col] = default_val
            else:
                feat_df[pol_col] = feat_df[pol_col].fillna(default_val)

        feat_df["pm_ratio_25_to_10"] = feat_df["pm25_ugm3"] / np.maximum(feat_df["pm10_ugm3"], 1.0)
        grp_pm25 = feat_df.groupby("location")["pm25_ugm3"]
        feat_df["pm25_lag_1d"] = grp_pm25.shift(1).fillna(feat_df["pm25_ugm3"])
        feat_df["pm25_rolling_3d_mean"] = grp_pm25.transform(
            lambda s: s.rolling(window=3, min_periods=1).mean()
        )
        feat_df["wind_stagnation_index"] = 1.0 / (1.0 + 0.15 * feat_df["wind_speed_kmh"].clip(lower=0.0))

        # Calculate official CPCB sub-indices for all 6 criteria pollutants
        sub_index_cols = []
        for pol_col, bp_list in CPCB_AQI_BREAKPOINTS.items():
            sub_col = f"sub_index_{pol_col}"
            feat_df[sub_col] = feat_df[pol_col].map(lambda v: compute_cpcb_sub_index(v, bp_list))
            sub_index_cols.append(sub_col)

        feat_df["cpcb_calculated_aqi"] = feat_df[sub_index_cols].max(axis=1)
        feat_df["pollutant_load_index"] = feat_df[sub_index_cols].mean(axis=1) / 500.0

        # ------------------------------------------------------------------
        # 5. WATER-STRESS & HYDRO-CLIMATIC FEATURES
        # ------------------------------------------------------------------
        grp_sm = feat_df.groupby("location")["soil_moisture"]
        grp_et = feat_df.groupby("location")["evapotranspiration_mm"]

        feat_df["soil_moisture_lag_1d"] = grp_sm.shift(1).fillna(feat_df["soil_moisture"])
        feat_df["soil_moisture_rolling_7d_mean"] = grp_sm.transform(
            lambda s: s.rolling(window=7, min_periods=1).mean()
        )
        feat_df["evap_rolling_7d_sum"] = grp_et.transform(
            lambda s: s.rolling(window=7, min_periods=1).sum()
        )
        feat_df["evap_rolling_30d_sum"] = grp_et.transform(
            lambda s: s.rolling(window=30, min_periods=1).sum()
        )

        if len(feat_df) == 1:
            feat_df["evap_rolling_7d_sum"] = feat_df["evapotranspiration_mm"] * 7.0
            feat_df["evap_rolling_30d_sum"] = feat_df["evapotranspiration_mm"] * 30.0

        feat_df["hydro_water_deficit_7d_mm"] = (
            feat_df["evap_rolling_7d_sum"] - feat_df["rainfall_rolling_7d_sum"]
        )
        feat_df["hydro_water_deficit_30d_mm"] = (
            feat_df["evap_rolling_30d_sum"] - feat_df["rainfall_rolling_30d_sum"]
        )
        feat_df["aridity_stress_index"] = (
            feat_df["evap_rolling_30d_sum"] / (feat_df["rainfall_rolling_30d_sum"] + 15.0)
        ) * (1.0 - feat_df["soil_moisture_rolling_7d_mean"])

        # Restore original row ordering
        feat_df = feat_df.loc[original_index]

        # Build feature availability report
        derived_cols = [c for c in FEATURE_CATALOG if c in feat_df.columns]
        report = {
            "raw_features_present": raw_present,
            "derived_features_created": derived_cols,
            "derived_feature_count": len(derived_cols),
            "total_feature_count": int(feat_df.shape[1]),
            "soil_moisture_was_measured": "soil_moisture" in raw_present,
            "evapotranspiration_was_measured": "evapotranspiration_mm" in raw_present,
            "measured_aqi_was_supplied": "measured_aqi" in raw_present,
            "feature_catalog": FEATURE_CATALOG,
        }
        self.last_availability_report_ = report

        if return_report:
            return feat_df, report
        return feat_df

    def get_feature_availability_report(self) -> Dict[str, Any]:
        """Return the availability report from the most recent feature engineering run."""
        return self.last_availability_report_
