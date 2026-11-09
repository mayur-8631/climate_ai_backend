"""
Unified Automated Unit Tests for Backend ClimateRiskEngine (`app.services.risk_engine`)
and ML Engine ClimateRiskScoreEngine (`ml_engine.risk_score`)
File: tests/test_risk_score.py
"""

import numpy as np
import pytest

from app.schemas.prediction import HazardDetail, HazardPredictions
from app.schemas.risk_score import RiskLevel
from app.services.risk_engine.calculator import ClimateRiskEngine
from ml_engine.risk_score import ClimateRiskScoreEngine


# ============================================================================
# PART 1: BACKEND CLIMATE RISK ENGINE TESTS (Mayuresh Kamble)
# ============================================================================

def test_composite_score_calculation():
    hazards = HazardPredictions(
        heat=HazardDetail(score=78.0, primary_driver="High heat index"),
        flood=HazardDetail(score=65.0, primary_driver="Sustained rainfall"),
        air_quality=HazardDetail(score=58.0, primary_driver="Elevated PM2.5"),
        water_stress=HazardDetail(score=40.0, primary_driver="Seasonal baseline"),
    )

    weights = {"heat": 0.30, "flood": 0.30, "air_quality": 0.20, "water_stress": 0.20}
    score, level = ClimateRiskEngine.calculate_composite_score(hazards, weights)
    assert score in (62, 63)
    assert level == RiskLevel.HIGH


def test_risk_level_boundaries():
    assert ClimateRiskEngine.assign_risk_level(15) == RiskLevel.LOW
    assert ClimateRiskEngine.assign_risk_level(20) == RiskLevel.LOW
    assert ClimateRiskEngine.assign_risk_level(21) == RiskLevel.MODERATE
    assert ClimateRiskEngine.assign_risk_level(50) == RiskLevel.MODERATE
    assert ClimateRiskEngine.assign_risk_level(51) == RiskLevel.HIGH
    assert ClimateRiskEngine.assign_risk_level(70) == RiskLevel.HIGH
    assert ClimateRiskEngine.assign_risk_level(71) == RiskLevel.SEVERE
    assert ClimateRiskEngine.assign_risk_level(85) == RiskLevel.SEVERE
    assert ClimateRiskEngine.assign_risk_level(86) == RiskLevel.EXTREME
    assert ClimateRiskEngine.assign_risk_level(100) == RiskLevel.EXTREME


# ============================================================================
# PART 2: ML ENGINE CLIMATE RISK SCORE ENGINE TESTS (Lokesh Joshi)
# ============================================================================

def test_risk_score_exact_weighted_calculation_and_categories():
    """Verify exact weighted aggregation, 0-100 range, and 5-tier risk category mapping."""
    engine = ClimateRiskScoreEngine()
    res = engine.calculate(
        {
            "heat": 78.0,
            "flood": 65.0,
            "air_quality": 58.0,
            "water_stress": 40.0,
        }
    )
    assert np.isclose(res["climate_risk_score"], 60.6)
    assert res["risk_level"] == "High"
    assert res["data_coverage"] == 100.0
    assert res["missing_hazards"] == []


def test_risk_score_weight_validation():
    """Verify negative weights or weights not summing to 1.0 raise ValueError."""
    with pytest.raises(ValueError, match="non-negative"):
        ClimateRiskScoreEngine(
            weights={"heat": -0.1, "flood": 0.5, "air_quality": 0.3, "water_stress": 0.3}
        )

    with pytest.raises(ValueError, match="sum to 1.0"):
        ClimateRiskScoreEngine(
            weights={"heat": 0.5, "flood": 0.5, "air_quality": 0.5, "water_stress": 0.5}
        )


def test_risk_score_out_of_range_hazard_rejected():
    """Verify hazard score outside [0, 100] raises ValueError."""
    engine = ClimateRiskScoreEngine()
    with pytest.raises(ValueError, match="within \\[0, 100\\]"):
        engine.calculate({"heat": 115.0, "flood": 40.0, "air_quality": 30.0, "water_stress": 20.0})


def test_missing_hazard_never_treated_as_zero():
    """
    Verify missing hazards are never silently treated as zero:
    if flood is None and the other three hazards are 80.0, the re-normalized
    composite score must be 80.0 (not 80 * 0.70 = 56.0), with data_coverage = 75.0%.
    """
    engine = ClimateRiskScoreEngine()
    res = engine.calculate(
        {
            "heat": 80.0,
            "flood": None,
            "air_quality": 80.0,
            "water_stress": 80.0,
        }
    )
    assert np.isclose(res["climate_risk_score"], 80.0)
    assert res["data_coverage"] == 75.0
    assert res["missing_hazards"] == ["flood"]
    assert res["effective_weights"]["flood"] == 0.0
    assert np.isclose(
        res["effective_weights"]["heat"]
        + res["effective_weights"]["air_quality"]
        + res["effective_weights"]["water_stress"],
        1.0,
    )


def test_risk_score_reproducibility():
    """Verify identical inputs produce identical Risk Score results across repeated calls."""
    engine = ClimateRiskScoreEngine()
    inp = {"heat": 42.3, "flood": 18.7, "air_quality": 51.2, "water_stress": 63.4}
    r1 = engine.calculate(inp)
    r2 = engine.calculate(inp)
    assert r1 == r2
