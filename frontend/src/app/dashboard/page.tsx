'use client';

import React, { useEffect, useState } from 'react';
import {
  Shield,
  Activity,
  Flame,
  CloudRain,
  Wind,
  Droplets,
  Layers,
  Sparkles,
  MapPin,
  RefreshCw,
  Sliders,
  FileCheck2,
  AlertTriangle,
} from 'lucide-react';
import { useClimate } from '@/context/ClimateContext';
import { AppShell } from '@/components/layout/AppShell';
import { RiskGauge } from '@/components/dashboard/RiskGauge';
import { RiskCard } from '@/components/dashboard/RiskCard';
import { MetricsGrid } from '@/components/dashboard/MetricsGrid';
import { AnalyticsCharts } from '@/components/dashboard/AnalyticsCharts';
import { InsightsPanel } from '@/components/dashboard/InsightsPanel';
import { ExplainableSection } from '@/components/dashboard/ExplainableSection';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { Badge } from '@/components/ui/Badge';
import { climateApi } from '@/services/api';
import { HistoricalDataPoint, ClimateInsight } from '@/types/climate';
import { MOCK_CLIMATE_INSIGHTS } from '@/services/mockData';
import Link from 'next/link';

export default function DashboardPage() {
  const { selectedLocation, isLoading, isMockMode } = useClimate();
  const [historicalData, setHistoricalData] = useState<HistoricalDataPoint[]>([]);
  const [insights, setInsights] = useState<ClimateInsight[]>(MOCK_CLIMATE_INSIGHTS);

  // Fetch historical trend points whenever selected location changes
  useEffect(() => {
    let active = true;
    async function loadTrends() {
      try {
        const res = await climateApi.getHistoricalTrends(selectedLocation.id, '7d');
        if (active) {
          setHistoricalData(res.data);
        }
      } catch (err) {
        console.warn('Failed loading trends:', err);
      }
    }
    loadTrends();
    return () => {
      active = false;
    };
  }, [selectedLocation.id]);

  return (
    <AppShell>
      <div className="space-y-6">
        {/* Transparent Honesty Disclaimer Banner */}
        <DisclaimerBanner type="demo-data" />

        {/* Dashboard Title & Quick Status Bar */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-[#1A3954]/70">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Climate Intelligence Dashboard
              </h1>
              <Badge riskLevel={selectedLocation.risk_level} size="sm">
                {selectedLocation.risk_level} Risk
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-cyan-400" />
              Monitoring active node:{' '}
              <span className="text-slate-200 font-medium">
                {selectedLocation.name}, {selectedLocation.state}, {selectedLocation.country}
              </span>
              <span className="text-slate-500">•</span>
              <span className="font-mono text-cyan-400">
                Lat {selectedLocation.lat}° N, Lng {selectedLocation.lng}° E
              </span>
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <Link
              href="/simulation"
              className="px-3 py-1.5 rounded-lg bg-[#10273D] hover:bg-[#163854] text-cyan-300 border border-cyan-500/30 text-xs font-medium flex items-center gap-1.5 transition-colors"
            >
              <Sliders className="w-3.5 h-3.5 text-cyan-400" />
              <span>Simulate Scenario</span>
            </Link>
            <Link
              href="/map"
              className="px-3 py-1.5 rounded-lg bg-[#10273D] hover:bg-[#163854] text-slate-200 border border-[#1A3954] text-xs font-medium flex items-center gap-1.5 transition-colors"
            >
              <MapPin className="w-3.5 h-3.5 text-emerald-400" />
              <span>View On Map</span>
            </Link>
          </div>
        </div>

        {/* Section C: Overall Climate Risk Score Gauge */}
        <RiskGauge
          score={selectedLocation.climate_risk_score}
          lastUpdated={selectedLocation.last_updated}
          statusExplanation={selectedLocation.status_explanation}
          locationName={selectedLocation.name}
        />

        {/* Section E: Environmental Metrics Grid */}
        <div>
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2.5 font-semibold flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            Ground Environmental Telemetry
          </div>
          <MetricsGrid metrics={selectedLocation.metrics} />
        </div>

        {/* Section D: Four Climate Risk Cards */}
        <div>
          <div className="text-xs font-mono uppercase tracking-wider text-slate-400 mb-2.5 font-semibold flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            Hazard Vector Vulnerability Breakdown
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <RiskCard
              hazard="heat"
              detail={selectedLocation.risk_details.heat}
            />
            <RiskCard
              hazard="flood"
              detail={selectedLocation.risk_details.flood}
            />
            <RiskCard
              hazard="air_quality"
              detail={selectedLocation.risk_details.air_quality}
            />
            <RiskCard
              hazard="water_stress"
              detail={selectedLocation.risk_details.water_stress}
            />
          </div>
        </div>

        {/* Section F: Climate Analytics (Recharts Trends & Radar) */}
        <AnalyticsCharts
          location={selectedLocation}
          historicalData={historicalData}
        />

        {/* Two-Column Grid: Section G Insights + Section 8 Explainable AI */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <InsightsPanel
            location={selectedLocation}
            insights={insights}
          />
          <ExplainableSection
            location={selectedLocation}
          />
        </div>
      </div>
    </AppShell>
  );
}

