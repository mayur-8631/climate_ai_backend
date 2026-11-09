# ClimateTwin AI — Environmental Datasets & Feasibility Matrix

**Owner:** Lokesh Joshi | AI/ML Lead  
**Team:** PrithviNex | PCCOE International Grand Challenge 2026  
**Institute:** AISSMS College of Engineering  

---

## 1. Scientific & Engineering Policy on Environmental Data

In strict compliance with the ClimateTwin AI Scientific Rules:
1. **No Fabricated Ground-Truth Labels:** Where historical emergency/mortality or direct flood-inundation ground-truth labels are unavailable from public APIs, models train on **explicitly documented physical/meteorological hazard proxy targets** (e.g., NOAA/Steadman Heat Index hazard scale, Hydrometeorological Rainfall-Runoff Flood Hazard Proxy, CPCB National Air Quality Index (NAQI) sub-index formula, and Surface Hydro-Climatic Water Deficit Proxy).
2. **Pilot Location:** **Pune, Maharashtra, India** (`18.5204° N, 73.8567° E`, elevation `560 m`) is the primary pilot location, with multi-city extensibility (Mumbai, Nagpur, Delhi, Bengaluru).
3. **Chronological Splitting:** All temporal datasets are split strictly chronologically (`70% Train`, `15% Validation`, `15% Test`) prior to fitting scalers or imputers to prevent data leakage.

---

## 2. Evaluated Environmental Data Sources (9-Point Documentation)

### Source A: Open-Meteo Historical Weather & Air Quality API
1. **Source Name:** Open-Meteo Historical Weather API & Air Quality API (ERA5 / CAMS Reanalysis)
2. **Data URL / Access Method:** `https://archive-api.open-meteo.com/v1/archive` and `https://air-quality-api.open-meteo.com/v1/air-quality` (REST JSON / CSV)
3. **Variables Available:** `temperature_2m`, `temperature_2m_max`, `temperature_2m_min`, `relative_humidity_2m`, `wind_speed_10m`, `wind_direction_10m`, `surface_pressure`, `precipitation`, `rain`, `soil_moisture_0_to_7cm`, `et0_fao_evapotranspiration`, `pm2_5`, `pm10`, `nitrogen_dioxide`, `sulphur_dioxide`, `carbon_monoxide`, `ozone`.
4. **Geographical Coverage:** Global (`0.1°` to `0.25°` resolution, covers Pune and all Indian districts).
5. **Historical Coverage:** 1940–present (Weather); 2013–present (Air Quality).
6. **Update Frequency:** Hourly / Daily (1–5 day reanalysis latency for historical archive; real-time for forecast endpoints).
7. **Licence & Usage Restrictions:** Attribution 4.0 International (CC BY 4.0) for non-commercial / academic research.
8. **Missing Variables:** Direct municipal reservoir storage levels, street-level drainage blockage data, verified flood inundation depth polygons, hospital heat-stroke admission counts.
9. **Suitability for Model Training:** **High** for meteorological, soil-moisture, evapotranspiration, and background pollutant features. Requires physical hazard proxy formulation for flood and water-stress targets.

---

### Source B: NASA POWER (Prediction Of Worldwide Energy Resources)
1. **Source Name:** NASA Langley Research Center POWER Project (MERRA-2)
2. **Data URL / Access Method:** `https://power.larc.nasa.gov/api/temporal/daily/point`
3. **Variables Available:** `T2M`, `T2M_MAX`, `T2M_MIN`, `RH2M`, `PRECTOTCORR` (bias-corrected precipitation), `WS10M`, `PS`, `GWETTOP` (surface soil wetness `0–1`).
4. **Geographical Coverage:** Global (`0.5° × 0.625°` grid).
5. **Historical Coverage:** 1981–present.
6. **Update Frequency:** Daily (2–7 day latency).
7. **Licence & Usage Restrictions:** Public Domain (NASA Open Data Policy).
8. **Missing Variables:** Criteria air pollutants (`PM2.5`, `PM10`, `NO2`, `SO2`, `CO`, `O3`), high-resolution urban drainage topology.
9. **Suitability for Model Training:** **High** for multi-decade climatological baselines (temperature anomalies, long-term precipitation percentiles, surface soil wetness).

---

### Source C: Central Pollution Control Board (CPCB) — CAAQMS
1. **Source Name:** CPCB Central Control Room for Air Quality Management (CAAQMS — Karve Road / Shivajinagar / Pashan stations, Pune)
2. **Data URL / Access Method:** `https://airquality.cpcb.gov.in` / data.gov.in Open Government Data Portal
3. **Variables Available:** `PM2.5`, `PM10`, `NO2`, `SO2`, `CO`, `O3`, `NH3`, `Pb`, and official Indian NAQI.
4. **Geographical Coverage:** Major Indian cities (including multiple stations in Pune).
5. **Historical Coverage:** 2015–present (varies by station).
6. **Update Frequency:** 15-minute / Hourly / Daily averages.
7. **Licence & Usage Restrictions:** Government Open Data License – India (GODL-India).
8. **Missing Variables:** Sensor maintenance gaps (frequent `NaN` outages in `SO2`/`O3`), soil moisture, hydrological runoff.
9. **Suitability for Model Training:** **High** for Indian NAQI calibration and pollutant hazard modeling; requires robust missing-value imputation (`ml_engine/data_preprocessing.py`) due to station outages.

---

### Source D: India Meteorological Department (IMD) Gridded Data & Pune Climatology
1. **Source Name:** IMD Pune (`imdpune.gov.in`) High-Resolution Gridded Rainfall (`0.25°×0.25°`) & Temperature (`1.0°×1.0°`)
2. **Data URL / Access Method:** `https://imdpune.gov.in/lrfindex.php` (`imdlib` / NetCDF / CSV extracts)
3. **Variables Available:** Daily rainfall (`mm`), daily `Tmax` (`°C`), daily `Tmin` (`°C`).
4. **Geographical Coverage:** All-India land points.
5. **Historical Coverage:** 1901–present (Rainfall); 1951–present (Temperature).
6. **Update Frequency:** Daily / Annual archival updates.
7. **Licence & Usage Restrictions:** Academic/research usage with IMD attribution.
8. **Missing Variables:** Hourly humidity, wind speed, air quality pollutants, soil moisture.
9. **Suitability for Model Training:** **High** for establishing Pune seasonal climatological baselines (summer `Tmax` percentiles, SW monsoon rainfall thresholds).

---

## 3. Dataset Availability & Feasibility Matrix

| Hazard Domain | Primary Input Variables | Primary Data Sources | Ground-Truth / Target Definition | Target Type | Feasibility & Limitations |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Heat Risk** | `temperature_c`, `temp_max_c`, `temp_min_c`, `humidity_pct`, `wind_speed_kmh`, `temp_rolling_3d_mean`, `temp_anomaly_c`, `heat_index_c` | Open-Meteo / NASA POWER / IMD | **24h-Ahead Meteorological Heat Hazard Proxy (`0–100`)** derived from NOAA/Steadman Apparent Temperature & IMD Heatwave anomaly thresholds | Continuous (`0–100`) + 5 Risk Levels | **High feasibility.** Does *not* claim medically validated hospital mortality prediction. |
| **2. Rainfall & Flood Risk** | `rainfall_mm`, `rainfall_intensity_mm_hr`, `rainfall_rolling_3d_sum`, `rainfall_rolling_7d_sum`, `soil_moisture`, `elevation_m`, `slope_deg`, `drainage_index` | Open-Meteo / NASA POWER / SRTM Elevation | **Hydrometeorological Flood-Hazard Proxy (`0–100`)** combining antecedent precipitation (3d/7d), peak intensity, soil saturation, and topographic drainage factor | Continuous (`0–100`) + 5 Risk Levels | **Moderate-High feasibility.** Explicitly labeled as a *rainfall-runoff flood-hazard proxy*, not hydrodynamic street inundation. |
| **3. Air-Quality Risk** | `pm25_ugm3`, `pm10_ugm3`, `no2_ugm3`, `so2_ugm3`, `co_mgm3`, `o3_ugm3`, `temperature_c`, `humidity_pct`, `wind_speed_kmh` | CPCB / Open-Meteo CAMS | **CPCB NAQI-Calibrated Air Quality Hazard Score (`0–100`)** mapped from official Indian CPCB breakpoint sub-indices (`0–500` NAQI scaled to `0–100` hazard) | Continuous (`0–100`) + 5 Risk Levels | **High feasibility.** Distinguishes measured AQI from ML-predicted air-quality hazard when partial sensors are missing. |
| **4. Water-Stress Analysis** | `rainfall_rolling_7d_sum`, `rainfall_rolling_30d_sum`, `temp_max_c`, `humidity_pct`, `soil_moisture`, `evapotranspiration_mm`, `P-PET deficit` | NASA POWER / Open-Meteo | **Environmental Hydro-Climatic Water-Stress Proxy (`0–100`)** based on 30-day cumulative precipitation-evapotranspiration deficit & root-zone soil moisture depletion | Continuous (`0–100`) + 5 Risk Levels | **Moderate-High feasibility.** Measures *environmental/climatic water stress*, not municipal dam storage or pipe supply shortages. |

---

## 4. Pilot Dataset (`datasets/raw/pune_environmental_timeseries.csv`)

To guarantee full offline reproducibility, automated testing, and immediate training/evaluation without requiring live API keys during grading, the repository includes a **climatologically calibrated multi-year daily dataset for Pune (`2022-01-01` to `2026-10-31`, 1,765 daily records)** generated from Pune's seasonal climatological distributions (IMD/Open-Meteo/CPCB seasonal profiles: Pre-Monsoon hot dry Mar–May, SW Monsoon heavy rain Jun–Sep, Post-Monsoon Oct–Nov, Winter inversion/pollution Dec–Feb), including realistic sensor missingness (`NaN`) and measurement anomalies for testing the preprocessing pipeline.

