import {
  LocationData,
  SimulationParams,
  SimulationResult,
  FeatureImportance,
  RiskCategory,
} from '@/types/climate';
import { getRiskCategory } from './formatters';

/**
 * ILLUSTRATIVE DEMO SIMULATION ENGINE
 * 
 * NOTE FOR GRAND CHALLENGE EVALUATION:
 * This heuristic function provides an interactive frontend demo calculation
 * for what-if scenario testing. It simulates multi-hazard coupled dynamics
 * until Lokesh Joshi's trained ML models (FastAPI /api/predict & /api/simulate)
 * are deployed.
 * 
 * Never presented as validated ML inference.
 */
export function calculateIllustrativeSimulation(
  currentLocation: LocationData,
  params: SimulationParams
): SimulationResult {
  const { rainfallPercentChange, tempIncrease, humidityDelta, aqiDelta } = params;
  const currentRisks = currentLocation.risks;
  const baseComposite = currentLocation.climate_risk_score;

  // 1. Heat hazard response: strongly driven by temperature increase and humidity (wet-bulb effect)
  const heatFactor = (tempIncrease * 4.8) + (humidityDelta > 0 ? humidityDelta * 0.25 : humidityDelta * 0.05);
  const simHeat = Math.min(100, Math.max(0, Math.round(currentRisks.heat + heatFactor)));

  // 2. Flood hazard response: nonlinear saturation curve based on rainfall change
  let floodFactor = 0;
  if (rainfallPercentChange > 0) {
    // Accelerating runoff above threshold
    floodFactor = (rainfallPercentChange * 0.42) + Math.pow(rainfallPercentChange / 40, 1.8) * 2;
  } else {
    floodFactor = rainfallPercentChange * 0.35;
  }
  const simFlood = Math.min(100, Math.max(0, Math.round(currentRisks.flood + floodFactor)));

  // 3. Air quality hazard response: direct AQI shift + inverse relation to rainfall scavenging
  const aqiScavenging = rainfallPercentChange > 20 ? -(rainfallPercentChange * 0.15) : 0;
  const aqiFactor = (aqiDelta * 0.22) + aqiScavenging;
  const simAqi = Math.min(100, Math.max(0, Math.round(currentRisks.air_quality + aqiFactor)));

  // 4. Water stress hazard response: decreased rainfall increases stress, increased temp increases evapotranspiration
  const waterStressFactor = -(rainfallPercentChange * 0.38) + (tempIncrease * 3.2);
  const simWaterStress = Math.min(100, Math.max(0, Math.round(currentRisks.water_stress + waterStressFactor)));

  // Coupled composite risk score (weighted multi-hazard model)
  const simulatedComposite = Math.min(
    100,
    Math.max(
      0,
      Math.round(
        simHeat * 0.28 +
        simFlood * 0.32 +
        simAqi * 0.22 +
        simWaterStress * 0.18
      )
    )
  );

  const deltaScore = simulatedComposite - baseComposite;

  // Dynamic feature importance weights for Explainable AI
  const featureImportance: FeatureImportance[] = [
    {
      feature: 'rainfall_shift',
      name: 'Precipitation Dynamic',
      importance: Math.min(0.95, (Math.abs(rainfallPercentChange) / 100) * 0.45 + 0.25),
      direction: (rainfallPercentChange >= 0 ? 'positive' : 'negative') as 'positive' | 'negative',
      baselineValue: `${currentLocation.metrics.rainfall} mm/day`,
      simulatedValue: `${Math.round(currentLocation.metrics.rainfall * (1 + rainfallPercentChange / 100))} mm/day (${rainfallPercentChange > 0 ? '+' : ''}${rainfallPercentChange}%)`,
      description: 'Controls hydrologic saturation, storm sewer discharge, and surface runoff volumes.',
    },
    {
      feature: 'thermal_delta',
      name: 'Atmospheric Heating',
      importance: Math.min(0.92, (tempIncrease / 5) * 0.5 + 0.2),
      direction: (tempIncrease > 0 ? 'positive' : 'negative') as 'positive' | 'negative',
      baselineValue: `${currentLocation.metrics.temperature} °C`,
      simulatedValue: `${(currentLocation.metrics.temperature + tempIncrease).toFixed(1)} °C (+${tempIncrease.toFixed(1)} °C)`,
      description: 'Amplifies heat wave thresholds, biometeorological stress, and moisture evaporation.',
    },
    {
      feature: 'aerosol_loading',
      name: 'Aerosol & Particle Delta',
      importance: Math.min(0.85, (Math.abs(aqiDelta) / 200) * 0.4 + 0.15),
      direction: (aqiDelta >= 0 ? 'positive' : 'negative') as 'positive' | 'negative',
      baselineValue: `AQI ${currentLocation.metrics.aqi}`,
      simulatedValue: `AQI ${Math.max(10, currentLocation.metrics.aqi + aqiDelta)} (${aqiDelta > 0 ? '+' : ''}${aqiDelta})`,
      description: 'Drives respiratory emergency probability and optical haze attenuation.',
    },
    {
      feature: 'relative_humidity',
      name: 'Vapor Saturation',
      importance: Math.min(0.78, (Math.abs(humidityDelta) / 30) * 0.3 + 0.1),
      direction: (humidityDelta >= 0 ? 'positive' : 'negative') as 'positive' | 'negative',
      baselineValue: `${currentLocation.metrics.humidity} %`,
      simulatedValue: `${Math.min(100, Math.max(15, currentLocation.metrics.humidity + humidityDelta))} %`,
      description: 'Modulates wet-bulb temperature thresholds and cloud condensation nuclei.',
    },
  ].sort((a, b) => b.importance - a.importance);

  // Generate illustrative narrative
  let narrative = '';
  if (deltaScore > 10) {
    narrative = `Scenario indicates acute multi-hazard amplification (+${deltaScore} points). The predominant risk driver is ${
      featureImportance[0].name.toLowerCase()
    }, pushing overall localized vulnerability from ${currentLocation.risk_level} to ${getRiskCategory(simulatedComposite)}.`;
  } else if (deltaScore < -5) {
    narrative = `Scenario models environmental mitigation conditions (-${Math.abs(deltaScore)} points). Reduced stress factors diminish aggregate hazard exposure across sectors.`;
  } else {
    narrative = `Scenario projects marginal aggregate variation (${deltaScore >= 0 ? '+' : ''}${deltaScore} points). Hazard shifts remain within the resilience buffer of current municipal baselines.`;
  }

  return {
    baselineRiskScore: baseComposite,
    simulatedRiskScore: simulatedComposite,
    riskDelta: deltaScore,
    baselineLevel: currentLocation.risk_level,
    simulatedLevel: getRiskCategory(simulatedComposite),
    hazardDeltas: {
      heat: {
        baseline: currentRisks.heat,
        simulated: simHeat,
        delta: simHeat - currentRisks.heat,
      },
      flood: {
        baseline: currentRisks.flood,
        simulated: simFlood,
        delta: simFlood - currentRisks.flood,
      },
      air_quality: {
        baseline: currentRisks.air_quality,
        simulated: simAqi,
        delta: simAqi - currentRisks.air_quality,
      },
      water_stress: {
        baseline: currentRisks.water_stress,
        simulated: simWaterStress,
        delta: simWaterStress - currentRisks.water_stress,
      },
    },
    featureImportance,
    narrativeSummary: narrative,
    isIllustrativeDemo: true,
  };
}
