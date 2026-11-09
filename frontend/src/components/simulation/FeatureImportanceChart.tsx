'use client';

import React from 'react';
import { Brain, Cpu, ArrowUpRight, ArrowDownRight, Sparkles } from 'lucide-react';
import { FeatureImportance } from '@/types/climate';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';

interface FeatureImportanceChartProps {
  features: FeatureImportance[];
}

export function FeatureImportanceChart({ features }: FeatureImportanceChartProps) {
  return (
    <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-5 sm:p-6 shadow-xl shadow-black/20 space-y-5">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1A3954]/70">
        <div>
          <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-cyan-400" />
            Explainable AI (XAI) Attribution
          </div>
          <h3 className="text-lg font-bold text-white mt-0.5">
            Sensitivity & Feature Importance Ranking
          </h3>
        </div>

        <span className="text-[11px] font-mono text-cyan-300 bg-cyan-500/10 px-2.5 py-1 rounded-full border border-cyan-500/30">
          Ranked by Perturbation Elasticity
        </span>
      </div>

      <DisclaimerBanner type="feature-importance" compact />

      {/* Feature List */}
      <div className="space-y-4">
        {features.map((item, index) => {
          const pct = Math.round(item.importance * 100);
          const isUp = item.direction === 'positive';

          return (
            <div
              key={item.feature}
              className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954] hover:border-cyan-500/40 transition-colors space-y-2.5"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2.5">
                  <span className="w-6 h-6 rounded-md bg-[#10273D] border border-[#1A3954] flex items-center justify-center text-xs font-mono font-bold text-slate-300">
                    #{index + 1}
                  </span>
                  <div>
                    <h4 className="text-sm font-semibold text-white flex items-center gap-2">
                      {item.name}
                      {isUp ? (
                        <ArrowUpRight className="w-4 h-4 text-orange-400" />
                      ) : (
                        <ArrowDownRight className="w-4 h-4 text-emerald-400" />
                      )}
                    </h4>
                    <span className="text-[11px] font-mono text-slate-400">
                      Feature: {item.feature}
                    </span>
                  </div>
                </div>

                {/* Values Comparison */}
                <div className="flex items-center gap-3 text-xs font-mono">
                  <div className="text-slate-400">
                    Base: <span className="text-slate-200">{item.baselineValue}</span>
                  </div>
                  {item.simulatedValue && (
                    <div className="text-cyan-400">
                      Sim: <span className="font-bold text-cyan-300">{item.simulatedValue}</span>
                    </div>
                  )}
                  <span className="px-2 py-0.5 rounded bg-cyan-500/15 text-cyan-300 font-bold border border-cyan-500/30">
                    {pct}% Weight
                  </span>
                </div>
              </div>

              {/* Progress bar */}
              <div className="h-2 w-full bg-[#10273D] rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 rounded-full transition-all duration-500"
                  style={{ width: `${pct}%` }}
                />
              </div>

              <p className="text-xs text-slate-300 leading-relaxed">
                {item.description}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

