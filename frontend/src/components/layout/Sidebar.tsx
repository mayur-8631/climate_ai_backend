'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Home,
  LayoutDashboard,
  MapPin,
  Sliders,
  FileCheck2,
  Users2,
  Activity,
  Layers,
  ChevronRight,
  Shield,
  Sparkles,
  ExternalLink,
  X,
} from 'lucide-react';
import { Badge } from '@/components/ui/Badge';

interface SidebarProps {
  onCloseMobile?: () => void;
}

const NAV_ITEMS = [
  {
    name: 'Overview',
    href: '/',
    icon: Home,
    description: 'Landing & architecture overview',
  },
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
    description: 'Real-time multi-hazard risk engine',
    badge: 'CORE',
  },
  {
    name: 'Climate Map',
    href: '/map',
    icon: MapPin,
    description: 'Geospatial GIS monitoring & layers',
  },
  {
    name: 'What-If Simulation',
    href: '/simulation',
    icon: Sliders,
    description: 'Scenario analysis & Explainable AI',
    badge: 'AI LAB',
  },
  {
    name: 'Recommendations',
    href: '/recommendations',
    icon: FileCheck2,
    description: 'Role-specific action protocols',
  },
  {
    name: 'About & Team',
    href: '/about',
    icon: Users2,
    description: 'Team PrithviNex & PCCOE Grand Challenge',
  },
];

export function Sidebar({ onCloseMobile }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="w-64 h-full bg-[#071827] border-r border-[#1A3954]/80 flex flex-col justify-between select-none">
      {/* Brand Header */}
      <div>
        <div className="px-5 py-5 border-b border-[#1A3954]/80 flex items-center justify-between">
          <Link
            href="/"
            onClick={onCloseMobile}
            className="flex items-center gap-3 group"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 via-teal-400 to-cyan-400 flex items-center justify-center text-navy-950 font-black text-base shadow-lg shadow-emerald-500/25 group-hover:scale-105 transition-transform duration-200">
              <Shield className="w-5 h-5 text-[#071827] fill-[#071827]" />
            </div>
            <div>
              <div className="font-extrabold text-base tracking-tight text-white flex items-center gap-1.5">
                ClimateTwin <span className="text-cyan-400 font-mono text-xs">AI</span>
              </div>
              <div className="text-[10px] tracking-wider uppercase text-emerald-400 font-semibold">
                Predict. Assess. Protect.
              </div>
            </div>
          </Link>

          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              className="lg:hidden p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-[#10273D]"
              aria-label="Close menu"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1 mt-2">
          <div className="px-3 py-1.5 text-[10px] uppercase font-semibold text-slate-500 tracking-wider">
            Navigation Modules
          </div>

          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive =
              item.href === '/'
                ? pathname === '/'
                : pathname === item.href || pathname?.startsWith(item.href + '/');

            return (
              <Link
                key={item.href}
                href={item.href}
                onClick={onCloseMobile}
                className={`group flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-150 ${
                  isActive
                    ? 'bg-gradient-to-r from-emerald-500/20 via-cyan-500/10 to-transparent text-white border-l-2 border-emerald-400 shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-[#0D2439]'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`w-7 h-7 rounded-lg flex items-center justify-center transition-colors ${
                      isActive
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'text-slate-400 group-hover:text-cyan-400 group-hover:bg-[#122E47]'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                  </div>
                  <div>
                    <div className={isActive ? 'font-semibold text-white' : ''}>
                      {item.name}
                    </div>
                  </div>
                </div>

                {item.badge ? (
                  <span
                    className={`text-[9px] font-mono px-1.5 py-0.5 rounded tracking-wider ${
                      isActive
                        ? 'bg-emerald-500/25 text-emerald-300 font-semibold'
                        : 'bg-[#10273D] text-slate-400 group-hover:text-cyan-300'
                    }`}
                  >
                    {item.badge}
                  </span>
                ) : (
                  <ChevronRight
                    className={`w-3.5 h-3.5 transition-transform ${
                      isActive
                        ? 'text-emerald-400 opacity-100 translate-x-0.5'
                        : 'text-slate-600 opacity-0 group-hover:opacity-100'
                    }`}
                  />
                )}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Footer / Team Attribution Widget */}
      <div className="p-3 border-t border-[#1A3954]/80 bg-[#061421]">
        <div className="p-3 rounded-xl bg-gradient-to-b from-[#0B2135] to-[#071827] border border-[#1A3954]/70">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-semibold">
              Team PrithviNex
            </span>
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          </div>
          <p className="text-[11px] text-slate-300 font-medium">
            PCCOE Grand Challenge &apos;26
          </p>
          <div className="mt-2 pt-2 border-t border-[#1A3954]/50 flex items-center justify-between text-[10px] text-slate-400">
            <span>FastAPI • Next.js • ML</span>
            <span className="text-emerald-400 font-mono">v1.0-MVP</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

