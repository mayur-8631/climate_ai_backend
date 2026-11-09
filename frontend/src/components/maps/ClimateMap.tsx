'use client';

import React, { useState, useEffect } from 'react';
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import { LocationData, RiskCategory, HazardType } from '@/types/climate';
import { getRiskColor, getRiskCategory } from '@/utils/formatters';
import { Badge } from '@/components/ui/Badge';
import {
  Flame,
  CloudRain,
  Wind,
  Droplets,
  Layers,
  MapPin,
  ExternalLink,
  ChevronRight,
} from 'lucide-react';

interface ClimateMapProps {
  locations: LocationData[];
  selectedLocation: LocationData;
  onSelectLocation: (loc: LocationData) => void;
  activeLayer?: HazardType | 'composite';
}

// Controller to fly map to selected location
function MapController({ center }: { center: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(center, 9, { duration: 1.2 });
  }, [center, map]);
  return null;
}

// Custom Leaflet Pin Icons generator
function createCustomPin(color: string, score: number, isSelected: boolean) {
  return L.divIcon({
    className: 'custom-map-pin',
    html: `
      <div style="
        position: relative;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background-color: #071827;
        border: 2px solid ${color};
        box-shadow: 0 0 15px ${color}80;
        cursor: pointer;
        transform: ${isSelected ? 'scale(1.2)' : 'scale(1)'};
        transition: transform 0.2s ease;
      ">
        <span style="
          font-family: monospace;
          font-weight: 800;
          font-size: 11px;
          color: ${color};
        ">${score}</span>
        ${
          isSelected
            ? `<div style="
                position: absolute;
                inset: -6px;
                border-radius: 50%;
                border: 2px dashed ${color};
                animation: spin 6s linear infinite;
              "></div>`
            : ''
        }
      </div>
    `,
    iconSize: [36, 36],
    iconAnchor: [18, 18],
    popupAnchor: [0, -20],
  });
}

export function ClimateMap({
  locations,
  selectedLocation,
  onSelectLocation,
  activeLayer = 'composite',
}: ClimateMapProps) {
  const centerPosition: [number, number] = [
    selectedLocation.lat,
    selectedLocation.lng,
  ];

  return (
    <div className="relative w-full h-[580px] rounded-2xl overflow-hidden border border-[#1A3954] shadow-2xl shadow-black/40">
      <MapContainer
        center={centerPosition}
        zoom={6}
        scrollWheelZoom={true}
        className="w-full h-full z-0 dark-map-tiles"
      >
        <MapController center={centerPosition} />

        {/* Clean OpenStreetMap Tiles with Dark Theme styling (Zero watermark, No API Key required) */}
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url={
            process.env.NEXT_PUBLIC_CARTO_API_KEY
              ? `https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png?api_key=${process.env.NEXT_PUBLIC_CARTO_API_KEY}`
              : 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
          }
          maxZoom={19}
        />

        {/* Location Markers and Risk Heat Circles */}
        {locations.map((loc, idx) => {
          const locKey = loc.id || `loc-pin-${idx}`;
          const isSelected = loc.id === selectedLocation.id;
          let displayScore = loc.climate_risk_score ?? 50;
          if (activeLayer !== 'composite' && loc.risks && loc.risks[activeLayer] !== undefined) {
            displayScore = loc.risks[activeLayer];
          }

          const category = getRiskCategory(displayScore);
          const colorData = getRiskColor(category);
          const icon = createCustomPin(colorData.hex, displayScore, isSelected);
          const lat = loc.lat ?? 18.5204;
          const lng = loc.lng ?? 73.8567;

          return (
            <React.Fragment key={locKey}>
              {/* Radius Circle showing localized hazard footprint */}
              <Circle
                center={[lat, lng]}
                radius={isSelected ? 45000 : 25000}
                pathOptions={{
                  color: colorData.hex,
                  fillColor: colorData.hex,
                  fillOpacity: isSelected ? 0.22 : 0.12,
                  weight: isSelected ? 2 : 1,
                  dashArray: isSelected ? '4, 4' : undefined,
                }}
              />

              {/* Marker */}
              <Marker
                position={[lat, lng]}
                icon={icon}
                eventHandlers={{
                  click: () => onSelectLocation(loc),
                }}
              >
                <Popup>
                  <div className="p-1 min-w-[220px]">
                    <div className="flex items-center justify-between gap-2 border-b border-[#1A3954] pb-2 mb-2">
                      <div>
                        <h4 className="font-bold text-sm text-white">
                          {loc.name}
                        </h4>
                        <span className="text-[11px] text-slate-400">
                          {loc.state}, {loc.country}
                        </span>
                      </div>
                      <Badge riskLevel={category} size="sm">
                        {category}
                      </Badge>
                    </div>

                    <div className="space-y-1.5 text-xs text-slate-300">
                      <div className="flex justify-between items-center">
                        <span className="text-slate-400">Composite Score:</span>
                        <span
                          className="font-mono font-bold"
                          style={{ color: colorData.hex }}
                        >
                          {loc.climate_risk_score} / 100
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="text-slate-400">Temperature:</span>
                        <span className="font-mono text-white">
                          {loc.metrics.temperature} °C
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="text-slate-400">24h Rainfall:</span>
                        <span className="font-mono text-cyan-400">
                          {loc.metrics.rainfall} mm
                        </span>
                      </div>
                      <div className="flex justify-between items-center text-[11px]">
                        <span className="text-slate-400">AQI:</span>
                        <span className="font-mono text-purple-400">
                          {loc.metrics.aqi}
                        </span>
                      </div>
                    </div>

                    <button
                      onClick={() => onSelectLocation(loc)}
                      className="mt-3 w-full py-1.5 px-3 rounded-lg bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/30 text-xs font-semibold flex items-center justify-center gap-1 transition-colors cursor-pointer"
                    >
                      <span>Focus Telemetry</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </Popup>
              </Marker>
            </React.Fragment>
          );
        })}
      </MapContainer>

      {/* Floating Map Legend Overlay */}
      <div className="absolute bottom-5 left-5 z-[1000] bg-[#071827]/90 backdrop-blur-md p-3.5 rounded-xl border border-[#1A3954] shadow-xl text-xs space-y-2 pointer-events-auto max-w-xs">
        <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400 font-semibold flex items-center gap-1.5">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          Risk Intensity Legend
        </div>
        <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400" />
            <span className="text-slate-300">0–25 Low</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
            <span className="text-slate-300">26–50 Moderate</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-orange-400" />
            <span className="text-slate-300">51–75 High</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-400" />
            <span className="text-slate-300">76–100 Critical</span>
          </div>
        </div>
      </div>
    </div>
  );
}
