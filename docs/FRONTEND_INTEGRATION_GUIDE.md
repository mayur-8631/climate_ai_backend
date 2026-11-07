# ClimateTwin AI — Frontend Integration Guide (for Pravin Kamble)

> **Frontend & Visualization Lead**: Pravin Kamble  
> **Backend & Data Lead**: Mayuresh Kamble  
> **Backend Base URL**: `http://localhost:8000` (or `http://127.0.0.1:8000`)  
> **CORS**: Enabled for `http://localhost:3000`

---

## 🗺️ 1. Interactive Risk Map Endpoint (Leaflet)
* **Endpoint**: `GET /api/v1/risk-score/map`
* **Purpose**: Single batch call to render all 6 Pune micro-wards on your Leaflet map.

### TypeScript Interfaces:
```typescript
export interface Coordinates {
  latitude: number;
  longitude: number;
}

export interface WardRiskMapPoint {
  ward_code: string;        // e.g. "PUN-SHV-01"
  name: string;             // e.g. "Shivajinagar"
  coordinates: Coordinates; // { latitude: 18.5314, longitude: 73.8446 }
  elevation_m: number;
  climate_risk_score: number; // 0 - 100
  risk_level: "Low" | "Moderate" | "High" | "Severe" | "Extreme";
  marker_color: string;     // Hex code: "#22C55E" (Green), "#F59E0B" (Amber), "#EF4444" (Red)
  primary_hazard: string;   // "Heat" | "Flood" | "Air Quality" | "Water Stress"
  temperature: number;      // °C
  rainfall: number;         // mm
  aqi: number;
  risks: {
    heat: number;
    flood: number;
    air_quality: number;
    water_stress: number;
  };
}

export interface WardsRiskMapResponse {
  city: string;
  state: string;
  country: string;
  centroid: Coordinates;
  timestamp: string;
  total_wards: number;
  citywide_average_risk: number;
  wards: WardRiskMapPoint[];
}
```

---

## 📈 2. Single Location Risk Score (Main Dashboard Badge)
* **Endpoint**: `GET /api/v1/risk-score?location=Pune&ward=Shivajinagar`
* **Sample Response**:
```json
{
  "location": "Pune",
  "ward": "Shivajinagar",
  "temperature": 32.4,
  "rainfall": 15.0,
  "aqi": 142,
  "risks": {
    "heat": 74.5,
    "flood": 22.0,
    "air_quality": 65.0,
    "water_stress": 48.0
  },
  "climate_risk_score": 62,
  "risk_level": "High",
  "breakdown_weights": {
    "heat": 0.30,
    "flood": 0.30,
    "air_quality": 0.20,
    "water_stress": 0.20
  }
}
```

---

## 🧪 3. What-If Simulation Endpoint (Scenario Slider UI)
* **Endpoint**: `POST /api/v1/simulate`
* **Request Body**:
```json
{
  "location": "Pune",
  "ward": "Shivajinagar",
  "deltas": {
    "rainfall_pct": 30.0,
    "temperature_delta_c": 2.5,
    "aqi_pct": 15.0
  }
}
```
* **Response**:
```json
{
  "location": "Pune",
  "ward": "Shivajinagar",
  "baseline_risk": { "climate_risk_score": 62, ... },
  "simulated_risk": { "climate_risk_score": 71, ... },
  "score_delta": 9,
  "hazard_deltas": { "heat": 12.0, "flood": 18.5, "air_quality": 6.2, "water_stress": 0.0 },
  "scenario_summary": "A 30% increase in rainfall shifts flood risk by +18.5 pts. A +2.5°C warming anomaly elevates heat stress risk by +12.0 pts.",
  "disclaimer": "SCENARIO ESTIMATE: These values are simulated projections based on perturbation modeling and do not constitute guaranteed weather forecasts."
}
```

---

## 📋 4. Stakeholder Recommendations Endpoint
* **Endpoint**: `GET /api/v1/recommendations?location=Pune&stakeholder=municipal`
* **Query Options for `stakeholder`**:
  - `all`
  - `municipal`
  - `citizens`
  - `disaster_management`
  - `agriculture`

---

## 💻 5. Ready-to-Use Next.js / React API Client (`api.ts`)

```typescript
import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const climateApi = {
  // 1. Fetch map points for Leaflet
  getWardsMap: async () => {
    const res = await axios.get(`${API_BASE_URL}/risk-score/map`);
    return res.data;
  },

  // 2. Fetch detailed risk score for a ward
  getRiskScore: async (ward: string = "Shivajinagar") => {
    const res = await axios.get(`${API_BASE_URL}/risk-score`, {
      params: { location: "Pune", ward }
    });
    return res.data;
  },

  // 3. Fetch historical trend for Recharts
  getHistory: async (days: number = 30) => {
    const res = await axios.get(`${API_BASE_URL}/history`, {
      params: { location: "Pune", days }
    });
    return res.data;
  },

  // 4. Run What-If simulation
  runSimulation: async (deltas: { rainfall_pct?: number; temperature_delta_c?: number; aqi_pct?: number }, ward?: string) => {
    const res = await axios.post(`${API_BASE_URL}/simulate`, {
      location: "Pune",
      ward: ward || "Shivajinagar",
      deltas
    });
    return res.data;
  },

  // 5. Fetch recommendations
  getRecommendations: async (stakeholder: string = "all") => {
    const res = await axios.get(`${API_BASE_URL}/recommendations`, {
      params: { location: "Pune", stakeholder }
    });
    return res.data;
  }
};
```

