"""
ClimateTwin AI — Module 1: Environmental Data Preprocessing Pipeline
Module: ml_engine/data_preprocessing.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Responsibilities:
A. Input validation (required columns, numeric coercion, invalid timestamps,
   impossible physical values, duplicate record removal).
B. Missing data handling (NEVER replaces missing environmental observations with zero;
   preserves missingness indicators; fits median/climatological imputers on training
   data only; reports unavailable/insufficient information).
C. Outlier detection (IQR & Z-score bounds fitted on training data; distinguishes
   genuine climate extremes from sensor measurement errors without deleting extreme weather).
D. Standardization (unit conversion, canonical column naming, timestamp normalization,
   optional StandardScaler fitted strictly on training data).
E. Reproducible persistence via joblib.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from ml_engine.config import (
    CANONICAL_NUMERIC_FEATURES,
    CLIMATE_EXTREME_THRESHOLDS,
    COLUMN_ALIASES,
    DEFAULT_LOCATION_METADATA,
    PHYSICAL_BOUNDS,
    PROCESSED_DATA_DIR,
)


class EnvironmentalDataPreprocessor:
    """
    Stateful, reproducible preprocessing pipeline for environmental observations.
    Fits all statistics (imputation medians, IQR/Z-score thresholds, scalers)
    strictly on training data and reuses them during validation/test/inference.
    """

    def __init__(
        self,
        preserve_missing_indicators: bool = True,
        scale_numeric: bool = False,
        z_score_threshold: float = 3.5,
        iqr_multiplier: float = 2.5,
    ) -> None:
        self.preserve_missing_indicators = preserve_missing_indicators
        self.scale_numeric = scale_numeric
        self.z_score_threshold = z_score_threshold
        self.iqr_multiplier = iqr_multiplier

        self.is_fitted_: bool = False
        self.feature_medians_: Dict[str, float] = {}
        self.monthly_feature_medians_: Dict[Tuple[int, str], float] = {}
        self.feature_means_: Dict[str, float] = {}
        self.feature_stds_: Dict[str, float] = {}
        self.iqr_bounds_: Dict[str, Tuple[float, float]] = {}
        self.fitted_columns_: List[str] = []
        self.scaler_: Optional[StandardScaler] = None
        self.last_validation_report_: Dict[str, Any] = {}

    # ------------------------------------------------------------------
    # 1. INPUT CONVERSION & UNIT / ALIAS STANDARDIZATION
    # ------------------------------------------------------------------
    @staticmethod
    def _to_dataframe(data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
        if isinstance(data, pd.DataFrame):
            return data.copy()
        if isinstance(data, dict):
            return pd.DataFrame([copy.deepcopy(data)])
        if isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Input environmental data list cannot be empty.")
            return pd.DataFrame(copy.deepcopy(data))
        raise TypeError(f"Unsupported input data type: {type(data)}. Expected DataFrame, dict, or list of dicts.")

    @staticmethod
    def standardize_units_and_columns(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
        """
        Standardize column aliases and convert non-standard measurement units
        (e.g., Kelvin -> Celsius, m/s -> km/h) into canonical ClimateTwin AI units.
        """
        df = df.copy()
        unit_notes: List[str] = []

        # Unit conversions before alias renaming
        if "temperature_k" in df.columns and "temperature_c" not in df.columns:
            df["temperature_c"] = pd.to_numeric(df["temperature_k"], errors="coerce") - 273.15
            df.drop(columns=["temperature_k"], inplace=True)
            unit_notes.append("Converted temperature_k (Kelvin) to temperature_c (°C).")

        if "temperature_f" in df.columns and "temperature_c" not in df.columns:
            df["temperature_c"] = (pd.to_numeric(df["temperature_f"], errors="coerce") - 32.0) * (5.0 / 9.0)
            df.drop(columns=["temperature_f"], inplace=True)
            unit_notes.append("Converted temperature_f (°F) to temperature_c (°C).")

        if "wind_speed_ms" in df.columns and "wind_speed_kmh" not in df.columns:
            df["wind_speed_kmh"] = pd.to_numeric(df["wind_speed_ms"], errors="coerce") * 3.6
            df.drop(columns=["wind_speed_ms"], inplace=True)
            unit_notes.append("Converted wind_speed_ms (m/s) to wind_speed_kmh (km/h).")

        # Map column aliases to canonical names without overwriting existing canonical columns
        rename_map = {}
        for col in df.columns:
            clean_col = str(col).strip().lower()
            if clean_col in COLUMN_ALIASES:
                target = COLUMN_ALIASES[clean_col]
                if target not in df.columns:
                    rename_map[col] = target
        if rename_map:
            df.rename(columns=rename_map, inplace=True)

        return df, unit_notes

    # ------------------------------------------------------------------
    # 2. INPUT VALIDATION, DUPLICATE REMOVAL & PHYSICAL BOUNDS CHECK
    # ------------------------------------------------------------------
    def validate_and_clean(
        self,
        df: pd.DataFrame,
        drop_invalid_timestamps: bool = False,
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Perform comprehensive validation:
        - Ensure location & timestamp exist
        - Parse and normalize timestamps
        - Remove duplicate (location, timestamp) rows
        - Coerce numeric columns
        - Replace physically impossible sensor errors with NaN (NEVER with 0)
        """
        df, unit_notes = self.standardize_units_and_columns(df)
        report: Dict[str, Any] = {
            "initial_row_count": int(len(df)),
            "unit_conversions": unit_notes,
            "duplicate_rows_removed": 0,
            "invalid_timestamp_count": 0,
            "non_numeric_coercions": {},
            "impossible_value_counts": {},
            "missing_counts_before_imputation": {},
            "extreme_weather_counts": {},
            "warnings": [],
        }

        # Location defaults
        if "location" not in df.columns:
            df["location"] = "Pune"
            report["warnings"].append("Column 'location' missing; defaulted to pilot location 'Pune'.")
        else:
            df["location"] = df["location"].fillna("Pune").astype(str).str.strip()

        # Timestamp validation
        if "timestamp" not in df.columns:
            df["timestamp"] = pd.Timestamp("2026-11-09T12:00:00")
            report["warnings"].append("Column 'timestamp' missing; assigned reference timestamp.")
        parsed_ts = pd.to_datetime(df["timestamp"], errors="coerce")
        invalid_ts_mask = parsed_ts.isna()
        report["invalid_timestamp_count"] = int(invalid_ts_mask.sum())

        if invalid_ts_mask.any():
            report["warnings"].append(
                f"Detected {int(invalid_ts_mask.sum())} invalid timestamp(s)."
            )
            if drop_invalid_timestamps:
                df = df.loc[~invalid_ts_mask].copy()
                parsed_ts = parsed_ts.loc[~invalid_ts_mask]
            else:
                parsed_ts = parsed_ts.ffill().bfill().fillna(pd.Timestamp("2026-11-09T12:00:00"))

        df["timestamp"] = parsed_ts

        # Duplicate removal by (location, timestamp)
        before_dedup = len(df)
        df = df.drop_duplicates(subset=["location", "timestamp"], keep="last").copy()
        report["duplicate_rows_removed"] = int(before_dedup - len(df))

        # Populate default geographical metadata per location when absent
        for geo_col in ["latitude", "longitude", "elevation_m", "slope_deg", "drainage_index"]:
            if geo_col not in df.columns:
                df[geo_col] = df["location"].map(
                    lambda loc: DEFAULT_LOCATION_METADATA.get(loc, DEFAULT_LOCATION_METADATA["Pune"])[geo_col]
                )

        # Numeric coercion and physical bounds check
        for col in CANONICAL_NUMERIC_FEATURES:
            if col not in df.columns:
                continue
            raw_non_null = df[col].notna().sum()
            coerced = pd.to_numeric(df[col], errors="coerce")
            coerced_non_null = coerced.notna().sum()
            if coerced_non_null < raw_non_null:
                diff = int(raw_non_null - coerced_non_null)
                report["non_numeric_coercions"][col] = diff
                report["warnings"].append(f"Column '{col}' had {diff} non-numeric entries coerced to NaN.")
            df[col] = coerced.astype(float)

            # Physical plausibility bounds check
            if col in PHYSICAL_BOUNDS:
                low_bound, high_bound = PHYSICAL_BOUNDS[col]
                impossible_mask = df[col].notna() & ((df[col] < low_bound) | (df[col] > high_bound))
                impossible_cnt = int(impossible_mask.sum())
                if impossible_cnt > 0:
                    report["impossible_value_counts"][col] = impossible_cnt
                    report["warnings"].append(
                        f"Column '{col}' had {impossible_cnt} physically impossible value(s) outside "
                        f"[{low_bound}, {high_bound}] replaced with NaN."
                    )
                    df.loc[impossible_mask, col] = np.nan

        # Logical cross-column check: temp_max_c >= temperature_c >= temp_min_c
        if {"temp_max_c", "temp_min_c"}.issubset(df.columns):
            inverted_mask = (
                df["temp_max_c"].notna()
                & df["temp_min_c"].notna()
                & (df["temp_max_c"] < df["temp_min_c"])
            )
            if inverted_mask.any():
                cnt = int(inverted_mask.sum())
                report["warnings"].append(
                    f"Detected {cnt} record(s) where temp_max_c < temp_min_c; swapped values."
                )
                tmp = df.loc[inverted_mask, "temp_max_c"].copy()
                df.loc[inverted_mask, "temp_max_c"] = df.loc[inverted_mask, "temp_min_c"]
                df.loc[inverted_mask, "temp_min_c"] = tmp

        # Record missing counts before imputation
        for col in CANONICAL_NUMERIC_FEATURES:
            if col in df.columns:
                report["missing_counts_before_imputation"][col] = int(df[col].isna().sum())

        return df, report

    # ------------------------------------------------------------------
    # 3. FIT PREPROCESSOR ON TRAINING DATA ONLY
    # ------------------------------------------------------------------
    def fit(self, train_data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> "EnvironmentalDataPreprocessor":
        """
        Fit imputation statistics, IQR/Z-score outlier thresholds, and optional
        StandardScaler strictly on the training dataset.
        """
        raw_df = self._to_dataframe(train_data)
        df, _ = self.validate_and_clean(raw_df, drop_invalid_timestamps=True)
        df = df.sort_values(["location", "timestamp"]).reset_index(drop=True)

        months = df["timestamp"].dt.month
        self.fitted_columns_ = [c for c in CANONICAL_NUMERIC_FEATURES if c in df.columns]
        self.feature_medians_.clear()
        self.monthly_feature_medians_.clear()
        self.feature_means_.clear()
        self.feature_stds_.clear()
        self.iqr_bounds_.clear()

        for col in self.fitted_columns_:
            series = df[col].dropna()
            if len(series) > 0:
                self.feature_medians_[col] = float(series.median())
                self.feature_means_[col] = float(series.mean())
                std_val = float(series.std(ddof=1)) if len(series) > 1 else 1.0
                self.feature_stds_[col] = std_val if std_val > 1e-8 else 1.0

                q25, q75 = np.percentile(series, [25, 75])
                iqr = max(float(q75 - q25), 1e-6)
                self.iqr_bounds_[col] = (
                    float(q25 - self.iqr_multiplier * iqr),
                    float(q75 + self.iqr_multiplier * iqr),
                )
            else:
                self.feature_medians_[col] = np.nan
                self.feature_means_[col] = 0.0
                self.feature_stds_[col] = 1.0
                self.iqr_bounds_[col] = (-np.inf, np.inf)

            # Monthly climatological medians for seasonally aware imputation
            for m in range(1, 13):
                m_series = df.loc[months == m, col].dropna()
                if len(m_series) > 0:
                    self.monthly_feature_medians_[(m, col)] = float(m_series.median())

        if self.scale_numeric and self.fitted_columns_:
            imputed_for_scaler = self._impute_dataframe(df.copy(), add_indicators=False)
            self.scaler_ = StandardScaler()
            self.scaler_.fit(imputed_for_scaler[self.fitted_columns_])

        self.is_fitted_ = True
        return self

    # ------------------------------------------------------------------
    # 4. IMPUTATION & OUTLIER / EXTREME WEATHER FLAGGING
    # ------------------------------------------------------------------
    def _impute_dataframe(self, df: pd.DataFrame, add_indicators: bool = True) -> pd.DataFrame:
        """
        Impute missing values using:
        1. Missingness indicator columns (<col>_is_missing) if enabled.
        2. Short-window forward fill (max 2 steps) for sequential records of the same location.
        3. Fitted monthly median from training data (preserving seasonal baseline, never 0).
        4. Fitted global training median fallback.
        """
        df = df.copy()
        months = df["timestamp"].dt.month

        # Collect new indicator columns to avoid DataFrame fragmentation
        indicator_cols: Dict[str, pd.Series] = {}

        for col in self.fitted_columns_:
            if col not in df.columns:
                df[col] = np.nan

            missing_mask = df[col].isna()
            if add_indicators and self.preserve_missing_indicators:
                indicator_cols[f"{col}_is_missing"] = missing_mask.astype(int)

            if missing_mask.any():
                # If multiple sequential rows exist for a location, allow max 2-step causal ffill
                if len(df) > 1 and df["timestamp"].is_monotonic_increasing:
                    df[col] = df.groupby("location")[col].ffill(limit=2)

                # Fill remaining NaNs with fitted monthly training median, then overall training median
                still_missing = df[col].isna()
                if still_missing.any():
                    monthly_fill = months.map(
                        lambda m: self.monthly_feature_medians_.get((int(m), col), self.feature_medians_.get(col, np.nan))
                    )
                    df.loc[still_missing, col] = monthly_fill.loc[still_missing]

                still_missing_after = df[col].isna()
                if still_missing_after.any():
                    fallback = self.feature_medians_.get(col, np.nan)
                    df.loc[still_missing_after, col] = fallback

        if indicator_cols:
            df = pd.concat([df, pd.DataFrame(indicator_cols, index=df.index)], axis=1)

        return df

    def _flag_outliers_and_extremes(
        self, df: pd.DataFrame, report: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        Identify statistical outliers (IQR & Z-score) and domain climate extremes.
        CRITICAL RULE: Genuine extreme weather events are flagged (`is_climate_extreme`),
        NEVER deleted.
        """
        df = df.copy()
        extreme_flags = pd.Series(0, index=df.index, dtype=int)
        statistical_outlier_flags = pd.Series(0, index=df.index, dtype=int)

        for col in self.fitted_columns_:
            if col not in df.columns:
                continue
            vals = df[col]

            # Statistical outlier check (Z-score & IQR from training distribution)
            mean_val = self.feature_means_.get(col, 0.0)
            std_val = self.feature_stds_.get(col, 1.0)
            z_scores = ((vals - mean_val) / std_val).abs()
            iqr_low, iqr_high = self.iqr_bounds_.get(col, (-np.inf, np.inf))
            stat_mask = (z_scores > self.z_score_threshold) | (vals < iqr_low) | (vals > iqr_high)
            statistical_outlier_flags = statistical_outlier_flags | stat_mask.fillna(False).astype(int)

            # Domain climate extreme check
            if col in CLIMATE_EXTREME_THRESHOLDS:
                ext_low, ext_high = CLIMATE_EXTREME_THRESHOLDS[col]
                ext_mask = vals.notna() & ((vals < ext_low) | (vals > ext_high))
                ext_cnt = int(ext_mask.sum())
                if ext_cnt > 0:
                    report["extreme_weather_counts"][col] = ext_cnt
                extreme_flags = extreme_flags | ext_mask.astype(int)

        df["is_statistical_outlier"] = statistical_outlier_flags
        df["is_climate_extreme"] = extreme_flags
        return df

    # ------------------------------------------------------------------
    # 5. TRANSFORM & FIT_TRANSFORM
    # ------------------------------------------------------------------
    def transform(
        self,
        data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
        return_report: bool = False,
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict[str, Any]]]:
        """
        Validate, clean, flag extremes, and impute environmental data using
        strictly pre-fitted training parameters.
        """
        if not self.is_fitted_:
            raise RuntimeError(
                "EnvironmentalDataPreprocessor is not fitted. Call fit() on training data "
                "or load a fitted preprocessor before calling transform()."
            )

        raw_df = self._to_dataframe(data)
        df, report = self.validate_and_clean(raw_df, drop_invalid_timestamps=False)

        # Calculate pre-imputation data coverage across core environmental variables
        core_vars = [
            "temperature_c",
            "humidity_pct",
            "wind_speed_kmh",
            "rainfall_mm",
            "pm25_ugm3",
            "pm10_ugm3",
            "soil_moisture",
        ]
        present_core = [c for c in core_vars if c in df.columns]
        if present_core and len(df) > 0:
            total_cells = len(df) * len(core_vars)
            non_null_cells = sum(int(df[c].notna().sum()) for c in present_core)
            report["data_coverage_pct"] = round(100.0 * non_null_cells / total_cells, 2)
        else:
            report["data_coverage_pct"] = 0.0

        # Flag statistical outliers and genuine climate extremes before scaling
        df = self._flag_outliers_and_extremes(df, report)

        # Impute missing values using fitted training statistics
        df = self._impute_dataframe(df, add_indicators=self.preserve_missing_indicators)

        # Reconcile temp_max_c and temp_min_c if only temperature_c was provided
        if "temperature_c" in df.columns:
            if "temp_max_c" in df.columns:
                df["temp_max_c"] = np.maximum(df["temp_max_c"], df["temperature_c"])
            if "temp_min_c" in df.columns:
                df["temp_min_c"] = np.minimum(df["temp_min_c"], df["temperature_c"])

        # Apply optional scaling
        if self.scale_numeric and self.scaler_ is not None:
            df[self.fitted_columns_] = self.scaler_.transform(df[self.fitted_columns_])

        self.last_validation_report_ = report
        if return_report:
            return df, report
        return df

    def fit_transform(
        self,
        train_data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]],
        return_report: bool = False,
    ) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict[str, Any]]]:
        """Fit the preprocessor on training data and return the transformed training DataFrame."""
        self.fit(train_data)
        return self.transform(train_data, return_report=return_report)

    # ------------------------------------------------------------------
    # 6. PERSISTENCE
    # ------------------------------------------------------------------
    def save(self, filepath: Optional[Union[str, Path]] = None) -> Path:
        if not self.is_fitted_:
            raise RuntimeError("Cannot save an unfitted EnvironmentalDataPreprocessor.")
        target_path = Path(filepath) if filepath else (PROCESSED_DATA_DIR / "preprocessor.joblib")
        target_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, target_path)
        return target_path

    @classmethod
    def load(cls, filepath: Optional[Union[str, Path]] = None) -> "EnvironmentalDataPreprocessor":
        target_path = Path(filepath) if filepath else (PROCESSED_DATA_DIR / "preprocessor.joblib")
        if not target_path.exists():
            raise FileNotFoundError(
                f"Fitted preprocessor file not found at '{target_path}'. "
                "Run model training pipeline first."
            )
        obj = joblib.load(target_path)
        if not isinstance(obj, cls):
            raise TypeError(f"Loaded artifact at '{target_path}' is not an EnvironmentalDataPreprocessor.")
        return obj

