"""
ClimateTwin AI — Module 7: Localized Climate Risk Score Engine
Module: ml_engine/risk_score.py

Owner: Lokesh Joshi | AI/ML Lead
Team: PrithviNex | PCCOE International Grand Challenge 2026

Objective:
Combine the four hazard-specific predictions (Heat, Flood, Air Quality, Water Stress)
into a single localized Climate Risk Score (0-100) using a transparent, configurable
weighted aggregation method.

Missing-Hazard Policy:
Missing hazards (None / NaN) are NEVER silently treated as zero. Instead:
1. `data_coverage` is reported as the percentage of the 4 hazards present.
2. Active weights are proportionally re-normalized across available hazards.
3. The exact calculation formula and renormalization are documented in the response.

Scientific Disclaimer:
This composite index is an analytical multi-hazard decision-support score for the
ClimateTwin AI platform, not an officially recognized universal meteorological index.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from ml_engine.config import (
    DEFAULT_RISK_THRESHOLDS,
    DEFAULT_RISK_WEIGHTS,
    score_to_risk_level,
)

HAZARD_KEYS: List[str] = ["heat", "flood", "air_quality", "water_stress"]


class ClimateRiskScoreEngine:
    """
    Configurable, strictly validated multi-hazard Climate Risk Score aggregation engine.
    """

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[List[Tuple[float, float, str]]] = None,
    ) -> None:
        self.weights: Dict[str, float] = dict(weights) if weights is not None else dict(DEFAULT_RISK_WEIGHTS)
        self.thresholds: List[Tuple[float, float, str]] = (
            list(thresholds) if thresholds is not None else list(DEFAULT_RISK_THRESHOLDS)
        )
        self._validate_weights(self.weights)

    @staticmethod
    def _validate_weights(weights: Dict[str, float]) -> None:
        missing_keys = [k for k in HAZARD_KEYS if k not in weights]
        if missing_keys:
            raise ValueError(f"Risk score weights missing required hazard keys: {missing_keys}")

        for k, val in weights.items():
            if val is None or np.isnan(float(val)):
                raise ValueError(f"Weight for hazard '{k}' cannot be None or NaN.")
            if float(val) < 0.0:
                raise ValueError(f"Weight for hazard '{k}' must be non-negative, got {val}.")

        total = sum(float(weights[k]) for k in HAZARD_KEYS)
        if not np.isclose(total, 1.0, atol=1e-5):
            raise ValueError(f"Risk score weights must sum to 1.0, got {total:.6f}.")

    @staticmethod
    def _extract_hazard_value(raw_input: Dict[str, Any], key: str) -> Optional[float]:
        """
        Extract hazard score whether passed directly (`{"heat": 72}`) or nested in
        model output dicts (`{"heat": {"heat_risk": 72}}`).
        """
        if key not in raw_input or raw_input[key] is None:
            return None
        val = raw_input[key]
        if isinstance(val, dict):
            nested_key = f"{key}_risk"
            if nested_key in val and val[nested_key] is not None:
                val = val[nested_key]
            elif "score" in val and val["score"] is not None:
                val = val["score"]
            else:
                return None
        try:
            fval = float(val)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid non-numeric score for hazard '{key}': {val}") from exc

        if np.isnan(fval):
            return None
        if fval < 0.0 or fval > 100.0:
            raise ValueError(f"Hazard score for '{key}' must be within [0, 100], got {fval}.")
        return round(fval, 2)

    def calculate(
        self,
        hazard_inputs: Dict[str, Any],
        custom_weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Compute the localized Climate Risk Score (0-100), risk category, data coverage,
        and transparent formula breakdown.
        """
        active_base_weights = dict(custom_weights) if custom_weights is not None else dict(self.weights)
        self._validate_weights(active_base_weights)

        extracted: Dict[str, Optional[float]] = {}
        available_keys: List[str] = []
        missing_keys: List[str] = []

        for k in HAZARD_KEYS:
            score = self._extract_hazard_value(hazard_inputs, k)
            extracted[k] = score
            if score is not None:
                available_keys.append(k)
            else:
                missing_keys.append(k)

        if not available_keys:
            raise ValueError("Cannot calculate Climate Risk Score: all four hazard inputs are unavailable.")

        data_coverage = round(100.0 * len(available_keys) / len(HAZARD_KEYS), 2)

        # Renormalize weights over available hazards so missing hazards are NEVER treated as 0
        available_weight_sum = sum(active_base_weights[k] for k in available_keys)
        if available_weight_sum <= 0.0:
            raise ValueError("Sum of weights for available hazards must be positive.")

        effective_weights_exact: Dict[str, float] = {}
        effective_weights: Dict[str, float] = {}
        for k in HAZARD_KEYS:
            if k in available_keys:
                exact_w = active_base_weights[k] / available_weight_sum
                effective_weights_exact[k] = exact_w
                effective_weights[k] = round(exact_w, 4)
            else:
                effective_weights_exact[k] = 0.0
                effective_weights[k] = 0.0

        # Ensure rounded display weights sum to 1.0000 exactly
        if available_keys:
            rounding_diff = round(1.0 - sum(effective_weights[k] for k in available_keys), 4)
            last_avail = available_keys[-1]
            effective_weights[last_avail] = round(effective_weights[last_avail] + rounding_diff, 4)

        composite_raw = sum(
            extracted[k] * effective_weights_exact[k] for k in available_keys if extracted[k] is not None
        )
        composite_score = round(float(np.clip(composite_raw, 0.0, 100.0)), 2)
        risk_level = score_to_risk_level(composite_score, self.thresholds)

        terms_str = " + ".join(
            f"({k}: {extracted[k]:.2f} × {effective_weights[k]:.2f})" for k in available_keys
        )
        if missing_keys:
            policy_note = (
                f"Missing hazards {missing_keys} were excluded (not set to zero); "
                f"weights were proportionally re-normalized across available hazards {available_keys}."
            )
        else:
            policy_note = "All 4 hazards available (100% coverage); standard configured weights applied."

        return {
            "climate_risk_score": composite_score,
            "risk_level": risk_level,
            "hazard_breakdown": {
                "heat": extracted["heat"],
                "flood": extracted["flood"],
                "air_quality": extracted["air_quality"],
                "water_stress": extracted["water_stress"],
            },
            "weights": active_base_weights,
            "effective_weights": effective_weights,
            "data_coverage": data_coverage,
            "missing_hazards": missing_keys,
            "calculation_explanation": f"Climate Risk Score = {terms_str} = {composite_score:.2f}. {policy_note}",
            "methodology_disclaimer": (
                "Weighted multi-hazard decision-support composite score (illustrative starting weights). "
                "Not an officially recognized WMO or IMD climate index."
            ),
        }
