'use client';

import React, { useState } from 'react';
import { Info, ShieldAlert, Sparkles, X, ChevronRight } from 'lucide-react';
import { useClimate } from '@/context/ClimateContext';

interface DisclaimerBannerProps {
  type?: 'demo-data' | 'simulation-demo' | 'recommendations' | 'feature-importance';
  className?: string;
  compact?: boolean;
}

export function DisclaimerBanner({
  type = 'demo-data',
  className = '',
  compact = false,
}: DisclaimerBannerProps) {
  const [dismissed, setDismissed] = useState(false);
  const { isMockMode } = useClimate();

  if (dismissed) return null;

  let title = 'Illustrative Climate Intelligence Baseline';
  let message =
    'Displayed meteorological metrics and composite risk values represent illustrative benchmark samples for UI/UX demonstration and evaluation. They are not real-time sensor measurements or certified ML forecasts.';
  let badgeText = 'DEMO TELEMETRY';

  if (type === 'simulation-demo') {
    title = 'Scenario Simulation — Heuristic Demo Calculation';
    message =
      'Calculations rendered in this What-If playground are frontend demo estimates simulating coupled hazard dynamics. A modular architecture is prepared for immediate swap with Lokesh Joshi’s validated ML inference API.';
    badgeText = 'HEURISTIC ESTIMATE';
  } else if (type === 'recommendations') {
    title = 'Illustrative Stakeholder Recommendations';
    message =
      'Actionable recommendations are curated demonstrative protocols mapped to current hazard tiers, prepared to ingest dynamic output from Team PrithviNex’s recommendation engine.';
    badgeText = 'BENCHMARK PROTOCOLS';
  } else if (type === 'feature-importance') {
    title = 'Explainable AI Interface Architecture';
    message =
      'Feature weightings and sensitivity vectors are illustrative structural mockups designed to ingest SHAP/LIME explanation tensors from the Python/FastAPI backend once trained.';
    badgeText = 'SHAP INTEGRATION READY';
  }

  if (compact) {
    return (
      <div
        className={`flex items-center justify-between gap-3 px-3 py-1.5 rounded-lg bg-[#0E263D]/80 border border-cyan-500/20 text-xs text-slate-300 ${className}`}
      >
        <div className="flex items-center gap-2 overflow-hidden">
          <Info className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
          <span className="truncate">
            <strong className="text-cyan-300 font-medium">Notice:</strong> {message}
          </span>
        </div>
        <span className="text-[10px] font-mono uppercase bg-cyan-500/10 text-cyan-300 px-1.5 py-0.5 rounded border border-cyan-500/30 shrink-0">
          {badgeText}
        </span>
      </div>
    );
  }

  return (
    <div
      className={`relative overflow-hidden rounded-xl bg-gradient-to-r from-[#0C243B] via-[#0E2B46] to-[#0A1F33] border border-cyan-500/30 p-3.5 sm:p-4 text-xs shadow-lg shadow-black/20 ${className}`}
    >
      <div className="flex items-start gap-3">
        <div className="w-7 h-7 rounded-lg bg-cyan-500/15 border border-cyan-500/30 text-cyan-400 flex items-center justify-center shrink-0 mt-0.5">
          <Info className="w-4 h-4" />
        </div>

        <div className="flex-1 pr-6">
          <div className="flex items-center gap-2 mb-1 flex-wrap">
            <span className="font-semibold text-slate-100">{title}</span>
            <span className="text-[10px] font-mono tracking-wider uppercase px-2 py-0.5 rounded-full bg-cyan-500/15 text-cyan-300 border border-cyan-500/30">
              {badgeText}
            </span>
            {isMockMode && (
              <span className="text-[10px] text-amber-400/90 font-mono">
                • Mode: Mock Service Active
              </span>
            )}
          </div>
          <p className="text-slate-300/90 leading-relaxed">{message}</p>
        </div>

        <button
          onClick={() => setDismissed(true)}
          className="text-slate-400 hover:text-slate-200 transition-colors p-1"
          aria-label="Dismiss disclaimer"
        >
          <X className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
}

