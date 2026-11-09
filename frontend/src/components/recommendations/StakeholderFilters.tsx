'use client';

import React from 'react';
import {
  Users,
  Building2,
  Tractor,
  DraftingCompass,
  Layers,
  Filter,
} from 'lucide-react';
import { StakeholderType, HazardType } from '@/types/climate';

interface StakeholderFiltersProps {
  selectedStakeholder: StakeholderType | 'all';
  onSelectStakeholder: (stakeholder: StakeholderType | 'all') => void;
  selectedHazard: HazardType | 'all';
  onSelectHazard: (hazard: HazardType | 'all') => void;
  selectedPriority: string;
  onSelectPriority: (priority: string) => void;
  counts: Record<string, number>;
}

export function StakeholderFilters({
  selectedStakeholder,
  onSelectStakeholder,
  selectedHazard,
  onSelectHazard,
  selectedPriority,
  onSelectPriority,
  counts,
}: StakeholderFiltersProps) {
  const stakeholderTabs: {
    id: StakeholderType | 'all';
    label: string;
    icon: React.ElementType;
  }[] = [
    { id: 'all', label: 'All Stakeholders', icon: Layers },
    { id: 'citizens', label: 'Citizens & Households', icon: Users },
    { id: 'government', label: 'Municipal & Government', icon: Building2 },
    { id: 'farmers', label: 'Farmers & Agriculture', icon: Tractor },
    { id: 'urban_planners', label: 'Urban Planners', icon: DraftingCompass },
  ];

  return (
    <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-5 shadow-xl shadow-black/20 space-y-4">
      {/* Stakeholder Category Tabs */}
      <div>
        <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold mb-2 flex items-center gap-1.5">
          <Filter className="w-3.5 h-3.5 text-cyan-400" />
          Stakeholder Persona Segmentation
        </div>
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          {stakeholderTabs.map((tab) => {
            const Icon = tab.icon;
            const isSelected = selectedStakeholder === tab.id;
            const count = counts[tab.id] ?? 0;

            return (
              <button
                key={tab.id}
                onClick={() => onSelectStakeholder(tab.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
                  isSelected
                    ? 'bg-gradient-to-r from-emerald-500/20 to-cyan-500/20 text-white border border-cyan-400/50 shadow-sm'
                    : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]/70'
                }`}
              >
                <Icon
                  className={`w-4 h-4 ${
                    isSelected ? 'text-cyan-400' : 'text-slate-400'
                  }`}
                />
                <span>{tab.label}</span>
                <span
                  className={`text-[10px] font-mono px-1.5 py-0.2 rounded-full ${
                    isSelected
                      ? 'bg-cyan-500/25 text-cyan-300 font-bold'
                      : 'bg-[#10273D] text-slate-500'
                  }`}
                >
                  {count}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Sub-Filters: Hazard Type and Priority */}
      <div className="pt-3 border-t border-[#1A3954]/60 flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Hazard filter pills */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-slate-400 text-[11px] font-mono mr-1">Hazard:</span>
          {(['all', 'heat', 'flood', 'air_quality', 'water_stress'] as const).map((h) => (
            <button
              key={h}
              onClick={() => onSelectHazard(h)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono transition-colors cursor-pointer ${
                selectedHazard === h
                  ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold'
                  : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]/60'
              }`}
            >
              {h === 'all'
                ? 'All Hazards'
                : h === 'air_quality'
                ? 'AQI'
                : h === 'water_stress'
                ? 'Water'
                : h.charAt(0).toUpperCase() + h.slice(1)}
            </button>
          ))}
        </div>

        {/* Priority filter */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-400 text-[11px] font-mono mr-1">Priority:</span>
          {['all', 'Critical', 'High', 'Medium'].map((p) => (
            <button
              key={p}
              onClick={() => onSelectPriority(p)}
              className={`px-2.5 py-1 rounded-md text-[11px] font-mono transition-colors cursor-pointer ${
                selectedPriority === p
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                  : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]/60'
              }`}
            >
              {p}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

