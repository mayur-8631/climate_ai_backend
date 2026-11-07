# ML Models Directory (Lokesh Joshi - AI / ML Lead)

Place trained scikit-learn / XGBoost / PyTorch model artifacts here for direct backend inference:

- `heat_model.joblib`: Trained model for thermal stress and heatwave risk
- `flood_model.joblib`: Trained model for rainfall runoff and urban waterlogging risk
- `air_quality_model.joblib`: Trained model for particulate dispersion and AQI risk
- `water_stress_model.joblib`: Trained model for catchment reservoir depletion and hydrological stress

The backend dynamically detects these files upon startup. If any model is omitted or undergoing retraining, the backend automatically falls back to calibrated climatological heuristic models with `inference_mode="calibrated_heuristic"`.

