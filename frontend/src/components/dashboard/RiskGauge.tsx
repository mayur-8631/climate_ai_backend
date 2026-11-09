'use client';

import React from 'react';
import { Shield, AlertTriangle, ArrowUpRight, Clock, HelpCircle, Activity } from 'lucide-react';
import { getRiskCategory, getRiskColor, formatTimestamp } from '@/utils/formatters';
import { Badge } from '@/components/ui/Badge';

interface RiskGaugeProps {
  score: number;
  lastUpdated: string;
  statusExplanation: string;
  locationName: string;
}

export function RiskGauge({
  score,
  lastUpdated,
  statusExplanation,
  locationName,
}: RiskGaugeProps) {
  const riskCategory = getRiskCategory(score);
  const colorData = getRiskColor(riskCategory);

  // SVG Gauge calculations
  const radius = 80;
  const stroke = 12;
  const normalizedRadius = radius - stroke * 0.5;
  const circumference = normalizedRadius * 2 * Math.PI;
  // Use 240 degree arc gauge
  const arcLength = circumference * (240 / 360);
  const strokeDashoffset = arcLength - (score / 100) * arcLength;

  return (
    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-b from-[#0E273F] via-[#0B2135] to-[#071827] border border-[#1A3954] p-6 shadow-xl shadow-black/30">
      {/* Background ambient glow matching risk color */}
      <div
        className="absolute -top-12 -right-12 w-48 h-48 rounded-full blur-3xl opacity-20 pointer-events-none transition-all duration-500"
        style={{ backgroundColor: colorData.hex }}
      />

      {/* Top Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            Composite Climate Vulnerability
          </span>
          <h2 className="text-xl font-bold text-white mt-0.5 flex items-center gap-2">
            Overall Risk Score
          </h2>
        </div>
        <Badge riskLevel={riskCategory} size="lg" dot>
          {riskCategory} Tier
        </Badge>
      </div>

      {/* Gauge and Score Display */}
      <div className="flex flex-col sm:flex-row items-center justify-center gap-6 py-2">
        <div className="relative flex items-center justify-center shrink-0">
          <svg height={radius * 2} width={radius * 2} className="rotate-[150deg] transform">
            {/* Background Track Arc */}
            <circle
              stroke="#132E47"
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={`${arcLength} ${circumference}`}
              style={{ strokeDashoffset: 0 }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
            {/* Animated Colored Progress Arc */}
            <circle
              stroke={colorData.hex}
              fill="transparent"
              strokeWidth={stroke}
              strokeDasharray={`${arcLength} ${circumference}`}
              style={{
                strokeDashoffset,
                transition: 'stroke-dashoffset 0.8s ease-in-out, stroke 0.4s ease',
              }}
              strokeLinecap="round"
              r={normalizedRadius}
              cx={radius}
              cy={radius}
            />
          </svg>

          {/* Center Score Value */}
          <div className="absolute inset-0 flex flex-col items-center justify-center text-center">
            <span
              className="text-4xl font-extrabold tracking-tight font-mono transition-colors duration-300"
              style={{ color: colorData.hex }}
            >
              {score}
            </span>
            <span className="text-[11px] font-mono text-slate-400 uppercase tracking-widest -mt-1">
              / 100
            </span>
            <span className="text-[10px] text-slate-300 font-medium mt-1">
              {riskCategory}
            </span>
          </div>
        </div>

        {/* Narrative & Status Column */}
        <div className="flex-1 space-y-3 text-center sm:text-left">
          <div className="bg-[#071827]/70 rounded-xl p-3.5 border border-[#1A3954]/70">
            <div className="text-xs text-slate-400 font-medium flex items-center justify-center sm:justify-start gap-1.5 mb-1">
              <Shield className="w-3.5 h-3.5 text-cyan-400" />
              <span>Current Status for {locationName}</span>
            </div>
            <p className="text-sm text-slate-200 leading-relaxed font-normal">
              {statusExplanation}
            </p>
          </div>

          {/* Risk Range Scale Visualizer */}
          <div className="space-y-1.5">
            <div className="flex justify-between text-[10px] text-slate-400 font-mono">
              <span className="text-emerald-400">0–25 Low</span>
              <span className="text-amber-400">26–50 Mod</span>
              <span className="text-orange-400">51–75 High</span>
              <span className="text-rose-400">76–100 Crit</span>
            </div>
            <div className="h-1.5 w-full bg-[#102638] rounded-full overflow-hidden flex">
              <div className="h-full w-1/4 bg-emerald-500/40" />
              <div className="h-full w-1/4 bg-amber-500/40" />
              <div className="h-full w-1/4 bg-orange-500/40" />
              <div className="h-full w-1/4 bg-rose-500/40" />
            </div>
          </div>

          <div className="flex items-center justify-center sm:justify-start gap-2 text-[11px] text-slate-400">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>Telemetry synched: {formatTimestamp(lastUpdated)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}

