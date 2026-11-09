from typing import Any, Dict
from app.schemas.prediction import HazardDetail
from app.services.preprocessing.normalizer import EnvironmentalNormalizer


class AirQualityHazardModel:
    """Predicts respiratory and atmospheric pollution risk (0-100 scale)."""

    def __init__(self, model_artifact: Any = None):
        self.model_artifact = model_artifact

    def predict(self, features: Dict[str, Any]) -> HazardDetail:
        if self.model_artifact is not None and hasattr(self.model_artifact, "predict"):
            try:
                import pandas as pd
                df_vec = pd.DataFrame([{
                    "aqi": features.get("aqi", 80),
                    "pm2_5": features.get("pm2_5", 35.0),
                    "pm10": features.get("pm10", 65.0),
                    "wind_speed_kmh": features.get("wind_speed_kmh", 10.0)
                }])
                pred = float(self.model_artifact.predict(df_vec)[0])
                score = max(0.0, min(100.0, round(pred, 1)))
                imps = getattr(self.model_artifact, "feature_importances_", [0.40, 0.30, 0.20, 0.10])
                cols = list(df_vec.columns)
                dynamic_contribs = {cols[i]: round(float(imps[i]), 4) for i in range(len(cols))}
                return HazardDetail(
                    score=score,
                    status="AVAILABLE",
                    confidence=0.94,
                    primary_driver=self._determine_driver(features),
                    feature_contributions=dynamic_contribs
                )
            except Exception:
                pass

        # Calibrated Urban Air Quality Risk Model
        aqi = features.get("aqi", 70)
        pm2_5 = features.get("pm2_5", 30.0)
        wind = features.get("wind_speed_kmh", 10.0)

        # Baseline AQI Risk Scale
        if aqi <= 50:
            score = EnvironmentalNormalizer.normalize_to_scale(aqi, 0.0, 50.0) * 0.25
        elif aqi <= 100:
            score = 25.0 + EnvironmentalNormalizer.normalize_to_scale(aqi, 50.0, 100.0) * 0.25
        elif aqi <= 200:
            score = 50.0 + EnvironmentalNormalizer.normalize_to_scale(aqi, 100.0, 200.0) * 0.25
        elif aqi <= 300:
            score = 75.0 + EnvironmentalNormalizer.normalize_to_scale(aqi, 200.0, 300.0) * 0.15
        else:
            score = 90.0 + min(10.0, (aqi - 300.0) * 0.1)

        # Wind dispersion penalty: calm winds (< 5 km/h) trap pollutants in valley
        if wind < 5.0 and score > 40.0:
            score = min(100.0, score + 8.0)

        score = round(max(0.0, min(100.0, score)), 1)
        driver = self._determine_driver(features)

        return HazardDetail(
            score=score,
            status="AVAILABLE",
            confidence=0.91,
            primary_driver=driver,
            feature_contributions={
                "measured_aqi": aqi,
                "pm2_5_ugm3": round(pm2_5, 1),
                "dispersion_wind_kmh": round(wind, 1)
            }
        )

    def _determine_driver(self, features: Dict[str, Any]) -> str:
        aqi = features.get("aqi", 70)
        pm2_5 = features.get("pm2_5", 30.0)
        wind = features.get("wind_speed_kmh", 10.0)
        if aqi > 300:
            return "Hazardous multi-pollutant accumulation posing acute health hazard"
        elif aqi > 200:
            return "Very unhealthy particulate density (PM2.5 & PM10 elevated)"
        elif pm2_5 > 60.0:
            return "Elevated fine particulate (PM2.5) exceeding WHO guidelines"
        elif wind < 4.0 and aqi > 100:
            return "Atmospheric inversion and stagnant surface winds trapping particulate"
        return "Air quality within acceptable standard ambient thresholds"

