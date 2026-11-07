import os
from typing import Any, Dict
from app.core.logging import logger
from app.schemas.prediction import HazardPredictions, PredictionResponse
from app.services.ml_bridge.heat_adapter import HeatHazardModel
from app.services.ml_bridge.flood_adapter import FloodHazardModel
from app.services.ml_bridge.aqi_adapter import AirQualityHazardModel
from app.services.ml_bridge.water_adapter import WaterStressHazardModel
from datetime import datetime, timezone


class MLModelRegistry:
    """Orchestrates Lokesh's hazard prediction models with graceful calibrated fallbacks."""

    def __init__(self, models_dir: str = "models"):
        self.models_dir = models_dir
        self.inference_mode = "calibrated_heuristic"

        # Initialize adapters
        self.heat_model = HeatHazardModel()
        self.flood_model = FloodHazardModel()
        self.aqi_model = AirQualityHazardModel()
        self.water_model = WaterStressHazardModel()

        self._attempt_load_trained_models()

    def _attempt_load_trained_models(self):
        """Attempts to load trained weights if provided by Lokesh."""
        if not os.path.exists(self.models_dir):
            logger.info(f"Models directory '{self.models_dir}' not found; active in Calibrated Heuristic mode.")
            return

        try:
            import joblib
            heat_path = os.path.join(self.models_dir, "heat_model.joblib")
            if os.path.exists(heat_path):
                self.heat_model.model_artifact = joblib.load(heat_path)
                self.inference_mode = "ml_trained"
                logger.info(f"Loaded trained heat model from {heat_path}")

            flood_path = os.path.join(self.models_dir, "flood_model.joblib")
            if os.path.exists(flood_path):
                self.flood_model.model_artifact = joblib.load(flood_path)
                self.inference_mode = "ml_trained"
                logger.info(f"Loaded trained flood model from {flood_path}")

            aqi_path = os.path.join(self.models_dir, "air_quality_model.joblib")
            if os.path.exists(aqi_path):
                self.aqi_model.model_artifact = joblib.load(aqi_path)
                self.inference_mode = "ml_trained"
                logger.info(f"Loaded trained air quality model from {aqi_path}")

            water_path = os.path.join(self.models_dir, "water_stress_model.joblib")
            if os.path.exists(water_path):
                self.water_model.model_artifact = joblib.load(water_path)
                self.inference_mode = "ml_trained"
                logger.info(f"Loaded trained water stress model from {water_path}")
        except Exception as e:
            logger.warning(f"Error loading trained models: {e}; falling back to calibrated heuristics.")

    def run_all_hazard_predictions(
        self,
        features: Dict[str, Any],
        location: str = "Pune",
        ward: str = None
    ) -> PredictionResponse:
        """Run inferences across all four core climate hazard domains."""
        heat_pred = self.heat_model.predict(features)
        flood_pred = self.flood_model.predict(features)
        aqi_pred = self.aqi_model.predict(features)
        water_pred = self.water_model.predict(features)

        hazards = HazardPredictions(
            heat=heat_pred,
            flood=flood_pred,
            air_quality=aqi_pred,
            water_stress=water_pred
        )

        return PredictionResponse(
            location=location,
            ward=ward,
            evaluated_at=datetime.now(timezone.utc),
            prediction_horizon="24h",
            hazards=hazards,
            model_version="1.0.0-rf-baseline" if self.inference_mode == "ml_trained" else "1.0.0-calibrated-baseline",
            inference_mode=self.inference_mode
        )


registry = MLModelRegistry()

