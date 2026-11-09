'use client';

import React from 'react';
import {
  Brain,
  Sparkles,
  HelpCircle,
  Cpu,
  BarChart3,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { LocationData, FeatureImportance } from '@/types/climate';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { Badge } from '@/components/ui/Badge';
import Link from 'next/link';

interface ExplainableSectionProps {
  location: LocationData;
}

export function ExplainableSection({ location }: ExplainableSectionProps) {
  // Illustrative feature importance weights for the location
  // Designed to map 1:1 with Lokesh Joshi's SHAP output schema
  const featureWeights: FeatureImportance[] = [
    {
      feature: 'thermal_island_intensity',
      name: 'Urban Heat Island Index',
      importance: 0.38,
      direction: 'positive',
      baselineValue: `${location.risks.heat}/100`,
      description: 'Satellite thermal infrared indicates high surface heat storage in concrete built-up areas.',
    },
    {
      feature: 'runoff_saturation_rate',
      name: 'Precipitation Runoff Saturation',
      importance: 0.28,
      direction: 'positive',
      baselineValue: `${location.metrics.rainfall} mm/24h`,
      description: 'Impervious urban canopy reduces natural soil infiltration, elevating stormwater volume.',
    },
    {
      feature: 'aerosol_optical_depth',
      name: 'Aerosol Optical Depth (AQI)',
      importance: 0.20,
      direction: 'positive',
      baselineValue: `AQI ${location.metrics.aqi}`,
      description: 'Vehicular particulate matter trapped by low nocturnal planetary boundary layers.',
    },
    {
      feature: 'aquifer_storage_deficit',
      name: 'Aquifer Deficit & Recharge Gap',
      importance: 0.14,
      direction: 'positive',
      baselineValue: `${location.risks.water_stress}/100`,
      description: 'Summer drawdown rate relative to monsoon reservoir replenishment volume.',
    },
  ];

  return (
    <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-5 sm:p-6 shadow-xl shadow-black/20 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1A3954]/70">
        <div>
          <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold flex items-center gap-1.5">
            <Brain className="w-3.5 h-3.5 text-cyan-400" />
            Explainable AI Architecture (XAI)
          </div>
          <h3 className="text-lg font-bold text-white mt-0.5">
            Why {location.name} Received a Score of {location.climate_risk_score}/100
          </h3>
        </div>

        <Badge variant="cyan" size="sm">
          SHAP-Ready Schema
        </Badge>
      </div>

      <DisclaimerBanner type="feature-importance" compact />

      {/* Narrative Synthesis */}
      <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954]/70">
        <h4 className="text-xs font-mono uppercase text-slate-400 font-semibold mb-1 flex items-center gap-1.5">
          <Cpu className="w-3.5 h-3.5 text-cyan-400" />
          Multi-Factor Attribution Summary
        </h4>
        <p className="text-xs text-slate-300 leading-relaxed">
          The composite risk score of <strong className="text-cyan-300 font-semibold">{location.climate_risk_score}/100 ({location.risk_level})</strong> is a weighted ensemble calculation. The primary hazard driving localized vulnerability is <strong className="text-orange-400">{location.risk_details.heat.explanation}</strong>, compounded by secondary runoff exposure during peak downpours.
        </p>
      </div>

      {/* Feature Importance Attribution Bars */}
      <div>
        <div className="flex items-center justify-between text-xs text-slate-300 font-medium mb-3">
          <span>Environmental Feature Importance Distribution</span>
          <span className="text-[10px] font-mono text-slate-400">Relative Weight (%)</span>
        </div>

        <div className="space-y-3.5">
          {featureWeights.map((f, i) => {
            const pct = Math.round(f.importance * 100);
            return (
              <div key={i} className="space-y-1.5">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-medium text-slate-200 flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                    {f.name}
                  </span>
                  <div className="flex items-center gap-2">
                    <span className="text-[11px] font-mono text-slate-400">
                      Baseline: {f.baselineValue}
                    </span>
                    <span className="text-xs font-mono font-bold text-cyan-300 bg-cyan-500/10 px-1.5 py-0.5 rounded border border-cyan-500/30">
                      {pct}%
                    </span>
                  </div>
                </div>

                {/* Progress track */}
                <div className="h-2 w-full bg-[#10273D] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-cyan-400 rounded-full transition-all duration-500"
                    style={{ width: `${pct * 2.5}%` }}
                  />
                </div>

                <p className="text-[11px] text-slate-400 leading-tight pl-3.5">
                  {f.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Simulation Playground teaser */}
      <div className="pt-2">
        <Link
          href="/simulation"
          className="w-full py-2.5 px-4 rounded-xl bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 hover:from-emerald-500/20 hover:to-cyan-500/20 border border-emerald-500/30 text-emerald-300 text-xs font-semibold flex items-center justify-center gap-2 transition-all"
        >
          <span>Run Interactive What-If Climate Simulation for {location.name}</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}

