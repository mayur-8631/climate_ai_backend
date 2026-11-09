export type RiskCategory = 'Low' | 'Moderate' | 'High' | 'Critical';

export type HazardType = 'heat' | 'flood' | 'air_quality' | 'water_stress';

export interface HazardDetail {
  score: number; // 0 - 100
  level: RiskCategory;
  trend: 'increasing' | 'stable' | 'decreasing';
  trendValue: string;
  explanation: string;
  contributingFactors: string[];
}

export interface RiskBreakdown {
  heat: HazardDetail;
  flood: HazardDetail;
  air_quality: HazardDetail;
  water_stress: HazardDetail;
}

export interface EnvironmentalMetrics {
  temperature: number; // °C
  humidity: number; // %
  rainfall: number; // mm (24h cumulative)
  aqi: number; // US AQI scale
  wind_speed: number; // km/h
  wind_direction?: string;
  uv_index?: number;
  pressure?: number; // hPa
  soil_moisture?: number; // %
}

export interface LocationData {
  id: string;
  name: string;
  state: string;
  country: string;
  lat: number;
  lng: number;
  climate_risk_score: number; // 0 - 100
  risk_level: RiskCategory;
  status_explanation: string;
  last_updated: string;
  metrics: EnvironmentalMetrics;
  risks: {
    heat: number;
    flood: number;
    air_quality: number;
    water_stress: number;
  };
  risk_details: RiskBreakdown;
  isMock?: boolean;
}

// Initial integration response contract matching section 10
export interface InitialIntegrationContract {
  location: string;
  temperature: number;
  rainfall: number;
  aqi: number;
  risks: {
    heat: number;
    flood: number;
    air_quality: number;
    water_stress: number;
  };
  climate_risk_score: number;
  risk_level: RiskCategory;
}

export interface HistoricalDataPoint {
  timestamp: string;
  timeLabel: string;
  temperature: number;
  rainfall: number;
  aqi: number;
  heat_risk: number;
  flood_risk: number;
  air_quality_risk: number;
  water_stress_risk: number;
  composite_risk: number;
}

export interface ClimateInsight {
  id: string;
  type: 'alert' | 'warning' | 'info' | 'positive';
  hazard: HazardType | 'composite';
  title: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timeframe: string;
  suggestedAction: string;
}

export interface SimulationParams {
  rainfallPercentChange: number; // e.g. -50% to +100%
  tempIncrease: number; // e.g. 0°C to +5°C
  humidityDelta: number; // e.g. -30% to +30%
  aqiDelta: number; // e.g. -50 to +200
}

export interface FeatureImportance {
  feature: string;
  name: string;
  importance: number; // 0 - 1 relative weight
  direction: 'positive' | 'negative';
  baselineValue: string;
  simulatedValue?: string;
  description: string;
}

export interface SimulationResult {
  baselineRiskScore: number;
  simulatedRiskScore: number;
  riskDelta: number;
  baselineLevel: RiskCategory;
  simulatedLevel: RiskCategory;
  hazardDeltas: {
    heat: { baseline: number; simulated: number; delta: number };
    flood: { baseline: number; simulated: number; delta: number };
    air_quality: { baseline: number; simulated: number; delta: number };
    water_stress: { baseline: number; simulated: number; delta: number };
  };
  featureImportance: FeatureImportance[];
  narrativeSummary: string;
  isIllustrativeDemo: boolean;
}

export type StakeholderType = 'citizens' | 'government' | 'farmers' | 'urban_planners';

export interface RecommendationItem {
  id: string;
  stakeholder: StakeholderType;
  hazardCategory: HazardType | 'multi-hazard';
  title: string;
  summary: string;
  priority: 'Critical' | 'High' | 'Medium' | 'Informational';
  actionableSteps: string[];
  timeframe: 'Immediate (<24h)' | 'Short-term (1-7 days)' | 'Seasonal (1-3 months)' | 'Strategic (Annual)';
  estimatedImpact: string;
  isIllustrativeDemo: boolean;
  tags: string[];
}

export interface TeamMember {
  name: string;
  role: string;
  focus: string;
  bio: string;
  avatar: string;
  contributions: string[];
  badge: string;
}

