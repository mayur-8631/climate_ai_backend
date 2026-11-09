'use client';

import React from 'react';
import {
  Thermometer,
  Droplets,
  CloudRain,
  Wind,
  Gauge,
  Sun,
  Compass,
  Layers,
} from 'lucide-react';
import { EnvironmentalMetrics } from '@/types/climate';
import { formatNumber } from '@/utils/formatters';

interface MetricsGridProps {
  metrics: EnvironmentalMetrics;
}

export function MetricsGrid({ metrics }: MetricsGridProps) {
  const metricItems = [
    {
      label: 'Temperature',
      value: `${formatNumber(metrics.temperature, 1)} °C`,
      subtext: 'Surface Ambient',
      icon: Thermometer,
      color: 'text-amber-400',
      bgColor: 'bg-amber-500/10',
      borderColor: 'border-amber-500/20',
    },
    {
      label: 'Relative Humidity',
      value: `${metrics.humidity} %`,
      subtext: 'Vapor Saturation',
      icon: Droplets,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-500/10',
      borderColor: 'border-cyan-500/20',
    },
    {
      label: '24h Precipitation',
      value: `${metrics.rainfall} mm`,
      subtext: 'Cumulative Gauge',
      icon: CloudRain,
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/10',
      borderColor: 'border-blue-500/20',
    },
    {
      label: 'Air Quality (AQI)',
      value: `${metrics.aqi}`,
      subtext: metrics.aqi > 150 ? 'Unhealthy' : metrics.aqi > 100 ? 'Moderate Alert' : 'Satisfactory',
      icon: Gauge,
      color: metrics.aqi > 200 ? 'text-rose-400' : metrics.aqi > 100 ? 'text-orange-400' : 'text-emerald-400',
      bgColor: 'bg-purple-500/10',
      borderColor: 'border-purple-500/20',
    },
    {
      label: 'Wind Speed',
      value: `${formatNumber(metrics.wind_speed, 1)} km/h`,
      subtext: metrics.wind_direction ? `Direction: ${metrics.wind_direction}` : 'Surface Breeze',
      icon: Wind,
      color: 'text-teal-400',
      bgColor: 'bg-teal-500/10',
      borderColor: 'border-teal-500/20',
    },
    {
      label: 'Soil Moisture',
      value: `${metrics.soil_moisture ?? 42} %`,
      subtext: 'Subsurface 15cm',
      icon: Layers,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/10',
      borderColor: 'border-emerald-500/20',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3.5">
      {metricItems.map((item, idx) => {
        const Icon = item.icon;
        return (
          <div
            key={idx}
            className="p-3.5 rounded-xl bg-[#0B2033] border border-[#1A3954] hover:border-cyan-500/30 transition-all duration-150 flex flex-col justify-between"
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] text-slate-400 font-medium truncate">
                {item.label}
              </span>
              <div
                className={`w-6 h-6 rounded-md flex items-center justify-center shrink-0 border ${item.bgColor} ${item.borderColor} ${item.color}`}
              >
                <Icon className="w-3.5 h-3.5" />
              </div>
            </div>

            <div>
              <div className="text-lg sm:text-xl font-bold font-mono tracking-tight text-white">
                {item.value}
              </div>
              <div className="text-[10px] text-slate-400 mt-0.5 truncate">
                {item.subtext}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

