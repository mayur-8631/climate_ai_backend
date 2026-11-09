import React from 'react';
import Link from 'next/link';
import { Shield, Heart, ExternalLink, Sparkles } from 'lucide-react';

export function Footer() {
  return (
    <footer className="w-full bg-[#05131F] border-t border-[#1A3954]/70 text-slate-400 text-xs py-8 px-4 lg:px-8 mt-auto">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
        {/* Col 1: Brand & Tagline */}
        <div className="md:col-span-2 space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="w-7 h-7 rounded-lg bg-gradient-to-tr from-emerald-500 to-cyan-400 flex items-center justify-center text-[#071827] font-bold text-xs">
              <Shield className="w-4 h-4 fill-current" />
            </div>
            <span className="text-base font-bold text-slate-100 tracking-tight">
              ClimateTwin <span className="text-cyan-400 font-mono">AI</span>
            </span>
          </div>
          <p className="text-emerald-400 font-mono text-xs uppercase tracking-wider font-semibold">
            Predict. Assess. Protect.
          </p>
          <p className="text-slate-400 text-xs max-w-md leading-relaxed">
            High-resolution geospatial climate intelligence and coupled multi-hazard digital twin platform. Engineered for municipal authorities, urban planners, farmers, and citizens to mitigate localized climate risk.
          </p>
          <div className="text-[11px] text-slate-500 pt-1">
            Built for <strong>PCCOE International Grand Challenge 2026</strong> by Team PrithviNex.
          </div>
        </div>

        {/* Col 2: Navigation Links */}
        <div>
          <div className="text-slate-200 font-semibold mb-3 text-xs tracking-wider uppercase font-mono">
            Platform Modules
          </div>
          <ul className="space-y-2 text-xs">
            <li>
              <Link href="/dashboard" className="hover:text-cyan-400 transition-colors">
                Main Risk Dashboard
              </Link>
            </li>
            <li>
              <Link href="/map" className="hover:text-cyan-400 transition-colors">
                Interactive Geospatial Map
              </Link>
            </li>
            <li>
              <Link href="/simulation" className="hover:text-cyan-400 transition-colors">
                What-If Climate Simulation
              </Link>
            </li>
            <li>
              <Link href="/recommendations" className="hover:text-cyan-400 transition-colors">
                Stakeholder Action Plans
              </Link>
            </li>
            <li>
              <Link href="/about" className="hover:text-cyan-400 transition-colors">
                About Architecture & Team
              </Link>
            </li>
          </ul>
        </div>

        {/* Col 3: Team Credits */}
        <div>
          <div className="text-slate-200 font-semibold mb-3 text-xs tracking-wider uppercase font-mono">
            Team PrithviNex
          </div>
          <ul className="space-y-2 text-xs text-slate-300">
            <li className="flex flex-col">
              <span className="font-medium text-slate-200">Lokesh Joshi</span>
              <span className="text-[11px] text-cyan-400">AI / ML Lead</span>
            </li>
            <li className="flex flex-col">
              <span className="font-medium text-slate-200">Mayuresh Kamble</span>
              <span className="text-[11px] text-emerald-400">Backend & Data Lead</span>
            </li>
            <li className="flex flex-col">
              <span className="font-medium text-slate-200">Pravin Kamble</span>
              <span className="text-[11px] text-amber-400">Frontend & Visualization Lead</span>
            </li>
          </ul>
        </div>
      </div>

      {/* Bottom Legal & Ethics Note */}
      <div className="max-w-7xl mx-auto pt-6 border-t border-[#1A3954]/50 flex flex-col sm:flex-row items-center justify-between gap-3 text-[11px] text-slate-500">
        <div>
          &copy; 2026 ClimateTwin AI. All rights reserved. Team PrithviNex.
        </div>
        <div className="text-center sm:text-right">
          Sample benchmarks are illustrative demo estimates until live FastAPI ML connection is toggled.
        </div>
      </div>
    </footer>
  );
}
