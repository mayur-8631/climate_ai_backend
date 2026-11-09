'use client';

import React from 'react';
import {
  Sliders,
  RotateCcw,
  Sparkles,
  CloudRain,
  Thermometer,
  Droplets,
  Wind,
  Play,
  Zap,
} from 'lucide-react';
import { SimulationParams } from '@/types/climate';
import { Button } from '@/components/ui/Button';

interface SimulationSlidersProps {
  params: SimulationParams;
  onChange: (params: SimulationParams) => void;
  onRunSimulation: () => void;
  onReset: () => void;
  isLoading: boolean;
}

export function SimulationSliders({
  params,
  onChange,
  onRunSimulation,
  onReset,
  isLoading,
}: SimulationSlidersProps) {
  // Preset scenarios
  const applyPreset = (preset: 'heatwave' | 'monsoon' | 'smog' | 'drought') => {
    switch (preset) {
      case 'heatwave':
        onChange({
          rainfallPercentChange: -20,
          tempIncrease: 4.2,
          humidityDelta: -10,
          aqiDelta: 45,
        });
        break;
      case 'monsoon':
        onChange({
          rainfallPercentChange: 75,
          tempIncrease: -1.5,
          humidityDelta: 20,
          aqiDelta: -35,
        });
        break;
      case 'smog':
        onChange({
          rainfallPercentChange: -15,
          tempIncrease: 0.5,
          humidityDelta: -5,
          aqiDelta: 160,
        });
        break;
      case 'drought':
        onChange({
          rainfallPercentChange: -45,
          tempIncrease: 3.5,
          humidityDelta: -25,
          aqiDelta: 30,
        });
        break;
    }
  };

  return (
    <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-5 sm:p-6 shadow-xl shadow-black/20 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-[#1A3954]/70">
        <div>
          <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold flex items-center gap-1.5">
            <Sliders className="w-3.5 h-3.5 text-cyan-400" />
            Interactive Scenario Controls
          </div>
          <h3 className="text-lg font-bold text-white mt-0.5">
            What-If Climate Modeler
          </h3>
        </div>

        {/* Preset Selector */}
        <div className="flex items-center gap-1.5 flex-wrap">
          <span className="text-[11px] text-slate-400 mr-1 flex items-center gap-1 font-mono">
            <Zap className="w-3 h-3 text-amber-400" /> Presets:
          </span>
          <button
            onClick={() => applyPreset('heatwave')}
            className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#10273D] hover:bg-[#163854] text-orange-300 border border-orange-500/30 transition-colors cursor-pointer"
          >
            Extreme Heatwave
          </button>
          <button
            onClick={() => applyPreset('monsoon')}
            className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#10273D] hover:bg-[#163854] text-cyan-300 border border-cyan-500/30 transition-colors cursor-pointer"
          >
            Monsoon Surge
          </button>
          <button
            onClick={() => applyPreset('smog')}
            className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#10273D] hover:bg-[#163854] text-purple-300 border border-purple-500/30 transition-colors cursor-pointer"
          >
            Smog Inversion
          </button>
          <button
            onClick={() => applyPreset('drought')}
            className="px-2.5 py-1 rounded-md text-[11px] font-medium bg-[#10273D] hover:bg-[#163854] text-amber-300 border border-amber-500/30 transition-colors cursor-pointer"
          >
            Arid Drought
          </button>
        </div>
      </div>

      {/* Sliders Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Slider 1: Rainfall Percentage */}
        <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954]/70 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              <CloudRain className="w-4 h-4 text-cyan-400" />
              Precipitation Shift (%)
            </span>
            <span className="font-mono font-bold text-cyan-300 text-sm bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/30">
              {params.rainfallPercentChange > 0 ? '+' : ''}
              {params.rainfallPercentChange} %
            </span>
          </div>
          <input
            type="range"
            min={-50}
            max={100}
            step={5}
            value={params.rainfallPercentChange}
            onChange={(e) =>
              onChange({
                ...params,
                rainfallPercentChange: Number(e.target.value),
              })
            }
            className="w-full accent-cyan-400 cursor-pointer h-1.5 bg-[#102638] rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-50% (Drought)</span>
            <span>0% Baseline</span>
            <span>+100% (Cloudburst)</span>
          </div>
        </div>

        {/* Slider 2: Temperature Increase */}
        <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954]/70 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              <Thermometer className="w-4 h-4 text-orange-400" />
              Temperature Increase (°C)
            </span>
            <span className="font-mono font-bold text-orange-300 text-sm bg-orange-500/10 px-2 py-0.5 rounded border border-orange-500/30">
              +{params.tempIncrease.toFixed(1)} °C
            </span>
          </div>
          <input
            type="range"
            min={0}
            max={5.0}
            step={0.1}
            value={params.tempIncrease}
            onChange={(e) =>
              onChange({
                ...params,
                tempIncrease: Number(e.target.value),
              })
            }
            className="w-full accent-orange-400 cursor-pointer h-1.5 bg-[#102638] rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>+0.0 °C Baseline</span>
            <span>+2.5 °C Paris Bound</span>
            <span>+5.0 °C Extreme Heating</span>
          </div>
        </div>

        {/* Slider 3: Relative Humidity Delta */}
        <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954]/70 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              <Droplets className="w-4 h-4 text-blue-400" />
              Humidity Delta (%)
            </span>
            <span className="font-mono font-bold text-blue-300 text-sm bg-blue-500/10 px-2 py-0.5 rounded border border-blue-500/30">
              {params.humidityDelta > 0 ? '+' : ''}
              {params.humidityDelta} %
            </span>
          </div>
          <input
            type="range"
            min={-30}
            max={30}
            step={2}
            value={params.humidityDelta}
            onChange={(e) =>
              onChange({
                ...params,
                humidityDelta: Number(e.target.value),
              })
            }
            className="w-full accent-blue-400 cursor-pointer h-1.5 bg-[#102638] rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-30% Dry Air</span>
            <span>0% Baseline</span>
            <span>+30% Wet-Bulb Saturation</span>
          </div>
        </div>

        {/* Slider 4: AQI Shift */}
        <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954]/70 space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="font-semibold text-slate-200 flex items-center gap-2">
              <Wind className="w-4 h-4 text-purple-400" />
              AQI Particulate Delta
            </span>
            <span className="font-mono font-bold text-purple-300 text-sm bg-purple-500/10 px-2 py-0.5 rounded border border-purple-500/30">
              {params.aqiDelta > 0 ? '+' : ''}
              {params.aqiDelta} AQI
            </span>
          </div>
          <input
            type="range"
            min={-50}
            max={200}
            step={5}
            value={params.aqiDelta}
            onChange={(e) =>
              onChange({
                ...params,
                aqiDelta: Number(e.target.value),
              })
            }
            className="w-full accent-purple-400 cursor-pointer h-1.5 bg-[#102638] rounded-lg"
          />
          <div className="flex justify-between text-[10px] text-slate-500 font-mono">
            <span>-50 Clean Air</span>
            <span>0 Baseline</span>
            <span>+200 Severe Smog</span>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="pt-2 flex flex-col sm:flex-row items-center justify-between gap-3">
        <button
          onClick={onReset}
          className="text-xs text-slate-400 hover:text-slate-200 flex items-center gap-1.5 px-3 py-2 rounded-lg hover:bg-[#102638] transition-colors cursor-pointer"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>Reset to Baseline Parameters</span>
        </button>

        <Button
          onClick={onRunSimulation}
          isLoading={isLoading}
          variant="primary"
          size="lg"
          icon={<Play className="w-4 h-4 fill-current" />}
          className="w-full sm:w-auto"
        >
          Run Climate Scenario Simulation
        </Button>
      </div>
    </div>
  );
}

