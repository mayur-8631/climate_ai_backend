'use client';

import React from 'react';
import {
  Flame,
  CloudRain,
  Wind,
  Droplets,
  TrendingUp,
  TrendingDown,
  Minus,
  AlertCircle,
} from 'lucide-react';
import { HazardType, HazardDetail } from '@/types/climate';
import { getRiskCategory, getRiskColor, getHazardMeta } from '@/utils/formatters';
import { Badge } from '@/components/ui/Badge';

interface RiskCardProps {
  hazard: HazardType;
  detail: HazardDetail;
}

export function RiskCard({ hazard, detail }: RiskCardProps) {
  const meta = getHazardMeta(hazard);
  const colorData = getRiskColor(detail.level);

  // Icon selector
  const renderIcon = () => {
    switch (hazard) {
      case 'heat':
        return <Flame className="w-5 h-5" />;
      case 'flood':
        return <CloudRain className="w-5 h-5" />;
      case 'air_quality':
        return <Wind className="w-5 h-5" />;
      case 'water_stress':
        return <Droplets className="w-5 h-5" />;
    }
  };

  // Trend icon selector
  const renderTrendIcon = () => {
    if (detail.trend === 'increasing') {
      return <TrendingUp className="w-3.5 h-3.5 text-rose-400" />;
    }
    if (detail.trend === 'decreasing') {
      return <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />;
    }
    return <Minus className="w-3.5 h-3.5 text-slate-400" />;
  };

  return (
    <div className="relative overflow-hidden rounded-xl bg-gradient-to-b from-[#0D243A] to-[#081B2B] border border-[#1A3954] hover:border-cyan-400/40 p-5 shadow-lg shadow-black/20 transition-all duration-200 group flex flex-col justify-between">
      {/* Accent corner line */}
      <div
        className="absolute top-0 left-0 right-0 h-1 transition-all duration-300"
        style={{ backgroundColor: colorData.hex }}
      />

      {/* Top Header */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2.5">
            <div
              className="w-9 h-9 rounded-lg flex items-center justify-center transition-transform group-hover:scale-105"
              style={{
                backgroundColor: `${colorData.hex}18`,
                color: colorData.hex,
                border: `1px solid ${colorData.hex}30`,
              }}
            >
              {renderIcon()}
            </div>
            <div>
              <h3 className="text-sm font-semibold text-white tracking-tight">
                {meta.name}
              </h3>
              <span className="text-[11px] font-mono text-slate-400">
                {meta.unit}
              </span>
            </div>
          </div>

          <Badge riskLevel={detail.level} size="sm">
            {detail.level}
          </Badge>
        </div>

        {/* Score & Progress Bar */}
        <div className="my-3">
          <div className="flex items-baseline justify-between mb-1.5">
            <div className="flex items-baseline gap-1.5">
              <span
                className="text-3xl font-extrabold font-mono tracking-tight"
                style={{ color: colorData.hex }}
              >
                {detail.score}
              </span>
              <span className="text-xs text-slate-400 font-mono">/ 100</span>
            </div>

            <div className="flex items-center gap-1 text-xs text-slate-300 bg-[#071827]/80 px-2 py-0.5 rounded-md border border-[#1A3954]">
              {renderTrendIcon()}
              <span className="text-[11px] font-mono">{detail.trendValue}</span>
            </div>
          </div>

          {/* Bar Gauge */}
          <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
            <div
              className="h-full rounded-full transition-all duration-700 ease-out"
              style={{
                width: `${Math.min(100, Math.max(0, detail.score))}%`,
                backgroundColor: colorData.hex,
              }}
            />
          </div>
        </div>

        {/* Explanation */}
        <p className="text-xs text-slate-300 leading-relaxed line-clamp-3 mb-3">
          {detail.explanation}
        </p>
      </div>

      {/* Contributing Factors Tags */}
      <div className="pt-3 border-t border-[#1A3954]/60">
        <div className="text-[10px] text-slate-400 font-mono uppercase tracking-wider mb-1.5">
          Key Drivers
        </div>
        <div className="flex flex-wrap gap-1.5">
          {detail.contributingFactors.slice(0, 3).map((factor, idx) => (
            <span
              key={idx}
              className="text-[10px] px-2 py-0.5 rounded-md bg-[#071827] text-slate-300 border border-[#1A3954]/80 truncate max-w-full"
            >
              {factor}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

