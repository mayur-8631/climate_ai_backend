'use client';

import React from 'react';
import {
  AlertTriangle,
  Flame,
  CloudRain,
  Wind,
  Droplets,
  ArrowRight,
  ShieldCheck,
  BellRing,
  Info,
} from 'lucide-react';
import { ClimateInsight, LocationData } from '@/types/climate';
import { Badge } from '@/components/ui/Badge';
import Link from 'next/link';

interface InsightsPanelProps {
  location: LocationData;
  insights: ClimateInsight[];
}

export function InsightsPanel({ location, insights }: InsightsPanelProps) {
  // Determine highest climate risk
  const risks = location.risks;
  const riskEntries = [
    { key: 'heat', name: 'Extreme Heat', score: risks.heat, icon: Flame, color: '#F97316' },
    { key: 'flood', name: 'Precipitation / Flood', score: risks.flood, icon: CloudRain, color: '#06B6D4' },
    { key: 'air_quality', name: 'Air Quality (AQI)', score: risks.air_quality, icon: Wind, color: '#A855F7' },
    { key: 'water_stress', name: 'Aquifer Water Stress', score: risks.water_stress, icon: Droplets, color: '#3B82F6' },
  ];
  const highestRisk = [...riskEntries].sort((a, b) => b.score - a.score)[0];

  return (
    <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-5 sm:p-6 shadow-xl shadow-black/20 space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between pb-3 border-b border-[#1A3954]/70">
        <div>
          <span className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold flex items-center gap-1.5">
            <BellRing className="w-3.5 h-3.5 text-cyan-400" />
            Early Warning & Vulnerability Diagnostics
          </span>
          <h3 className="text-lg font-bold text-white mt-0.5">
            Climate Intelligence Insights
          </h3>
        </div>
        <Badge variant="cyan" size="sm">
          {insights.length} Active Feeds
        </Badge>
      </div>

      {/* Highest Risk Highlight Banner */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-orange-500/15 via-[#0E273F] to-[#081B2B] border border-orange-500/30 flex items-start gap-3.5">
        <div className="w-10 h-10 rounded-xl bg-orange-500/20 text-orange-400 flex items-center justify-center shrink-0 border border-orange-500/30">
          <highestRisk.icon className="w-5 h-5" />
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-mono uppercase text-orange-400 font-bold">
              Dominant Hazard Driver
            </span>
            <span className="text-xs font-mono bg-orange-500/20 text-orange-300 px-2 py-0.5 rounded-full font-bold">
              Score: {highestRisk.score}/100
            </span>
          </div>
          <h4 className="text-base font-bold text-white mt-1">
            {highestRisk.name} is the Primary Threat in {location.name}
          </h4>
          <p className="text-xs text-slate-300 mt-1 leading-relaxed">
            Multivariate analysis isolates {highestRisk.name.toLowerCase()} as contributing the highest weighted share to the composite vulnerability index.
          </p>
        </div>
      </div>

      {/* List of Insights / Alerts */}
      <div className="space-y-3">
        {insights.map((item) => {
          let severityBadge = (
            <Badge variant="slate" size="sm">
              Info
            </Badge>
          );
          if (item.severity === 'critical') {
            severityBadge = (
              <Badge variant="rose" size="sm" dot>
                Critical Alert
              </Badge>
            );
          } else if (item.severity === 'high') {
            severityBadge = (
              <Badge variant="orange" size="sm">
                High Priority
              </Badge>
            );
          } else if (item.severity === 'medium') {
            severityBadge = (
              <Badge variant="amber" size="sm">
                Watch
              </Badge>
            );
          } else if (item.severity === 'low') {
            severityBadge = (
              <Badge variant="emerald" size="sm">
                Stable
              </Badge>
            );
          }

          return (
            <div
              key={item.id}
              className="p-3.5 rounded-xl bg-[#081B2B] border border-[#1A3954]/70 hover:border-cyan-500/30 transition-all duration-150"
            >
              <div className="flex items-start justify-between gap-2 mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-xs font-semibold text-white">
                    {item.title}
                  </span>
                </div>
                <div className="shrink-0">{severityBadge}</div>
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {item.description}
              </p>

              {/* Action Suggestion */}
              <div className="mt-2.5 pt-2 border-t border-[#1A3954]/50 flex items-center justify-between text-[11px] text-cyan-300/90 gap-2">
                <span className="truncate">
                  <strong className="text-slate-400">Action:</strong>{' '}
                  {item.suggestedAction}
                </span>
                <span className="text-[10px] font-mono text-slate-500 shrink-0">
                  {item.timeframe}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Direct link to recommendations */}
      <div className="pt-2">
        <Link
          href="/recommendations"
          className="w-full py-2.5 px-4 rounded-xl bg-[#0D2439] hover:bg-[#122F4C] border border-cyan-500/30 text-cyan-300 text-xs font-semibold flex items-center justify-center gap-2 transition-colors"
        >
          <span>View Comprehensive Stakeholder Recommendations</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </Link>
      </div>
    </div>
  );
}

