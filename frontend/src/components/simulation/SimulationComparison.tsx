'use client';

import React from 'react';
import {
  Flame,
  CloudRain,
  Wind,
  Droplets,
  TrendingUp,
  TrendingDown,
  ArrowRight,
  Shield,
  Activity,
  Layers,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { SimulationResult, LocationData } from '@/types/climate';
import { getRiskCategory, getRiskColor } from '@/utils/formatters';
import { Badge } from '@/components/ui/Badge';

interface SimulationComparisonProps {
  location: LocationData;
  result: SimulationResult;
}

export function SimulationComparison({
  location,
  result,
}: SimulationComparisonProps) {
  const baseCategory = result.baselineLevel;
  const simCategory = result.simulatedLevel;
  const baseColor = getRiskColor(baseCategory);
  const simColor = getRiskColor(simCategory);

  // Prepare data for comparison chart
  const comparisonChartData = [
    {
      hazard: 'Composite',
      Baseline: result.baselineRiskScore,
      Simulated: result.simulatedRiskScore,
    },
    {
      hazard: 'Heat',
      Baseline: result.hazardDeltas.heat.baseline,
      Simulated: result.hazardDeltas.heat.simulated,
    },
    {
      hazard: 'Flood',
      Baseline: result.hazardDeltas.flood.baseline,
      Simulated: result.hazardDeltas.flood.simulated,
    },
    {
      hazard: 'AQI',
      Baseline: result.hazardDeltas.air_quality.baseline,
      Simulated: result.hazardDeltas.air_quality.simulated,
    },
    {
      hazard: 'Water Stress',
      Baseline: result.hazardDeltas.water_stress.baseline,
      Simulated: result.hazardDeltas.water_stress.simulated,
    },
  ];

  return (
    <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-5 sm:p-6 shadow-xl shadow-black/20 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#1A3954]/70">
        <div>
          <div className="text-[10px] font-mono tracking-wider uppercase text-emerald-400 font-semibold flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            Simulation Output & Impact Analytics
          </div>
          <h3 className="text-lg font-bold text-white mt-0.5">
            Baseline vs. Simulated Risk Transition
          </h3>
        </div>

        <Badge
          variant={result.riskDelta > 0 ? 'rose' : result.riskDelta < 0 ? 'emerald' : 'cyan'}
          size="md"
        >
          {result.riskDelta > 0 ? `+${result.riskDelta}` : result.riskDelta} Points Delta
        </Badge>
      </div>

      {/* Main Score Comparison Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-center">
        {/* Baseline Card */}
        <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954] text-center">
          <div className="text-[11px] font-mono uppercase text-slate-400 mb-1">
            Current Baseline Score
          </div>
          <div
            className="text-4xl font-extrabold font-mono tracking-tight"
            style={{ color: baseColor.hex }}
          >
            {result.baselineRiskScore}
          </div>
          <div className="mt-1">
            <Badge riskLevel={baseCategory} size="sm">
              {baseCategory}
            </Badge>
          </div>
          <div className="text-[11px] text-slate-400 mt-2">
            Baseline telemetry for {location.name}
          </div>
        </div>

        {/* Transition Indicator */}
        <div className="flex flex-col items-center justify-center p-2 text-center">
          <div className="flex items-center gap-2 text-slate-400 font-mono text-xs uppercase mb-1">
            <span>Shift Delta</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-full bg-[#10273D] border border-[#1A3954] flex items-center justify-center text-cyan-400">
              <ArrowRight className="w-4 h-4" />
            </div>
            <span
              className={`text-2xl font-black font-mono ${
                result.riskDelta > 0
                  ? 'text-rose-400'
                  : result.riskDelta < 0
                  ? 'text-emerald-400'
                  : 'text-slate-400'
              }`}
            >
              {result.riskDelta > 0 ? `+${result.riskDelta}` : result.riskDelta}
            </span>
          </div>
          <div className="text-[11px] text-slate-300 mt-1 font-medium">
            {result.baselineLevel} &rarr; {result.simulatedLevel}
          </div>
        </div>

        {/* Simulated Score Card */}
        <div className="p-4 rounded-xl bg-gradient-to-b from-[#0F2A42] to-[#0A1F33] border border-cyan-500/30 text-center shadow-lg shadow-cyan-500/5">
          <div className="text-[11px] font-mono uppercase text-cyan-400 mb-1 font-semibold">
            Simulated Scenario Score
          </div>
          <div
            className="text-4xl font-extrabold font-mono tracking-tight"
            style={{ color: simColor.hex }}
          >
            {result.simulatedRiskScore}
          </div>
          <div className="mt-1">
            <Badge riskLevel={simCategory} size="sm" dot>
              {simCategory}
            </Badge>
          </div>
          <div className="text-[11px] text-slate-300 mt-2 font-medium">
            Under Simulated Climate Shocks
          </div>
        </div>
      </div>

      {/* Narrative Synthesis */}
      <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954]/80 text-xs text-slate-300 leading-relaxed">
        <strong className="text-cyan-300 font-semibold">Scenario Narrative: </strong>
        {result.narrativeSummary}
      </div>

      {/* Hazard-Specific Changes Grid */}
      <div>
        <div className="text-xs font-semibold text-slate-200 mb-3 uppercase tracking-wider font-mono">
          Hazard-Specific Delta Breakdown
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3.5">
          {/* Heat */}
          <div className="p-3.5 rounded-xl bg-[#081B2B] border border-[#1A3954] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-white flex items-center gap-1.5">
                <Flame className="w-3.5 h-3.5 text-orange-400" /> Heat Hazard
              </span>
              <span
                className={`font-mono text-xs font-bold ${
                  result.hazardDeltas.heat.delta > 0
                    ? 'text-rose-400'
                    : 'text-emerald-400'
                }`}
              >
                {result.hazardDeltas.heat.delta > 0 ? '+' : ''}
                {result.hazardDeltas.heat.delta}
              </span>
            </div>
            <div className="flex items-baseline justify-between text-xs text-slate-300 font-mono">
              <span>{result.hazardDeltas.heat.baseline}</span>
              <span className="text-slate-500">&rarr;</span>
              <span className="text-white font-bold">
                {result.hazardDeltas.heat.simulated}
              </span>
            </div>
            <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
              <div
                className="h-full bg-orange-400 rounded-full"
                style={{ width: `${result.hazardDeltas.heat.simulated}%` }}
              />
            </div>
          </div>

          {/* Flood */}
          <div className="p-3.5 rounded-xl bg-[#081B2B] border border-[#1A3954] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-white flex items-center gap-1.5">
                <CloudRain className="w-3.5 h-3.5 text-cyan-400" /> Flood Hazard
              </span>
              <span
                className={`font-mono text-xs font-bold ${
                  result.hazardDeltas.flood.delta > 0
                    ? 'text-rose-400'
                    : 'text-emerald-400'
                }`}
              >
                {result.hazardDeltas.flood.delta > 0 ? '+' : ''}
                {result.hazardDeltas.flood.delta}
              </span>
            </div>
            <div className="flex items-baseline justify-between text-xs text-slate-300 font-mono">
              <span>{result.hazardDeltas.flood.baseline}</span>
              <span className="text-slate-500">&rarr;</span>
              <span className="text-white font-bold">
                {result.hazardDeltas.flood.simulated}
              </span>
            </div>
            <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
              <div
                className="h-full bg-cyan-400 rounded-full"
                style={{ width: `${result.hazardDeltas.flood.simulated}%` }}
              />
            </div>
          </div>

          {/* Air Quality */}
          <div className="p-3.5 rounded-xl bg-[#081B2B] border border-[#1A3954] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-white flex items-center gap-1.5">
                <Wind className="w-3.5 h-3.5 text-purple-400" /> AQI Aerosol
              </span>
              <span
                className={`font-mono text-xs font-bold ${
                  result.hazardDeltas.air_quality.delta > 0
                    ? 'text-rose-400'
                    : 'text-emerald-400'
                }`}
              >
                {result.hazardDeltas.air_quality.delta > 0 ? '+' : ''}
                {result.hazardDeltas.air_quality.delta}
              </span>
            </div>
            <div className="flex items-baseline justify-between text-xs text-slate-300 font-mono">
              <span>{result.hazardDeltas.air_quality.baseline}</span>
              <span className="text-slate-500">&rarr;</span>
              <span className="text-white font-bold">
                {result.hazardDeltas.air_quality.simulated}
              </span>
            </div>
            <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
              <div
                className="h-full bg-purple-400 rounded-full"
                style={{ width: `${result.hazardDeltas.air_quality.simulated}%` }}
              />
            </div>
          </div>

          {/* Water Stress */}
          <div className="p-3.5 rounded-xl bg-[#081B2B] border border-[#1A3954] space-y-2">
            <div className="flex items-center justify-between text-xs">
              <span className="font-semibold text-white flex items-center gap-1.5">
                <Droplets className="w-3.5 h-3.5 text-blue-400" /> Water Stress
              </span>
              <span
                className={`font-mono text-xs font-bold ${
                  result.hazardDeltas.water_stress.delta > 0
                    ? 'text-rose-400'
                    : 'text-emerald-400'
                }`}
              >
                {result.hazardDeltas.water_stress.delta > 0 ? '+' : ''}
                {result.hazardDeltas.water_stress.delta}
              </span>
            </div>
            <div className="flex items-baseline justify-between text-xs text-slate-300 font-mono">
              <span>{result.hazardDeltas.water_stress.baseline}</span>
              <span className="text-slate-500">&rarr;</span>
              <span className="text-white font-bold">
                {result.hazardDeltas.water_stress.simulated}
              </span>
            </div>
            <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
              <div
                className="h-full bg-blue-400 rounded-full"
                style={{ width: `${result.hazardDeltas.water_stress.simulated}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Visual Recharts Bar Comparison Chart */}
      <div className="pt-2">
        <div className="text-xs font-semibold text-slate-200 mb-3 uppercase tracking-wider font-mono">
          Comparative Exposure Visualizer (0–100 Scale)
        </div>
        <div className="h-64 w-full bg-[#081B2B] rounded-xl p-3 border border-[#1A3954]/70">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={comparisonChartData}
              margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#1A3954" opacity={0.6} />
              <XAxis dataKey="hazard" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis domain={[0, 100]} stroke="#94A3B8" fontSize={11} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#0C2033',
                  borderColor: '#1A3954',
                  borderRadius: '0.75rem',
                  color: '#F8FAFC',
                  fontSize: '12px',
                }}
              />
              <Legend
                wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }}
              />
              <Bar dataKey="Baseline" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              <Bar dataKey="Simulated" fill="#10B981" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

