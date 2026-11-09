import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  LocationData,
  HistoricalDataPoint,
  RecommendationItem,
  SimulationParams,
  SimulationResult,
  InitialIntegrationContract,
  EnvironmentalMetrics,
  RiskBreakdown,
  RiskCategory,
} from '@/types/climate';
import {
  MOCK_LOCATIONS,
  MOCK_HISTORICAL_DATA,
  MOCK_RECOMMENDATIONS,
} from './mockData';
import { calculateIllustrativeSimulation } from '@/utils/riskCalculator';
import { getRiskCategory } from '@/utils/formatters';

/**
 * CLIMATETWIN AI - API SERVICE LAYER
 * 
 * Integrated with FastAPI backend (Team PrithviNex - Mayuresh Kamble & Lokesh Joshi).
 * Default API Base: http://localhost:8000
 * Endpoints:
 *   - GET  /api/v1/risk-score?location={location}
 *   - GET  /api/v1/locations
 *   - GET  /api/v1/history?location={location}
 *   - GET  /api/v1/recommendations
 *   - POST /api/v1/simulate
 */

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

const API_V1 = '/api/v1';

const FORCE_MOCK =
  process.env.NEXT_PUBLIC_USE_MOCK_API === 'true' ||
  typeof window === 'undefined'; // SSR default safe

export interface ServiceResponse<T> {
  data: T;
  isMock: boolean;
  status: 'success' | 'fallback' | 'error';
  sourceUrl: string;
  timestamp: string;
  error?: string;
}

class ClimateApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 4000, // 4-second timeout before graceful fallback
      headers: {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
    });
  }

  /**
   * Helper to find a mock location by ID or name
   */
  public getMockLocation(query: string = 'pune'): LocationData {
    const q = query.toLowerCase().trim();
    const found = MOCK_LOCATIONS.find(
      (loc) =>
        loc.id.toLowerCase() === q ||
        loc.name.toLowerCase().includes(q) ||
        loc.state.toLowerCase().includes(q)
    );
    return found || MOCK_LOCATIONS[0]; // Defaults to Pune
  }

  /**
   * Fetch all supported locations
   */
  public async getLocations(): Promise<ServiceResponse<LocationData[]>> {
    const timestamp = '2026-11-09T13:45:00Z';
    if (FORCE_MOCK) {
      return {
        data: MOCK_LOCATIONS,
        isMock: true,
        status: 'success',
        sourceUrl: 'local://mockData/locations',
        timestamp,
      };
    }

    try {
      const res = await this.client.get(`${API_V1}/locations`);
      if (Array.isArray(res.data) && res.data.length > 0) {
        // If items already conform to LocationData (have id and name)
        if (res.data[0].id && res.data[0].name) {
          return {
            data: res.data,
            isMock: false,
            status: 'success',
            sourceUrl: `${API_BASE_URL}${API_V1}/locations`,
            timestamp,
          };
        }

        // Map backend LocationDetail format [{ city, state, country, coordinates, wards }]
        const puneBase = MOCK_LOCATIONS.find((l) => l.id === 'pune') || MOCK_LOCATIONS[0];
        const wardLocations: LocationData[] = [];

        res.data.forEach((locDetail: any) => {
          if (Array.isArray(locDetail.wards)) {
            locDetail.wards.forEach((ward: any) => {
              const cleanId = (ward.name || ward.ward_code || 'ward')
                .toLowerCase()
                .replace(/[^a-z0-9]/g, '-');
              wardLocations.push({
                ...puneBase,
                id: cleanId,
                name: ward.name,
                state: locDetail.state || 'Maharashtra',
                country: locDetail.country || 'India',
                lat: ward.coordinates?.latitude ?? puneBase.lat,
                lng: ward.coordinates?.longitude ?? puneBase.lng,
                status_explanation: ward.description || puneBase.status_explanation,
              });
            });
          }
        });

        // Combine primary regional nodes (Pune, Mumbai, etc.) with Pune micro-wards
        const combined = [
          ...MOCK_LOCATIONS,
          ...wardLocations.filter((w) => !MOCK_LOCATIONS.some((m) => m.id === w.id)),
        ];

        return {
          data: combined,
          isMock: false,
          status: 'success',
          sourceUrl: `${API_BASE_URL}${API_V1}/locations`,
          timestamp,
        };
      }

      return {
        data: MOCK_LOCATIONS,
        isMock: false,
        status: 'success',
        sourceUrl: `${API_BASE_URL}${API_V1}/locations`,
        timestamp,
      };
    } catch (err) {
      return {
        data: MOCK_LOCATIONS,
        isMock: true,
        status: 'fallback',
        sourceUrl: 'local://mockData/locations (fallback)',
        timestamp,
        error: (err as AxiosError).message,
      };
    }
  }

  /**
   * Fetch complete climate summary for a location
   * Connects to GET /api/v1/risk-score?location={location}
   */
  public async getClimateSummary(
    locationQuery: string = 'pune'
  ): Promise<ServiceResponse<LocationData>> {
    const timestamp = '2026-11-09T13:45:00Z';
    const mockMatch = this.getMockLocation(locationQuery);

    if (FORCE_MOCK) {
      return {
        data: mockMatch,
        isMock: true,
        status: 'success',
        sourceUrl: `local://mockData/summary/${mockMatch.id}`,
        timestamp,
      };
    }

    try {
      const cleanQ = locationQuery.trim();
      const isWard = ['shivajinagar', 'kothrud', 'hadapsar', 'lohegaon', 'hinjawadi', 'katraj'].some(
        (w) => cleanQ.toLowerCase().includes(w)
      );

      const params: Record<string, string> = isWard
        ? { location: 'Pune', ward: cleanQ }
        : { location: cleanQ };

      const res = await this.client.get<InitialIntegrationContract>(
        `${API_V1}/risk-score`,
        { params }
      );

      const apiData = res.data;
      const score = apiData.climate_risk_score ?? mockMatch.climate_risk_score;
      const merged: LocationData = {
        ...mockMatch,
        name: apiData.location || mockMatch.name,
        climate_risk_score: score,
        risk_level: (apiData.risk_level as RiskCategory) || getRiskCategory(score),
        metrics: {
          ...mockMatch.metrics,
          temperature: apiData.temperature ?? mockMatch.metrics.temperature,
          rainfall: apiData.rainfall ?? mockMatch.metrics.rainfall,
          aqi: apiData.aqi ?? mockMatch.metrics.aqi,
        },
        risks: {
          heat: Math.round(apiData.risks?.heat ?? mockMatch.risks.heat),
          flood: Math.round(apiData.risks?.flood ?? mockMatch.risks.flood),
          air_quality: Math.round(apiData.risks?.air_quality ?? mockMatch.risks.air_quality),
          water_stress: Math.round(apiData.risks?.water_stress ?? mockMatch.risks.water_stress),
        },
        isMock: false,
      };

      return {
        data: merged,
        isMock: false,
        status: 'success',
        sourceUrl: `${API_BASE_URL}${API_V1}/risk-score?location=${locationQuery}`,
        timestamp,
      };
    } catch (err) {
      return {
        data: mockMatch,
        isMock: true,
        status: 'fallback',
        sourceUrl: `local://mockData/summary/${mockMatch.id} (fallback)`,
        timestamp,
        error: `FastAPI backend unavailable (${(err as AxiosError).message || 'offline'}). Serving illustrative mock contract.`,
      };
    }
  }

  /**
   * Fetch historical trend data for Recharts
   * Connects to GET /api/v1/history?location={location}
   */
  public async getHistoricalTrends(
    locationId: string = 'pune',
    timeRange: '24h' | '7d' | '30d' | '1y' = '7d'
  ): Promise<ServiceResponse<HistoricalDataPoint[]>> {
    const timestamp = '2026-11-09T13:45:00Z';
    const fallbackData =
      MOCK_HISTORICAL_DATA[locationId.toLowerCase()] ||
      MOCK_HISTORICAL_DATA['pune'];

    if (FORCE_MOCK) {
      return {
        data: fallbackData,
        isMock: true,
        status: 'success',
        sourceUrl: `local://mockData/history/${locationId}`,
        timestamp,
      };
    }

    try {
      const res = await this.client.get<HistoricalDataPoint[]>(`${API_V1}/history`, {
        params: { location: locationId, range: timeRange },
      });
      return {
        data: res.data && res.data.length > 0 ? res.data : fallbackData,
        isMock: false,
        status: 'success',
        sourceUrl: `${API_BASE_URL}${API_V1}/history?location=${locationId}`,
        timestamp,
      };
    } catch (err) {
      return {
        data: fallbackData,
        isMock: true,
        status: 'fallback',
        sourceUrl: `local://mockData/history/${locationId} (fallback)`,
        timestamp,
        error: (err as AxiosError).message,
      };
    }
  }

  /**
   * Fetch recommendations by stakeholder
   * Connects to GET /api/v1/recommendations
   */
  public async getRecommendations(
    stakeholder?: string
  ): Promise<ServiceResponse<RecommendationItem[]>> {
    const timestamp = '2026-11-09T13:45:00Z';
    let filtered = MOCK_RECOMMENDATIONS;
    if (stakeholder && stakeholder !== 'all') {
      filtered = filtered.filter((r) => r.stakeholder === stakeholder);
    }

    if (FORCE_MOCK) {
      return {
        data: filtered,
        isMock: true,
        status: 'success',
        sourceUrl: 'local://mockData/recommendations',
        timestamp,
      };
    }

    try {
      const res = await this.client.get<RecommendationItem[]>(`${API_V1}/recommendations`, {
        params: { stakeholder },
      });
      return {
        data: res.data && res.data.length > 0 ? res.data : filtered,
        isMock: false,
        status: 'success',
        sourceUrl: `${API_BASE_URL}${API_V1}/recommendations`,
        timestamp,
      };
    } catch (err) {
      return {
        data: filtered,
        isMock: true,
        status: 'fallback',
        sourceUrl: 'local://mockData/recommendations (fallback)',
        timestamp,
        error: (err as AxiosError).message,
      };
    }
  }

  /**
   * Run What-If climate simulation
   * Connects to POST /api/v1/simulate
   */
  public async runSimulation(
    location: LocationData,
    params: SimulationParams
  ): Promise<ServiceResponse<SimulationResult>> {
    const timestamp = '2026-11-09T13:45:00Z';
    const demoCalc = calculateIllustrativeSimulation(location, params);

    if (FORCE_MOCK) {
      return {
        data: demoCalc,
        isMock: true,
        status: 'success',
        sourceUrl: 'client://illustrativeSimulationEngine',
        timestamp,
      };
    }

    try {
      const res = await this.client.post(`${API_V1}/simulate`, {
        location: location.name,
        deltas: {
          rainfall_pct: params.rainfallPercentChange,
          temperature_delta_c: params.tempIncrease,
          aqi_pct: params.aqiDelta,
          impervious_surface_delta_pct: params.humidityDelta,
        },
      });

      const resData = res.data;
      if (resData && resData.simulated_risk) {
        const simRisk = resData.simulated_risk;
        const baseRisk = resData.baseline_risk;
        const mappedResult: SimulationResult = {
          baselineRiskScore: baseRisk.climate_risk_score,
          simulatedRiskScore: simRisk.climate_risk_score,
          riskDelta: resData.score_delta,
          baselineLevel: baseRisk.risk_level as RiskCategory,
          simulatedLevel: simRisk.risk_level as RiskCategory,
          hazardDeltas: {
            heat: {
              baseline: baseRisk.risks.heat,
              simulated: simRisk.risks.heat,
              delta: resData.hazard_deltas?.heat ?? 0,
            },
            flood: {
              baseline: baseRisk.risks.flood,
              simulated: simRisk.risks.flood,
              delta: resData.hazard_deltas?.flood ?? 0,
            },
            air_quality: {
              baseline: baseRisk.risks.air_quality,
              simulated: simRisk.risks.air_quality,
              delta: resData.hazard_deltas?.air_quality ?? 0,
            },
            water_stress: {
              baseline: baseRisk.risks.water_stress,
              simulated: simRisk.risks.water_stress,
              delta: resData.hazard_deltas?.water_stress ?? 0,
            },
          },
          featureImportance: demoCalc.featureImportance,
          narrativeSummary: resData.scenario_summary || demoCalc.narrativeSummary,
          isIllustrativeDemo: false,
        };

        return {
          data: mappedResult,
          isMock: false,
          status: 'success',
          sourceUrl: `${API_BASE_URL}${API_V1}/simulate`,
          timestamp,
        };
      }

      return {
        data: demoCalc,
        isMock: true,
        status: 'success',
        sourceUrl: 'client://illustrativeSimulationEngine',
        timestamp,
      };
    } catch (err) {
      return {
        data: demoCalc,
        isMock: true,
        status: 'fallback',
        sourceUrl: 'client://illustrativeSimulationEngine (fallback)',
        timestamp,
        error: `ML simulation endpoint offline (${(err as AxiosError).message || 'offline'}). Serving illustrative demo estimate.`,
      };
    }
  }
}

export const climateApi = new ClimateApiService();
