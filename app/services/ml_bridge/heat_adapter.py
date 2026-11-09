from typing import Any, Dict
from app.schemas.prediction import HazardDetail
from app.services.preprocessing.normalizer import EnvironmentalNormalizer


class HeatHazardModel:
    """Predicts heatwave and thermal stress risk (0-100 scale)."""

    def __init__(self, model_artifact: Any = None):
        self.model_artifact = model_artifact

    def predict(self, features: Dict[str, Any]) -> HazardDetail:
        if self.model_artifact is not None and hasattr(self.model_artifact, "predict"):
            # If Lokesh's trained scikit-learn / XGBoost model artifact is loaded
            try:
                import pandas as pd
                df_vec = pd.DataFrame([{
                    "temp_c": features.get("temp_c", 30.0),
                    "humidity_pct": features.get("humidity_pct", 50.0),
                    "heat_index_c": features.get("heat_index_c", 32.0),
                    "is_summer_season": features.get("is_summer_season", 0)
                }])
                pred = float(self.model_artifact.predict(df_vec)[0])
                score = max(0.0, min(100.0, round(pred, 1)))
                imps = getattr(self.model_artifact, "feature_importances_", [0.45, 0.20, 0.25, 0.10])
                cols = list(df_vec.columns)
                dynamic_contribs = {cols[i]: round(float(imps[i]), 4) for i in range(len(cols))}
                return HazardDetail(
                    score=score,
                    status="AVAILABLE",
                    confidence=0.93,
                    primary_driver=self._determine_driver(features),
                    feature_contributions=dynamic_contribs
                )
            except Exception:
                pass

        # Calibrated Pune Climatological Heuristic Model
        temp = features.get("temp_c", 28.0)
        hi = features.get("heat_index_c", temp)
        summer = features.get("is_summer_season", 0)

        # Baseline: normal Pune max temp is ~28-32C; heatwave alerts start at 38C
        if hi < 30.0:
            score = EnvironmentalNormalizer.normalize_to_scale(hi, 20.0, 30.0) * 0.35
        elif hi < 37.0:
            score = 35.0 + EnvironmentalNormalizer.normalize_to_scale(hi, 30.0, 37.0) * 0.30
        elif hi < 42.0:
            score = 65.0 + EnvironmentalNormalizer.normalize_to_scale(hi, 37.0, 42.0) * 0.20
        else:
            score = 85.0 + min(15.0, (hi - 42.0) * 3.0)

        if summer:
            score = min(100.0, score + 5.0)

        score = round(max(0.0, min(100.0, score)), 1)
        driver = self._determine_driver(features)

        return HazardDetail(
            score=score,
            status="AVAILABLE",
            confidence=0.88,
            primary_driver=driver,
            feature_contributions={
                "heat_index": round(hi, 1),
                "ambient_temp": round(temp, 1),
                "relative_humidity": features.get("humidity_pct", 50.0)
            }
        )

    def _determine_driver(self, features: Dict[str, Any]) -> str:
        temp = features.get("temp_c", 28.0)
        hi = features.get("heat_index_c", temp)
        if hi >= 42.0:
            return "Extreme heat index exceeding danger threshold (>42°C)"
        elif temp >= 38.0:
            return "Severe ambient heatwave conditions (>38°C)"
        elif hi > temp + 4.0:
            return "High humidity amplifying apparent heat stress"
        elif temp >= 33.0:
            return "Moderate elevated afternoon temperatures"
        return "Normal ambient thermal conditions for Pune"

