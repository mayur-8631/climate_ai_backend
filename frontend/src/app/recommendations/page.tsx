'use client';

import React, { useState, useEffect } from 'react';
import {
  FileCheck2,
  Users,
  Building2,
  Tractor,
  DraftingCompass,
  Filter,
  Sparkles,
  Search,
  CheckCircle2,
  Download,
  Info,
} from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { StakeholderFilters } from '@/components/recommendations/StakeholderFilters';
import { RecommendationCard } from '@/components/recommendations/RecommendationCard';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { Badge } from '@/components/ui/Badge';
import { useClimate } from '@/context/ClimateContext';
import { climateApi } from '@/services/api';
import {
  StakeholderType,
  HazardType,
  RecommendationItem,
} from '@/types/climate';
import { MOCK_RECOMMENDATIONS } from '@/services/mockData';

export default function RecommendationsPage() {
  const { selectedLocation } = useClimate();
  const [selectedStakeholder, setSelectedStakeholder] = useState<StakeholderType | 'all'>('all');
  const [selectedHazard, setSelectedHazard] = useState<HazardType | 'all'>('all');
  const [selectedPriority, setSelectedPriority] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>(MOCK_RECOMMENDATIONS);

  useEffect(() => {
    async function loadRecs() {
      try {
        const res = await climateApi.getRecommendations(
          selectedStakeholder === 'all' ? undefined : selectedStakeholder
        );
        setRecommendations(res.data);
      } catch (err) {
        console.warn('Failed loading recommendations:', err);
      }
    }
    loadRecs();
  }, [selectedStakeholder]);

  // Compute category counts
  const counts: Record<string, number> = {
    all: recommendations.length,
    citizens: recommendations.filter((r) => r.stakeholder === 'citizens').length,
    government: recommendations.filter((r) => r.stakeholder === 'government').length,
    farmers: recommendations.filter((r) => r.stakeholder === 'farmers').length,
    urban_planners: recommendations.filter((r) => r.stakeholder === 'urban_planners').length,
  };

  // Filter recommendations
  const filteredRecs = recommendations.filter((item) => {
    if (selectedStakeholder !== 'all' && item.stakeholder !== selectedStakeholder) {
      return false;
    }
    if (selectedHazard !== 'all' && item.hazardCategory !== selectedHazard) {
      return false;
    }
    if (selectedPriority !== 'all' && item.priority !== selectedPriority) {
      return false;
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      const matchTitle = item.title.toLowerCase().includes(q);
      const matchSummary = item.summary.toLowerCase().includes(q);
      const matchTags = item.tags.some((t) => t.toLowerCase().includes(q));
      if (!matchTitle && !matchSummary && !matchTags) return false;
    }
    return true;
  });

  return (
    <AppShell>
      <div className="space-y-6">
        <DisclaimerBanner type="recommendations" />

        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1A3954]/70">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Stakeholder Action Protocols
              </h1>
              <Badge variant="emerald" size="sm">
                Target: {selectedLocation.name}
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Role-specific climate resilience playbooks mapped dynamically to localized hazard scores.
            </p>
          </div>

          {/* Quick search input */}
          <div className="relative w-full sm:w-64">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Filter actions or keywords..."
              className="w-full pl-8 pr-3 py-1.5 bg-[#081B2B] border border-[#1A3954] focus:border-cyan-400 text-xs text-slate-200 placeholder-slate-500 rounded-lg outline-none transition-all"
            />
          </div>
        </div>

        {/* Stakeholder Filters & Segmentation Bar */}
        <StakeholderFilters
          selectedStakeholder={selectedStakeholder}
          onSelectStakeholder={setSelectedStakeholder}
          selectedHazard={selectedHazard}
          onSelectHazard={setSelectedHazard}
          selectedPriority={selectedPriority}
          onSelectPriority={setSelectedPriority}
          counts={counts}
        />

        {/* Recommendations Cards Grid */}
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
            <span>
              Showing {filteredRecs.length} actionable protocols for {selectedLocation.name}
            </span>
            <span className="text-cyan-400">
              Interactive Checklist Mode
            </span>
          </div>

          {filteredRecs.length > 0 ? (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
              {filteredRecs.map((item) => (
                <RecommendationCard key={item.id} item={item} />
              ))}
            </div>
          ) : (
            <div className="p-12 text-center rounded-2xl bg-[#081B2B] border border-[#1A3954] text-slate-400 space-y-2">
              <FileCheck2 className="w-8 h-8 text-slate-500 mx-auto" />
              <div className="text-sm font-semibold text-slate-300">
                No matching recommendations found
              </div>
              <p className="text-xs text-slate-500">
                Try resetting hazard or priority filters to view additional stakeholder guidance.
              </p>
            </div>
          )}
        </div>
      </div>
    </AppShell>
  );
}

