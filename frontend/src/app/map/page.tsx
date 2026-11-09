'use client';

import React, { useState } from 'react';
import {
  MapPin,
  Layers,
  Flame,
  CloudRain,
  Wind,
  Droplets,
  Activity,
  Compass,
  ArrowRight,
  Shield,
  Info,
} from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { ClimateMapWrapper } from '@/components/maps/ClimateMapWrapper';
import { useClimate } from '@/context/ClimateContext';
import { HazardType, LocationData } from '@/types/climate';
import { Badge } from '@/components/ui/Badge';
import { DisclaimerBanner } from '@/components/ui/DisclaimerBanner';
import { getRiskCategory, getRiskColor, formatTimestamp } from '@/utils/formatters';
import Link from 'next/link';

export default function MapPage() {
  const { selectedLocation, locationsList, selectLocationById } = useClimate();
  const [activeLayer, setActiveLayer] = useState<HazardType | 'composite'>('composite');

  const colorData = getRiskColor(selectedLocation.risk_level);

  return (
    <AppShell>
      <div className="space-y-6">
        <DisclaimerBanner type="demo-data" compact />

        {/* Page Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-[#1A3954]/70">
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-2xl sm:text-3xl font-black text-white tracking-tight">
                Geospatial Climate Risk Map
              </h1>
              <Badge variant="cyan" size="sm">
                Interactive GIS
              </Badge>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              Multi-scale geospatial vulnerability mapping across Indian metropolitan nodes. Pan, zoom, inspect localized telemetry footprints.
            </p>
          </div>

          {/* Quick Location Pills */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 scrollbar-none">
            <span className="text-[11px] text-slate-400 font-mono mr-1">Focus Node:</span>
            {locationsList.map((loc, idx) => {
              const locId = loc.id || (loc as any).ward_code || (loc as any).city?.toLowerCase() || `loc-${idx}`;
              const locName = loc.name || (loc as any).city || 'Node';
              const isSelected = locId === selectedLocation.id;
              return (
                <button
                  key={locId}
                  onClick={() => selectLocationById(locId)}
                  className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${isSelected
                      ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-bold'
                      : 'bg-[#0B2033] text-slate-400 hover:text-slate-200 border border-[#1A3954]'
                    }`}
                >
                  {locName}
                </button>
              );
            })}
          </div>
        </div>

        {/* Layer Selector Bar */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          <span className="text-xs font-mono text-slate-400 flex items-center gap-1.5 mr-2 shrink-0">
            <Layers className="w-3.5 h-3.5 text-cyan-400" />
            Active Overlay Layer:
          </span>

          <button
            onClick={() => setActiveLayer('composite')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${activeLayer === 'composite'
                ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 font-semibold'
                : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]'
              }`}
          >
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Composite Multi-Hazard</span>
          </button>

          <button
            onClick={() => setActiveLayer('heat')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${activeLayer === 'heat'
                ? 'bg-orange-500/20 text-orange-300 border border-orange-500/40 font-semibold'
                : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]'
              }`}
          >
            <Flame className="w-3.5 h-3.5 text-orange-400" />
            <span>Heat Island Layer</span>
          </button>

          <button
            onClick={() => setActiveLayer('flood')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${activeLayer === 'flood'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40 font-semibold'
                : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]'
              }`}
          >
            <CloudRain className="w-3.5 h-3.5 text-cyan-400" />
            <span>Precipitation / Inundation</span>
          </button>

          <button
            onClick={() => setActiveLayer('air_quality')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${activeLayer === 'air_quality'
                ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40 font-semibold'
                : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]'
              }`}
          >
            <Wind className="w-3.5 h-3.5 text-purple-400" />
            <span>AQI Aerosol Inversion</span>
          </button>

          <button
            onClick={() => setActiveLayer('water_stress')}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer whitespace-nowrap ${activeLayer === 'water_stress'
                ? 'bg-blue-500/20 text-blue-300 border border-blue-500/40 font-semibold'
                : 'bg-[#081B2B] text-slate-400 hover:text-slate-200 border border-[#1A3954]'
              }`}
          >
            <Droplets className="w-3.5 h-3.5 text-blue-400" />
            <span>Aquifer Depletion Layer</span>
          </button>
        </div>

        {/* Map Container and Selected Location Detail Sidecard */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 items-start">
          {/* Main Leaflet Map View */}
          <div className="lg:col-span-3">
            <ClimateMapWrapper
              locations={locationsList}
              selectedLocation={selectedLocation}
              onSelectLocation={(loc) => selectLocationById(loc.id)}
              activeLayer={activeLayer}
            />
          </div>

          {/* Selected Location Details Card */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] shadow-xl space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-[#1A3954]/70">
              <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold">
                Focused GIS Target
              </span>
              <Badge riskLevel={selectedLocation.risk_level} size="sm">
                {selectedLocation.risk_level}
              </Badge>
            </div>

            <div>
              <h3 className="text-xl font-bold text-white tracking-tight">
                {selectedLocation.name}
              </h3>
              <p className="text-xs text-slate-400">
                {selectedLocation.state}, {selectedLocation.country}
              </p>
              <div className="text-[11px] font-mono text-cyan-400 mt-1">
                Coordinates: {selectedLocation.lat.toFixed(4)}°N, {selectedLocation.lng.toFixed(4)}°E
              </div>
            </div>

            {/* Score Big Display */}
            <div className="p-3.5 rounded-xl bg-[#081B2B] border border-[#1A3954] text-center">
              <div className="text-[10px] font-mono uppercase text-slate-400 mb-0.5">
                Composite Climate Risk Score
              </div>
              <div
                className="text-3xl font-extrabold font-mono"
                style={{ color: colorData.hex }}
              >
                {selectedLocation.climate_risk_score} / 100
              </div>
              <p className="text-[11px] text-slate-300 mt-1.5 leading-snug">
                {selectedLocation.status_explanation}
              </p>
            </div>

            {/* Hazard Breakdown Bars */}
            <div className="space-y-2.5">
              <div className="text-[11px] font-mono uppercase text-slate-400 font-semibold">
                Hazard Vectors
              </div>

              {/* Heat */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300 flex items-center gap-1.5">
                    <Flame className="w-3.5 h-3.5 text-orange-400" /> Heat Stress
                  </span>
                  <span className="font-mono text-orange-300 font-bold">
                    {selectedLocation.risks.heat}
                  </span>
                </div>
                <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-orange-400 rounded-full"
                    style={{ width: `${selectedLocation.risks.heat}%` }}
                  />
                </div>
              </div>

              {/* Flood */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300 flex items-center gap-1.5">
                    <CloudRain className="w-3.5 h-3.5 text-cyan-400" /> Flood Risk
                  </span>
                  <span className="font-mono text-cyan-300 font-bold">
                    {selectedLocation.risks.flood}
                  </span>
                </div>
                <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-cyan-400 rounded-full"
                    style={{ width: `${selectedLocation.risks.flood}%` }}
                  />
                </div>
              </div>

              {/* AQI */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300 flex items-center gap-1.5">
                    <Wind className="w-3.5 h-3.5 text-purple-400" /> Air Quality
                  </span>
                  <span className="font-mono text-purple-300 font-bold">
                    {selectedLocation.risks.air_quality}
                  </span>
                </div>
                <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-400 rounded-full"
                    style={{ width: `${selectedLocation.risks.air_quality}%` }}
                  />
                </div>
              </div>

              {/* Water Stress */}
              <div className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-300 flex items-center gap-1.5">
                    <Droplets className="w-3.5 h-3.5 text-blue-400" /> Water Stress
                  </span>
                  <span className="font-mono text-blue-300 font-bold">
                    {selectedLocation.risks.water_stress}
                  </span>
                </div>
                <div className="h-1.5 w-full bg-[#10273D] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-blue-400 rounded-full"
                    style={{ width: `${selectedLocation.risks.water_stress}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Action Link */}
            <div className="pt-2">
              <Link
                href="/dashboard"
                className="w-full py-2 px-3 rounded-xl bg-cyan-500/15 hover:bg-cyan-500/25 border border-cyan-500/30 text-cyan-300 text-xs font-semibold flex items-center justify-center gap-1.5 transition-colors"
              >
                <span>Open Full Analytics for {selectedLocation.name}</span>
                <ArrowRight className="w-3.5 h-3.5" />
              </Link>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

