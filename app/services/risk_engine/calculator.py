from typing import Dict, Optional, Tuple
from app.schemas.risk_score import RiskScoreResponse, RisksBreakdown, RiskLevel
from app.schemas.prediction import HazardPredictions
from app.schemas.common import Provenance


class ClimateRiskEngine:
    """Calculates composite localized Climate Risk Score (0-100) and assigns risk levels."""

    DEFAULT_WEIGHTS = {
        "heat": 0.30,
        "flood": 0.30,
        "air_quality": 0.20,
        "water_stress": 0.20
    }

    @classmethod
    def calculate_composite_score(
        cls,
        hazards: HazardPredictions,
        weights: Optional[Dict[str, float]] = None
    ) -> Tuple[int, RiskLevel]:
        w = weights or cls.DEFAULT_WEIGHTS

        # Normalize weights to sum to 1.0
        total_w = sum(w.values())
        norm_weights = {k: v / total_w for k, v in w.items()}

        raw_score = (
            hazards.heat.score * norm_weights["heat"]
            + hazards.flood.score * norm_weights["flood"]
            + hazards.air_quality.score * norm_weights["air_quality"]
            + hazards.water_stress.score * norm_weights["water_stress"]
        )

        composite = int(round(max(0.0, min(100.0, raw_score))))
        level = cls.assign_risk_level(composite)
        return composite, level

    @staticmethod
    def assign_risk_level(score: int) -> RiskLevel:
        if score <= 20:
            return RiskLevel.LOW
        elif score <= 50:
            return RiskLevel.MODERATE
        elif score <= 70:
            return RiskLevel.HIGH
        elif score <= 85:
            return RiskLevel.SEVERE
        else:
            return RiskLevel.EXTREME

    @classmethod
    def build_risk_response(
        cls,
        location: str,
        ward: Optional[str],
        temperature: Optional[float],
        rainfall: Optional[float],
        aqi: Optional[int],
        hazards: HazardPredictions,
        provenance: Optional[Provenance] = None,
        weights: Optional[Dict[str, float]] = None
    ) -> RiskScoreResponse:
        composite, level = cls.calculate_composite_score(hazards, weights)

        return RiskScoreResponse(
            location=location,
            ward=ward,
            temperature=temperature,
            rainfall=rainfall,
            aqi=aqi,
            risks=RisksBreakdown(
                heat=hazards.heat.score,
                flood=hazards.flood.score,
                air_quality=hazards.air_quality.score,
                water_stress=hazards.water_stress.score
            ),
            climate_risk_score=composite,
            risk_level=level,
            breakdown_weights=weights or cls.DEFAULT_WEIGHTS,
            provenance=provenance
        )

