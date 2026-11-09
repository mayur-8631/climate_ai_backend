import React, { ReactNode } from 'react';
import { RiskCategory } from '@/types/climate';

interface BadgeProps {
  children: ReactNode;
  variant?: 'emerald' | 'cyan' | 'amber' | 'orange' | 'rose' | 'slate' | 'outline';
  riskLevel?: RiskCategory;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  dot?: boolean;
}

export function Badge({
  children,
  variant,
  riskLevel,
  size = 'md',
  className = '',
  dot = false,
}: BadgeProps) {
  let colorStyles = 'bg-slate-800 text-slate-300 border-slate-700';

  if (riskLevel) {
    switch (riskLevel) {
      case 'Low':
        colorStyles = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
        break;
      case 'Moderate':
        colorStyles = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
        break;
      case 'High':
        colorStyles = 'bg-orange-500/15 text-orange-400 border-orange-500/30';
        break;
      case 'Critical':
        colorStyles = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
        break;
    }
  } else if (variant) {
    switch (variant) {
      case 'emerald':
        colorStyles = 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
        break;
      case 'cyan':
        colorStyles = 'bg-cyan-500/15 text-cyan-400 border-cyan-500/30';
        break;
      case 'amber':
        colorStyles = 'bg-amber-500/15 text-amber-400 border-amber-500/30';
        break;
      case 'orange':
        colorStyles = 'bg-orange-500/15 text-orange-400 border-orange-500/30';
        break;
      case 'rose':
        colorStyles = 'bg-rose-500/15 text-rose-400 border-rose-500/30';
        break;
      case 'slate':
        colorStyles = 'bg-slate-800/80 text-slate-300 border-slate-700';
        break;
      case 'outline':
        colorStyles = 'bg-transparent text-slate-300 border-[#1A3954]';
        break;
    }
  }

  let sizeStyles = 'text-xs px-2.5 py-0.5 rounded-full';
  if (size === 'sm') sizeStyles = 'text-[10px] px-2 py-0.5 rounded-md';
  if (size === 'lg') sizeStyles = 'text-sm px-3.5 py-1 rounded-full font-medium';

  return (
    <span
      className={`inline-flex items-center gap-1.5 border font-medium ${sizeStyles} ${colorStyles} ${className}`}
    >
      {dot && (
        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
      )}
      {children}
    </span>
  );
}

