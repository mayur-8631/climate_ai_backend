'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Globe2,
  RefreshCw,
  Sun,
  Moon,
  User,
  Activity,
  Layers,
  Menu,
  X,
  Radio,
  Server,
} from 'lucide-react';
import { useClimate } from '@/context/ClimateContext';
import { LocationSearch } from '@/components/ui/LocationSearch';
import { Badge } from '@/components/ui/Badge';
import { formatTimestamp } from '@/utils/formatters';

export function Navbar({ onToggleMobileMenu }: { onToggleMobileMenu?: () => void }) {
  const pathname = usePathname();
  const {
    selectedLocation,
    isLoading,
    isMockMode,
    dataSourceInfo,
    theme,
    toggleTheme,
    refreshCurrentLocation,
  } = useClimate();

  return (
    <header className="sticky top-0 z-40 w-full bg-[#071827]/90 backdrop-blur-md border-b border-[#1A3954]/80 px-4 lg:px-6 py-2.5 flex items-center justify-between gap-4">
      {/* Left: Mobile Toggle + Location Search */}
      <div className="flex items-center gap-3 flex-1 max-w-xl">
        <button
          onClick={onToggleMobileMenu}
          className="lg:hidden p-2 text-slate-300 hover:text-white hover:bg-[#10273D] rounded-lg transition-colors"
          aria-label="Toggle navigation menu"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Brand on mobile header */}
        <Link
          href="/"
          className="lg:hidden flex items-center gap-2 text-slate-100 font-bold shrink-0"
        >
          <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-500 to-cyan-400 flex items-center justify-center text-navy-950 font-black text-xs shadow-md shadow-emerald-500/20">
            CT
          </div>
          <span className="text-sm tracking-tight hidden sm:inline">ClimateTwin AI</span>
        </Link>

        {/* Global Location Search bar */}
        <div className="flex-1">
          <LocationSearch />
        </div>
      </div>

      {/* Right: Telemetry, Refresh, Theme Toggle & User Profile */}
      <div className="flex items-center gap-2.5 sm:gap-3 shrink-0">
        {/* Selected location status pill (desktop) */}
        <div className="hidden xl:flex items-center gap-2 px-3 py-1 rounded-lg bg-[#0C2033] border border-[#1A3954] text-xs">
          <div className="flex items-center gap-1.5 text-slate-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-medium text-white">{selectedLocation.name}</span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-400">
              {formatTimestamp(selectedLocation.last_updated)}
            </span>
          </div>
        </div>

        {/* API Mode Indicator */}
        <div
          title={dataSourceInfo}
          className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-[#0C2033] border border-[#1A3954] text-[11px] text-slate-300"
        >
          <Radio
            className={`w-3 h-3 ${
              isMockMode ? 'text-amber-400' : 'text-emerald-400'
            }`}
          />
          <span className="font-mono uppercase text-[10px] tracking-wider text-slate-400">
            {isMockMode ? 'MOCK API' : 'FASTAPI LIVE'}
          </span>
        </div>

        {/* Manual Refresh Button */}
        <button
          onClick={refreshCurrentLocation}
          disabled={isLoading}
          title="Refresh current location data"
          className="p-2 rounded-lg bg-[#0C2033] hover:bg-[#122A42] text-slate-300 hover:text-cyan-400 border border-[#1A3954] transition-colors cursor-pointer"
        >
          <RefreshCw
            className={`w-4 h-4 ${isLoading ? 'animate-spin text-cyan-400' : ''}`}
          />
        </button>

        {/* Theme Toggle Button */}
        <button
          onClick={toggleTheme}
          title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
          className="p-2 rounded-lg bg-[#0C2033] hover:bg-[#122A42] text-slate-300 hover:text-amber-300 border border-[#1A3954] transition-colors cursor-pointer"
        >
          {theme === 'dark' ? (
            <Sun className="w-4 h-4 text-amber-400" />
          ) : (
            <Moon className="w-4 h-4 text-cyan-400" />
          )}
        </button>

        {/* User / Team Profile */}
        <Link
          href="/about"
          className="flex items-center gap-2 pl-2 pr-2.5 py-1.5 rounded-lg bg-[#0C2033] hover:bg-[#122A42] border border-[#1A3954] text-xs text-slate-200 transition-colors"
        >
          <div className="w-6 h-6 rounded-md bg-gradient-to-tr from-cyan-500 to-emerald-400 text-[#071827] flex items-center justify-center font-bold text-[10px] shadow-sm">
            PN
          </div>
          <div className="hidden sm:block text-left leading-tight">
            <div className="font-medium text-slate-100 text-[11px]">PrithviNex</div>
            <div className="text-[10px] text-cyan-400 font-mono">PCCOE &apos;26</div>
          </div>
        </Link>
      </div>
    </header>
  );
}

