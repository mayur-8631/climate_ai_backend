import { RiskCategory, HazardType } from '@/types/climate';

export function getRiskCategory(score: number): RiskCategory {
  if (score <= 25) return 'Low';
  if (score <= 50) return 'Moderate';
  if (score <= 75) return 'High';
  return 'Critical';
}

export function getRiskColor(level: RiskCategory): {
  text: string;
  bg: string;
  border: string;
  fill: string;
  hex: string;
  glow: string;
} {
  switch (level) {
    case 'Low':
      return {
        text: 'text-emerald-400',
        bg: 'bg-emerald-500/10',
        border: 'border-emerald-500/30',
        fill: '#10B981',
        hex: '#10B981',
        glow: 'shadow-[0_0_20px_rgba(16,185,129,0.25)]',
      };
    case 'Moderate':
      return {
        text: 'text-amber-400',
        bg: 'bg-amber-500/10',
        border: 'border-amber-500/30',
        fill: '#F59E0B',
        hex: '#F59E0B',
        glow: 'shadow-[0_0_20px_rgba(245,158,11,0.25)]',
      };
    case 'High':
      return {
        text: 'text-orange-400',
        bg: 'bg-orange-500/10',
        border: 'border-orange-500/30',
        fill: '#F97316',
        hex: '#F97316',
        glow: 'shadow-[0_0_20px_rgba(249,115,22,0.25)]',
      };
    case 'Critical':
      return {
        text: 'text-rose-400',
        bg: 'bg-rose-500/10',
        border: 'border-rose-500/30',
        fill: '#EF4444',
        hex: '#EF4444',
        glow: 'shadow-[0_0_20px_rgba(239,68,68,0.25)]',
      };
  }
}

export function getHazardMeta(hazard: HazardType): {
  name: string;
  shortName: string;
  iconName: string;
  unit: string;
  color: string;
  description: string;
} {
  switch (hazard) {
    case 'heat':
      return {
        name: 'Extreme Heat Risk',
        shortName: 'Heat',
        iconName: 'Flame',
        unit: '°C Thermal Load',
        color: '#F97316',
        description: 'Vulnerability to wet-bulb heatwaves, urban heat island effects, and thermal stress.',
      };
    case 'flood':
      return {
        name: 'Precipitation & Flood Risk',
        shortName: 'Flood',
        iconName: 'CloudRain',
        unit: 'mm Runoff Exposure',
        color: '#06B6D4',
        description: 'Pluvial urban waterlogging, riverine overflow, and watershed saturation rates.',
      };
    case 'air_quality':
      return {
        name: 'Air Quality & Aerosol Risk',
        shortName: 'Air Quality',
        iconName: 'Wind',
        unit: 'PM2.5 / PM10 AQI',
        color: '#A855F7',
        description: 'Particulate density, chemical oxidants, thermal inversion trap potential.',
      };
    case 'water_stress':
      return {
        name: 'Aquifer & Water Stress Risk',
        shortName: 'Water Stress',
        iconName: 'Droplets',
        unit: 'Basin Depletion Index',
        color: '#3B82F6',
        description: 'Groundwater draft rates, reservoir storage deficit, and seasonal recharge capacity.',
      };
  }
}

export function formatNumber(val: number, decimals: number = 1): string {
  if (val === undefined || val === null || isNaN(val)) return '—';
  return val.toFixed(decimals);
}

export function formatTimestamp(isoStr: string): string {
  try {
    const d = new Date(isoStr);
    return d.toLocaleString('en-IN', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      timeZone: 'Asia/Kolkata',
    }) + ' IST';
  } catch {
    return isoStr;
  }
}

