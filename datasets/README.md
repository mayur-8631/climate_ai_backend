# ClimateTwin AI — Unified Environmental Dataset (Pune Pilot)

> **Phase 1 & Phase 2 Deliverable**: Multi-Year Historical & Climatological Dataset for Machine Learning Model Training.

---

## 📁 File Information
- **File**: `datasets/pune_environmental_historical.csv`
- **Total Records**: 1,095 daily observations (3 years: 2023-01-01 to 2025-12-31)
- **Spatial Coverage**: 6 micro-monitoring wards across Pune, Maharashtra:
  1. `PUN-SHV-01`: Shivajinagar (Centroid & IMD Station #43063)
  2. `PUN-KOT-02`: Kothrud (Residential Mutha river foothills)
  3. `PUN-HAD-03`: Hadapsar (Industrial / Commercial eastern corridor)
  4. `PUN-LOH-04`: Lohegaon (Airport / Northeast thermal exposure)
  5. `PUN-HIN-05`: Hinjawadi (Western IT Park & high concrete density)
  6. `PUN-KAT-06`: Katraj (Southern lake basin and hill slopes)

---

## 📊 Data Dictionary

### 1. Geographic & Temporal Identifiers
| Column | Type | Description |
| :--- | :--- | :--- |
| `date` | `YYYY-MM-DD` | Observation date |
| `location` | `string` | Pilot city (`Pune`) |
| `ward` | `string` | Ward / sub-district name |
| `ward_code` | `string` | Unique micro-ward identifier |
| `latitude` | `float` | Decimal latitude coordinate |
| `longitude` | `float` | Decimal longitude coordinate |
| `elevation_m` | `float` | Elevation above mean sea level in meters |
| `month` | `int` | Month number (1–12) |
| `is_monsoon_season` | `binary (0/1)` | Active monsoon flag (June–September) |
| `is_summer_season` | `binary (0/1)` | Summer / pre-monsoon heat flag (March–May) |

### 2. Meteorological & Environmental Features
| Column | Unit | Description |
| :--- | :--- | :--- |
| `temp_c` | °C | Ambient 24h mean temperature |
| `temp_max_c` | °C | Daily maximum peak temperature |
| `temp_min_c` | °C | Daily minimum night-time temperature |
| `humidity_pct` | % | Relative humidity percentage (0–100) |
| `heat_index_c` | °C | NOAA / Steadman-Rothfusz calculated apparent thermal stress |
| `precip_current_mm`| mm | Measured daily precipitation amount |
| `precip_24h_sum_mm` | mm | 24-hour antecedent cumulative precipitation |
| `wind_speed_kmh` | km/h | Mean surface wind speed |
| `surface_pressure_hpa` | hPa | Atmospheric pressure at station elevation (~946–955 hPa) |
| `aqi` | index | National Air Quality Index (NAQI / US AQI) |
| `pm2_5` | µg/m³ | Fine particulate matter (≤ 2.5 µm) |
| `pm10` | µg/m³ | Inhalable coarse particulate matter (≤ 10 µm) |
| `no2` | µg/m³ | Nitrogen dioxide concentration |

### 3. Hazard Prediction Ground Truth Targets (0–100 Scale)
| Column | Range | Model Target Description |
| :--- | :--- | :--- |
| `target_heat_risk` | 0.0 – 100.0 | Thermal stress & heatwave hazard level |
| `target_flood_risk` | 0.0 – 100.0 | Runoff saturation & urban waterlogging hazard level |
| `target_air_quality_risk`| 0.0 – 100.0 | Atmospheric pollution & respiratory hazard level |
| `target_water_stress_risk`| 0.0 – 100.0 | Catchment drought & hydrological reservoir deficit |
| `target_climate_risk_score` | 0 – 100 | Weighted composite Climate Risk Score |

---

## 🛠️ Usage for AI/ML Lead (Lokesh Joshi)
To train baseline models directly on this dataset:
```powershell
python ml_engine/train_baseline_models.py
```
This trains Random Forest regressors and exports the `.joblib` files to the `models/` directory for immediate backend inference.

