'use client';

import React, { useState } from 'react';
import {
  Sliders,
  Sparkles,
  Activity,
  Brain,
  ShieldAlert,
  Play,
  RotateCcw,
  Zap,
} from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { SimulationSliders } from '@/components/simulation/SimulationSliders';
import { SimulationComparison } from '@/components/simulation/SimulationComparison';
import { FeatureImportanceChart } from '@/components/simulation/FeatureImportanceChart';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { Badge } from '@/components/ui/Badge';
import { useClimate } from '@/context/ClimateContext';
import { SimulationParams, SimulationResult } from '@/types/climate';
import { calculateIllustrativeSimulation } from '@/utils/riskCalculator';
import { climateApi } from '@/services/api';

const DEFAULT_SIM_PARAMS: SimulationParams = {
  rainfallPercentChange: 25,
  tempIncrease: 2.1,
  humidityDelta: 10,
  aqiDelta: 40,
};

export default function SimulationPage() {
  const { selectedLocation } = useClimate();
  const [params, setParams] = useState<SimulationParams>(DEFAULT_SIM_PARAMS);
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Initial calculation
  const [simulationResult, setSimulationResult] = useState<SimulationResult>(() =>
    calculateIllustrativeSimulation(selectedLocation, DEFAULT_SIM_PARAMS)
  );

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const res = await climateApi.runSimulation(selectedLocation, params);
      setSimulationResult(res.data);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleReset = () => {
    setParams(DEFAULT_SIM_PARAMS);
    setSimulationResult(
      calculateIllustrativeSimulation(selectedLocation, DEFAULT_SIM_PARAMS)
    );
  };

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Transparent Honesty Banner as required in Section 7 */}
        <DisclaimerBanner type="simulation-demo" />

        {/* Page Title */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1A3954]/70">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                What-If Climate Scenario Simulation
              </h1>
              <Badge variant="cyan" size="sm">
                Interactive Lab
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Simulate localized multi-hazard responses under compound precipitation, thermal, aerosol, and moisture shocks for{' '}
              <strong className="text-slate-200">{selectedLocation.name}</strong>.
            </p>
          </div>

          <div className="flex items-center gap-2 text-xs font-mono text-cyan-300 bg-[#0E263D] px-3 py-1.5 rounded-lg border border-cyan-500/30">
            <Brain className="w-4 h-4 text-cyan-400" />
            <span>Swappable with Team PrithviNex ML API</span>
          </div>
        </div>

        {/* Section 7 Sliders & Numeric Controls */}
        <SimulationSliders
          params={params}
          onChange={setParams}
          onRunSimulation={handleRunSimulation}
          onReset={handleReset}
          isLoading={isSimulating}
        />

        {/* Section 7 Visual Comparison Output */}
        <SimulationComparison
          location={selectedLocation}
          result={simulationResult}
        />

        {/* Section 8 Explainable AI Feature Importance Visualization */}
        <FeatureImportanceChart
          features={simulationResult.featureImportance}
        />
      </div>
    </AppShell>
  );
}

