'use client';

import React from 'react';
import dynamic from 'next/dynamic';
import { Loader2, MapPin } from 'lucide-react';
import { LocationData, HazardType } from '@/types/climate';

const DynamicClimateMap = dynamic(
  () => import('./ClimateMap').then((mod) => mod.ClimateMap),
  {
    ssr: false,
    loading: () => (
      <div className="w-full h-[580px] rounded-2xl bg-[#081B2B] border border-[#1A3954] flex flex-col items-center justify-center text-slate-400 gap-3 shadow-2xl">
        <Loader2 className="w-8 h-8 animate-spin text-cyan-400" />
        <div className="text-sm font-medium text-slate-300">
          Initializing Geospatial GIS Mapping Engine...
        </div>
        <div className="text-xs text-slate-500 font-mono">
          Loading OpenStreetMap & CartoDB Dark Basemap
        </div>
      </div>
    ),
  }
);

interface ClimateMapWrapperProps {
  locations: LocationData[];
  selectedLocation: LocationData;
  onSelectLocation: (loc: LocationData) => void;
  activeLayer?: HazardType | 'composite';
}

export function ClimateMapWrapper(props: ClimateMapWrapperProps) {
  return <DynamicClimateMap {...props} />;
}

