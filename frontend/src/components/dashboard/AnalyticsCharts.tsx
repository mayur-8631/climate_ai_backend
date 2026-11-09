'use client';

import React, { useState } from 'react';
import {
  Thermometer,
  CloudRain,
  Wind,
  Radar as RadarIcon,
  Filter,
  Calendar,
  Layers,
} from 'lucide-react';
import { TemperatureChart } from '@/components/charts/TemperatureChart';
import { RainfallChart } from '@/components/charts/RainfallChart';
import { AqiChart } from '@/components/charts/AqiChart';
import { RiskComparisonRadar } from '@/components/charts/RiskComparisonRadar';
import { HistoricalDataPoint, LocationData } from '@/types/climate';

interface AnalyticsChartsProps {
  location: LocationData;
  historicalData: HistoricalDataPoint[];
}

export function AnalyticsCharts({
  location,
  historicalData,
}: AnalyticsChartsProps) {
  const [activeTab, setActiveTab] = useState<'temp' | 'rain' | 'aqi' | 'radar'>('temp');
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d' | '1y'>('7d');

  return (
    <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-5 sm:p-6 shadow-xl shadow-black/20">
      {/* Top Header: Tabs and Range Filter */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-[#1A3954]/70">
        <div>
          <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            Climatological Telemetry & Predictive Analytics
          </div>
          <h3 className="text-lg font-bold text-white mt-0.5">
            Historical Trends & Multi-Hazard Comparative Profiling
          </h3>
        </div>

        {/* Time-Range Filters */}
        <div className="flex items-center gap-1 bg-[#071827] p-1 rounded-lg border border-[#1A3954] self-start md:self-auto">
          {(['24h', '7d', '30d', '1y'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-2.5 py-1 text-xs font-mono rounded-md transition-all cursor-pointer ${
                timeRange === range
                  ? 'bg-cyan-500/20 text-cyan-300 font-bold border border-cyan-500/30 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {range.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Selector Tabs */}
      <div className="flex items-center gap-2 my-4 overflow-x-auto pb-1 scrollbar-none">
        <button
          onClick={() => setActiveTab('temp')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'temp'
              ? 'bg-[#122F4C] text-amber-300 border border-amber-500/40 shadow-sm'
              : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]/60'
          }`}
        >
          <Thermometer className="w-4 h-4 text-amber-400" />
          <span>Temperature History</span>
        </button>

        <button
          onClick={() => setActiveTab('rain')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'rain'
              ? 'bg-[#122F4C] text-cyan-300 border border-cyan-500/40 shadow-sm'
              : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]/60'
          }`}
        >
          <CloudRain className="w-4 h-4 text-cyan-400" />
          <span>Precipitation (mm)</span>
        </button>

        <button
          onClick={() => setActiveTab('aqi')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'aqi'
              ? 'bg-[#122F4C] text-purple-300 border border-purple-500/40 shadow-sm'
              : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]/60'
          }`}
        >
          <Wind className="w-4 h-4 text-purple-400" />
          <span>AQI Aerosol Curve</span>
        </button>

        <button
          onClick={() => setActiveTab('radar')}
          className={`flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${
            activeTab === 'radar'
              ? 'bg-[#122F4C] text-emerald-300 border border-emerald-500/40 shadow-sm'
              : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]/60'
          }`}
        >
          <RadarIcon className="w-4 h-4 text-emerald-400" />
          <span>Multi-Hazard Radar</span>
        </button>
      </div>

      {/* Main Chart Render Box */}
      <div className="bg-[#071827]/70 rounded-xl p-4 border border-[#1A3954]/60">
        {activeTab === 'temp' && <TemperatureChart data={historicalData} />}
        {activeTab === 'rain' && <RainfallChart data={historicalData} />}
        {activeTab === 'aqi' && <AqiChart data={historicalData} />}
        {activeTab === 'radar' && (
          <RiskComparisonRadar
            risks={location.risks}
            locationName={location.name}
          />
        )}
      </div>

      {/* Chart Footer with Insight Footnote */}
      <div className="mt-3.5 flex flex-col sm:flex-row items-center justify-between text-xs text-slate-400 gap-2">
        <div className="flex items-center gap-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          <span>
            Displaying normalized 7-day observation window for {location.name},{' '}
            {location.state}
          </span>
        </div>
        <span className="text-[11px] font-mono text-slate-500">
          Source: Recharts Visual Engine • Resampled 6h intervals
        </span>
      </div>
    </div>
  );
}

