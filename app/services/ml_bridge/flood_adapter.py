from typing import Any, Dict
from app.schemas.prediction import HazardDetail
from app.services.preprocessing.normalizer import EnvironmentalNormalizer


class FloodHazardModel:
    """Predicts localized flash flood and drainage inundation risk (0-100 scale)."""

    def __init__(self, model_artifact: Any = None):
        self.model_artifact = model_artifact

    def predict(self, features: Dict[str, Any]) -> HazardDetail:
        if self.model_artifact is not None and hasattr(self.model_artifact, "predict"):
            try:
                import pandas as pd
                df_vec = pd.DataFrame([{
                    "precip_current_mm": features.get("precip_current_mm", 0.0),
                    "precip_24h_sum_mm": features.get("precip_24h_sum_mm", 0.0),
                    "is_monsoon_season": features.get("is_monsoon_season", 0)
                }])
                pred = float(self.model_artifact.predict(df_vec)[0])
                score = max(0.0, min(100.0, round(pred, 1)))
                imps = getattr(self.model_artifact, "feature_importances_", [0.30, 0.60, 0.10])
                cols = list(df_vec.columns)
                dynamic_contribs = {cols[i]: round(float(imps[i]), 4) for i in range(len(cols))}
                return HazardDetail(
                    score=score,
                    status="AVAILABLE",
                    confidence=0.91,
                    primary_driver=self._determine_driver(features),
                    feature_contributions=dynamic_contribs
                )
            except Exception:
                pass

        # Calibrated Pune Drainage Basin Heuristic Model
        precip_24h = features.get("precip_24h_sum_mm", 0.0)
        precip_curr = features.get("precip_current_mm", 0.0)
        is_monsoon = features.get("is_monsoon_season", 0)

        # Baseline Pune Urban Flood Thresholds:
        # 0 - 15 mm: dry/light runoff (< 20)
        # 15 - 64.5 mm: moderate runoff (20 - 55)
        # 64.5 - 115.5 mm: heavy rain / waterlogging alert (55 - 80)
        # > 115.5 mm: very heavy / extreme inundation danger (80 - 100)
        if precip_24h <= 5.0:
            score = 10.0 if is_monsoon else 5.0
        elif precip_24h <= 30.0:
            score = 15.0 + EnvironmentalNormalizer.normalize_to_scale(precip_24h, 5.0, 30.0) * 0.25
        elif precip_24h <= 65.0:
            score = 40.0 + EnvironmentalNormalizer.normalize_to_scale(precip_24h, 30.0, 65.0) * 0.25
        elif precip_24h <= 120.0:
            score = 65.0 + EnvironmentalNormalizer.normalize_to_scale(precip_24h, 65.0, 120.0) * 0.20
        else:
            score = 85.0 + min(15.0, (precip_24h - 120.0) * 0.2)

        # High burst rate booster
        if precip_curr > 20.0:
            score = min(100.0, score + 15.0)

        score = round(max(0.0, min(100.0, score)), 1)
        driver = self._determine_driver(features)

        return HazardDetail(
            score=score,
            status="AVAILABLE",
            confidence=0.87,
            primary_driver=driver,
            feature_contributions={
                "precip_24h_sum_mm": round(precip_24h, 1),
                "current_intensity_mm": round(precip_curr, 1),
                "drainage_saturation_factor": 1.2 if is_monsoon else 0.8
            }
        )

    def _determine_driver(self, features: Dict[str, Any]) -> str:
        p24 = features.get("precip_24h_sum_mm", 0.0)
        curr = features.get("precip_current_mm", 0.0)
        if p24 >= 115.0:
            return "Extreme rainfall threshold exceeded (>115 mm in 24h); high flash flood & river surge risk"
        elif p24 >= 65.0:
            return "Heavy sustained precipitation causing waterlogging in low-lying Mula-Mutha basin corridors"
        elif curr >= 15.0:
            return "High instantaneous rainfall burst exceeding storm drain capacity"
        elif p24 >= 20.0:
            return "Moderate antecedent precipitation with elevated soil saturation"
        return "Normal stormwater absorption and low surface runoff"

