from app.schemas.prediction import HazardPredictions, HazardDetail
from app.schemas.risk_score import RiskLevel
from app.services.risk_engine.calculator import ClimateRiskEngine


def test_composite_score_calculation():
    hazards = HazardPredictions(
        heat=HazardDetail(score=78.0, primary_driver="High heat index"),
        flood=HazardDetail(score=65.0, primary_driver="Sustained rainfall"),
        air_quality=HazardDetail(score=58.0, primary_driver="Elevated PM2.5"),
        water_stress=HazardDetail(score=40.0, primary_driver="Seasonal baseline")
    )

    weights = {"heat": 0.30, "flood": 0.30, "air_quality": 0.20, "water_stress": 0.20}
    # Expected: 78*0.3 + 65*0.3 + 58*0.2 + 40*0.2 = 23.4 + 19.5 + 11.6 + 8.0 = 62.5 -> 62 or 63
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

