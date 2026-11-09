'use client';

import React, { useState } from 'react';
import {
  Flame,
  CloudRain,
  Wind,
  Droplets,
  Clock,
  Sparkles,
  CheckCircle2,
  Circle,
  AlertTriangle,
  Zap,
} from 'lucide-react';
import { RecommendationItem, HazardType } from '@/types/climate';
import { getHazardMeta } from '@/utils/formatters';
import { Badge } from '@/components/ui/Badge';

interface RecommendationCardProps {
  item: RecommendationItem;
}

export function RecommendationCard({ item }: RecommendationCardProps) {
  // Track completed checklist items locally for interactive demo fidelity
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});

  const toggleStep = (idx: number) => {
    setCompletedSteps((prev) => ({
      ...prev,
      [idx]: !prev[idx],
    }));
  };

  // Hazard metadata
  const isMulti = item.hazardCategory === 'multi-hazard';
  const meta = !isMulti ? getHazardMeta(item.hazardCategory as HazardType) : null;

  const renderHazardIcon = () => {
    switch (item.hazardCategory) {
      case 'heat':
        return <Flame className="w-4 h-4 text-orange-400" />;
      case 'flood':
        return <CloudRain className="w-4 h-4 text-cyan-400" />;
      case 'air_quality':
        return <Wind className="w-4 h-4 text-purple-400" />;
      case 'water_stress':
        return <Droplets className="w-4 h-4 text-blue-400" />;
      default:
        return <Zap className="w-4 h-4 text-amber-400" />;
    }
  };

  let priorityBadge = <Badge variant="slate" size="sm">Medium</Badge>;
  if (item.priority === 'Critical') {
    priorityBadge = (
      <Badge variant="rose" size="sm" dot>
        Critical Priority
      </Badge>
    );
  } else if (item.priority === 'High') {
    priorityBadge = (
      <Badge variant="orange" size="sm">
        High Priority
      </Badge>
    );
  }

  const completedCount = Object.values(completedSteps).filter(Boolean).length;
  const allCompleted =
    completedCount === item.actionableSteps.length && item.actionableSteps.length > 0;

  return (
    <div
      className={`rounded-2xl p-5 sm:p-6 transition-all duration-200 border flex flex-col justify-between ${
        allCompleted
          ? 'bg-[#091D2F] border-emerald-500/40 opacity-90'
          : 'bg-gradient-to-b from-[#0C2237] to-[#071928] border-[#1A3954] hover:border-cyan-500/40 shadow-xl shadow-black/20'
      }`}
    >
      <div>
        {/* Top Meta Bar */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#081B2B] border border-[#1A3954] text-xs font-medium text-slate-200">
              {renderHazardIcon()}
              <span>{meta ? meta.shortName : 'Multi-Hazard'}</span>
            </div>
            {priorityBadge}
            {item.isIllustrativeDemo && (
              <span className="text-[10px] font-mono uppercase bg-[#10273D] text-slate-400 px-2 py-0.5 rounded border border-[#1A3954]">
                Demo Benchmark
              </span>
            )}
          </div>

          <div className="flex items-center gap-1.5 text-xs text-slate-400 font-mono shrink-0">
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>{item.timeframe}</span>
          </div>
        </div>

        {/* Title & Summary */}
        <h3 className="text-base font-bold text-white tracking-tight mb-1.5">
          {item.title}
        </h3>
        <p className="text-xs text-slate-300 leading-relaxed mb-4">
          {item.summary}
        </p>

        {/* Actionable Checklist */}
        <div className="space-y-2 mb-4 bg-[#081B2B] p-3.5 rounded-xl border border-[#1A3954]/70">
          <div className="flex items-center justify-between text-[11px] font-mono text-slate-400 mb-1">
            <span className="uppercase tracking-wider font-semibold text-slate-300">
              Action Execution Checklist
            </span>
            <span className="text-cyan-400">
              {completedCount} of {item.actionableSteps.length} Checked
            </span>
          </div>

          <div className="space-y-2">
            {item.actionableSteps.map((step, idx) => {
              const isChecked = Boolean(completedSteps[idx]);
              return (
                <div
                  key={idx}
                  onClick={() => toggleStep(idx)}
                  className={`flex items-start gap-2.5 p-2 rounded-lg cursor-pointer transition-colors text-xs leading-relaxed select-none ${
                    isChecked
                      ? 'bg-emerald-500/10 text-slate-300 line-through'
                      : 'hover:bg-[#10273D] text-slate-200'
                  }`}
                >
                  <div className="mt-0.5 shrink-0">
                    {isChecked ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    ) : (
                      <Circle className="w-4 h-4 text-slate-500 hover:text-cyan-400" />
                    )}
                  </div>
                  <span>{step}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Footer Assessment & Tags */}
      <div className="pt-3 border-t border-[#1A3954]/60 space-y-2.5">
        <div className="flex items-center gap-2 text-xs text-emerald-300/90 bg-emerald-500/10 px-3 py-1.5 rounded-lg border border-emerald-500/20">
          <Sparkles className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span className="truncate">
            <strong>Impact:</strong> {item.estimatedImpact}
          </span>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-2 text-[10px] text-slate-400">
          <div className="flex flex-wrap gap-1.5">
            {item.tags.map((t, i) => (
              <span
                key={i}
                className="px-2 py-0.5 rounded bg-[#071827] text-slate-400 border border-[#1A3954]"
              >
                #{t}
              </span>
            ))}
          </div>
          <span className="font-mono text-cyan-400 capitalize">
            Persona: {item.stakeholder.replace('_', ' ')}
          </span>
        </div>
      </div>
    </div>
  );
}
