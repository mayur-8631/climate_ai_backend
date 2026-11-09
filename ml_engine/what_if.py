"""
ClimateTwin AI — Module 10: What-If Climate Scenario Simulation Engine
Module: ml_engine/what_if.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Objective:
Allow stakeholders to perturb environmental inputs (via percentage changes, deltas,
or direct overrides) and observe the recalculated hazard scores and overall
Climate Risk Score compared against the original baseline prediction.

Safety & Scientific Rules:
1. Never mutates the caller's original environmental dataset or dictionary.
2. Strictly validates scenario parameters and physical plausibility bounds.
3. Re-runs the exact fitted preprocessing and causal feature engineering pipelines.
4. Flags out-of-distribution (OOD) extrapolations when perturbed inputs exceed
   the training distribution's [min, max] or extreme thresholds.
5. Explicitly labels outputs as model-based counterfactual estimates, not guaranteed
   future meteorological forecasts.
"""

from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Optional, Union

import numpy as np
import pandas as pd

from ml_engine.config import CLIMATE_EXTREME_THRESHOLDS, PHYSICAL_BOUNDS


# Supported scenario parameter mappings
PERCENT_SCENARIO_MAP: Dict[str, List[str]] = {
    "rainfall_change_percent": [
        "rainfall_mm",
        "rainfall_intensity_mm_hr",
        "cumulative_rainfall_3d_mm",
        "cumulative_rainfall_7d_mm",
    ],
    "rainfall_pct": [
        "rainfall_mm",
        "rainfall_intensity_mm_hr",
        "cumulative_rainfall_3d_mm",
        "cumulative_rainfall_7d_mm",
    ],
    "temperature_change_percent": ["temperature_c", "temp_max_c", "temp_min_c"],
    "humidity_change_percent": ["humidity_pct"],
    "wind_speed_change_percent": ["wind_speed_kmh"],
    "pm25_change_percent": ["pm25_ugm3"],
    "pm10_change_percent": ["pm10_ugm3"],
    "aqi_change_percent": ["measured_aqi", "pm25_ugm3", "pm10_ugm3", "no2_ugm3"],
    "aqi_pct": ["measured_aqi", "pm25_ugm3", "pm10_ugm3", "no2_ugm3"],
    "soil_moisture_change_percent": ["soil_moisture"],
    "evapotranspiration_change_percent": ["evapotranspiration_mm"],
    "impervious_surface_delta_pct": ["drainage_index"],
}

DELTA_SCENARIO_MAP: Dict[str, List[str]] = {
    "temperature_delta_c": ["temperature_c", "temp_max_c", "temp_min_c"],
    "rainfall_delta_mm": ["rainfall_mm"],
    "humidity_delta_pct": ["humidity_pct"],
    "wind_speed_delta_kmh": ["wind_speed_kmh"],
    "pm25_delta_ugm3": ["pm25_ugm3"],
    "soil_moisture_delta": ["soil_moisture"],
}

DIRECT_OVERRIDE_KEYS: List[str] = list(PHYSICAL_BOUNDS.keys())


class WhatIfSimulationEngine:
    """
    Executes counterfactual climate scenario simulations while preserving original
    inputs and detecting out-of-distribution extrapolations.
    """

    def __init__(self, prediction_fn: Callable[[Any], Dict[str, Any]]) -> None:
        """
        Args:
            prediction_fn: Function that accepts raw environmental input and returns
                           the full hazard + composite Climate Risk Score prediction.
        """
        self.prediction_fn = prediction_fn

    @staticmethod
    def validate_scenario(scenario: Dict[str, Any]) -> None:
        """
        Validate scenario keys, numeric types, and realistic perturbation ranges.
        Raises ValueError on unsupported or physically impossible scenarios.
        """
        if not isinstance(scenario, dict) or len(scenario) == 0:
            raise ValueError("What-if scenario must be a non-empty dictionary.")

        allowed_keys = (
            set(PERCENT_SCENARIO_MAP.keys())
            | set(DELTA_SCENARIO_MAP.keys())
            | set(DIRECT_OVERRIDE_KEYS)
        )

        for key, raw_val in scenario.items():
            if key not in allowed_keys:
                raise ValueError(
                    f"Unsupported scenario parameter '{key}'. "
                    f"Supported keys: {sorted(allowed_keys)}"
                )
            try:
                val = float(raw_val)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Scenario value for '{key}' must be numeric, got {raw_val!r}.") from exc

            if np.isnan(val) or np.isinf(val):
                raise ValueError(f"Scenario value for '{key}' cannot be NaN or infinite.")

            # Validate percentage changes
            if key.endswith("_change_percent") or key.endswith("_pct"):
                if val < -100.0 or val > 500.0:
                    raise ValueError(
                        f"Unrealistic percentage change for '{key}': {val}%. "
                        "Allowed range is [-100%, +500%]."
                    )
            # Validate direct overrides against physical bounds
            if key in PHYSICAL_BOUNDS:
                low_b, high_b = PHYSICAL_BOUNDS[key]
                if val < low_b or val > high_b:
                    raise ValueError(
                        f"Scenario override for '{key}' ({val}) violates physical bounds [{low_b}, {high_b}]."
                    )
            # Validate temperature delta bounds
            if key == "temperature_delta_c" and (val < -25.0 or val > 25.0):
                raise ValueError(
                    f"Unrealistic temperature_delta_c ({val}°C). Allowed range is [-25°C, +25°C]."
                )

    @staticmethod
    def apply_scenario_to_data(
        data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
        scenario: Dict[str, Any],
    ) -> Tuple[Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]], List[str]]:
        """
        Create a deep copy of `data` and apply the validated scenario modifications
        to the target observation without mutating the original input.
        """
        WhatIfSimulationEngine.validate_scenario(scenario)
        modified = copy.deepcopy(data)
        ood_warnings: List[str] = []

        if isinstance(modified, dict):
            target_records = [modified]
        elif isinstance(modified, list):
            target_records = modified
        elif isinstance(modified, pd.DataFrame):
            target_records = modified.to_dict(orient="records")
        else:
            raise TypeError(f"Unsupported data type for What-If simulation: {type(data)}")

        # Apply perturbations to the latest observation (or all rows if single-step scenario)
        for rec in target_records:
            # Ensure temp_max_c and temp_min_c exist if temperature_c is present so deltas apply consistently
            if "temperature_c" in rec and rec["temperature_c"] is not None:
                base_t = float(rec["temperature_c"])
                if "temp_max_c" not in rec or rec["temp_max_c"] is None:
                    rec["temp_max_c"] = base_t + 5.0
                if "temp_min_c" not in rec or rec["temp_min_c"] is None:
                    rec["temp_min_c"] = base_t - 5.0

            # 1. Percentage changes
            for p_key, target_cols in PERCENT_SCENARIO_MAP.items():
                if p_key in scenario:
                    pct = float(scenario[p_key])
                    multiplier = 1.0 + (pct / 100.0)
                    for col in target_cols:
                        if col in rec and rec[col] is not None and not pd.isna(rec[col]):
                            rec[col] = float(rec[col]) * multiplier
                        elif col == "rainfall_intensity_mm_hr" and "rainfall_mm" in rec and rec["rainfall_mm"] is not None:
                            rec[col] = float(rec["rainfall_mm"]) * 0.28

            # 2. Additive delta changes
            for d_key, target_cols in DELTA_SCENARIO_MAP.items():
                if d_key in scenario:
                    delta = float(scenario[d_key])
                    for col in target_cols:
                        if col in rec and rec[col] is not None and not pd.isna(rec[col]):
                            rec[col] = float(rec[col]) + delta

            # 3. Direct variable overrides
            for o_key in DIRECT_OVERRIDE_KEYS:
                if o_key in scenario:
                    rec[o_key] = float(scenario[o_key])
                    if o_key == "temperature_c":
                        rec["temp_max_c"] = max(float(rec.get("temp_max_c", rec[o_key] + 5.0)), float(rec[o_key]) + 3.0)
                        rec["temp_min_c"] = min(float(rec.get("temp_min_c", rec[o_key] - 5.0)), float(rec[o_key]) - 3.0)

            # Clamp bounded variables (like humidity 0-100%, soil_moisture 0-1) and check OOD extremes
            for col, (low_b, high_b) in PHYSICAL_BOUNDS.items():
                if col in rec and rec[col] is not None and not pd.isna(rec[col]):
                    val = float(rec[col])
                    if val < low_b or val > high_b:
                        ood_warnings.append(
                            f"Perturbed '{col}' ({val:.2f}) exceeded physical bounds [{low_b}, {high_b}] and was clamped."
                        )
                        rec[col] = float(np.clip(val, low_b, high_b))

            for col, (ext_low, ext_high) in CLIMATE_EXTREME_THRESHOLDS.items():
                if col in rec and rec[col] is not None and not pd.isna(rec[col]):
                    val = float(rec[col])
                    if val < ext_low or val > ext_high:
                        ood_warnings.append(
                            f"Scenario places '{col}' ({val:.2f}) in extreme tail regime outside typical training range [{ext_low}, {ext_high}]."
                        )

        if isinstance(modified, pd.DataFrame):
            return pd.DataFrame(target_records), list(dict.fromkeys(ood_warnings))
        if isinstance(modified, dict):
            return target_records[0], list(dict.fromkeys(ood_warnings))
        return target_records, list(dict.fromkeys(ood_warnings))

    def simulate(
        self,
        data: Union[Dict[str, Any], pd.DataFrame, List[Dict[str, Any]]],
        scenario: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute baseline prediction and scenario prediction, returning the exact
        hazard-by-hazard and composite Climate Risk Score comparison.
        """
        baseline_input = copy.deepcopy(data)
        scenario_input, ood_warnings = self.apply_scenario_to_data(data, scenario)

        baseline_res = self.prediction_fn(baseline_input)
        scenario_res = self.prediction_fn(scenario_input)

        base_score = float(baseline_res["climate_risk_score"])
        scen_score = float(scenario_res["climate_risk_score"])
        abs_change = round(scen_score - base_score, 2)
        pct_change = (
            round((abs_change / base_score) * 100.0, 2)
            if base_score > 1e-6
            else (100.0 if abs_change > 0 else 0.0)
        )

        hazard_comparison: Dict[str, Dict[str, Any]] = {}
        changed_hazards_summary: List[str] = []

        for h_key in ["heat", "flood", "air_quality", "water_stress"]:
            b_h = float(baseline_res["risks"][h_key])
            s_h = float(scenario_res["risks"][h_key])
            diff_h = round(s_h - b_h, 2)
            pct_h = round((diff_h / b_h) * 100.0, 2) if b_h > 1e-6 else 0.0
            hazard_comparison[h_key] = {
                "baseline": round(b_h, 2),
                "scenario": round(s_h, 2),
                "change": diff_h,
                "change_percentage": pct_h,
            }
            if abs(diff_h) >= 0.05:
                direction = "increased" if diff_h > 0 else "decreased"
                changed_hazards_summary.append(f"{h_key} risk {direction} by {abs(diff_h):.2f} pts ({b_h:.1f} -> {s_h:.1f})")

        if changed_hazards_summary:
            explanation_text = (
                f"Under scenario {scenario}, " + "; ".join(changed_hazards_summary) + ". "
                f"Overall Climate Risk Score moved from {base_score:.2f} ({baseline_res['risk_level']}) "
                f"to {scen_score:.2f} ({scenario_res['risk_level']})."
            )
        else:
            explanation_text = (
                f"Under scenario {scenario}, model hazard outputs remained unchanged at "
                f"Climate Risk Score {scen_score:.2f} ({scenario_res['risk_level']})."
            )

        return {
            "baseline_score": round(base_score, 2),
            "scenario_score": round(scen_score, 2),
            "baseline_risk_level": baseline_res["risk_level"],
            "scenario_risk_level": scenario_res["risk_level"],
            "change": abs_change,
            "change_percentage": pct_change,
            "scenario": copy.deepcopy(scenario),
            "hazard_comparison": hazard_comparison,
            "explanation": explanation_text,
            "out_of_distribution_warnings": ood_warnings,
            "simulation_disclaimer": (
                "Model-based counterfactual simulation estimate only; not a guaranteed future weather forecast."
            ),
        }

