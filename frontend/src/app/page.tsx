'use client';

import React from 'react';
import Link from 'next/link';
import {
  Shield,
  Activity,
  Flame,
  CloudRain,
  Wind,
  Droplets,
  ArrowRight,
  Sparkles,
  Layers,
  Cpu,
  BarChart3,
  Sliders,
  CheckCircle2,
  Users2,
  Compass,
  MapPin,
  ChevronRight,
  Database,
  ShieldAlert,
} from 'lucide-react';
import { TEAM_MEMBERS, WORKFLOW_STAGES } from '@/services/mockData';
import { Button } from '@/components/ui/Button';
import { Badge } from '@/components/ui/Badge';
import { Footer } from '@/components/layout/Footer';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#071827] text-slate-100 flex flex-col font-sans selection:bg-cyan-500/30">
      {/* Top Floating Glass Navigation */}
      <header className="sticky top-0 z-50 w-full bg-[#071827]/85 backdrop-blur-md border-b border-[#1A3954]/70 px-4 sm:px-8 py-3.5 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-2.5 group">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-400 flex items-center justify-center text-[#071827] font-black text-sm shadow-lg shadow-emerald-500/25 group-hover:scale-105 transition-transform">
            <Shield className="w-4 h-4 fill-[#071827]" />
          </div>
          <div>
            <span className="font-extrabold text-base tracking-tight text-white">
              ClimateTwin <span className="text-cyan-400 font-mono text-xs">AI</span>
            </span>
          </div>
        </Link>

        <nav className="hidden md:flex items-center gap-6 text-xs text-slate-300 font-medium">
          <Link href="/dashboard" className="hover:text-cyan-400 transition-colors">
            Live Dashboard
          </Link>
          <Link href="/map" className="hover:text-cyan-400 transition-colors">
            Interactive Map
          </Link>
          <Link href="/simulation" className="hover:text-cyan-400 transition-colors">
            What-If Simulator
          </Link>
          <Link href="/recommendations" className="hover:text-cyan-400 transition-colors">
            Recommendations
          </Link>
          <Link href="/about" className="hover:text-cyan-400 transition-colors">
            Team & Science
          </Link>
        </nav>

        <div className="flex items-center gap-3">
          <Link href="/dashboard">
            <Button
              variant="primary"
              size="sm"
              icon={<ArrowRight className="w-3.5 h-3.5" />}
            >
              Explore Dashboard
            </Button>
          </Link>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 sm:pt-20 sm:pb-28 px-4 sm:px-8 max-w-7xl mx-auto w-full">
        {/* Ambient background glows */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[350px] bg-gradient-to-tr from-emerald-500/15 via-cyan-500/15 to-transparent rounded-full blur-3xl pointer-events-none -z-10" />

        <div className="text-center max-w-3xl mx-auto space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#0E263D] border border-cyan-500/30 text-xs text-cyan-300 shadow-sm">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="font-semibold">Team PrithviNex</span>
            <span className="text-slate-500">•</span>
            <span className="text-slate-300">PCCOE International Grand Challenge 2026</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-black tracking-tight text-white leading-[1.1]">
            Predict. Assess. <span className="bg-gradient-to-r from-emerald-400 via-teal-300 to-cyan-400 bg-clip-text text-transparent">Protect.</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed font-normal">
            A next-generation localized climate-intelligence and multi-hazard digital twin web platform. Synthesizing satellite telemetry, deep learning risk models, and actionable mitigation protocols for Indian cities.
          </p>

          <div className="pt-2 flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link href="/dashboard" className="w-full sm:w-auto">
              <Button
                variant="primary"
                size="lg"
                icon={<ArrowRight className="w-4 h-4" />}
                className="w-full sm:w-auto shadow-emerald-500/25"
              >
                Launch Climate Dashboard
              </Button>
            </Link>
            <Link href="/map" className="w-full sm:w-auto">
              <Button
                variant="outline"
                size="lg"
                icon={<MapPin className="w-4 h-4 text-cyan-400" />}
                className="w-full sm:w-auto"
              >
                Interactive Risk Map
              </Button>
            </Link>
          </div>

          {/* Quick telemetry badge */}
          <div className="text-xs text-slate-400 pt-2 flex items-center justify-center gap-2">
            <span className="font-mono text-cyan-400">Default Baseline Node:</span>
            <span className="text-white font-medium">Pune, Maharashtra</span>
            <span className="text-slate-500">•</span>
            <span className="text-emerald-400 font-mono">FastAPI API Ready</span>
          </div>
        </div>

        {/* Live Metrics Snapshot Bar */}
        <div className="mt-14 max-w-5xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-4 p-4 rounded-2xl bg-[#0B2135]/90 border border-[#1A3954] shadow-2xl backdrop-blur-md">
          <div className="p-3 text-center border-r border-[#1A3954]/60 last:border-none">
            <div className="text-2xl sm:text-3xl font-extrabold font-mono text-cyan-300">
              100m²
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Hyper-Local Grid Resolution
            </div>
          </div>
          <div className="p-3 text-center border-r border-[#1A3954]/60 last:border-none">
            <div className="text-2xl sm:text-3xl font-extrabold font-mono text-emerald-400">
              4 Core
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Compounding Hazard Vectors
            </div>
          </div>
          <div className="p-3 text-center border-r border-[#1A3954]/60 last:border-none">
            <div className="text-2xl sm:text-3xl font-extrabold font-mono text-amber-400">
              &lt; 24h
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Early Warning Horizon
            </div>
          </div>
          <div className="p-3 text-center">
            <div className="text-2xl sm:text-3xl font-extrabold font-mono text-purple-400">
              4 Roles
            </div>
            <div className="text-xs text-slate-400 mt-1">
              Segmented Stakeholder Actions
            </div>
          </div>
        </div>
      </section>

      {/* 4 Compounding Hazards Overview */}
      <section className="py-16 px-4 sm:px-8 max-w-7xl mx-auto w-full border-t border-[#1A3954]/60">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold mb-2">
            Coupled Risk Assessment
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white">
            Four Interconnected Climate Threats
          </h2>
          <p className="text-slate-300 text-xs sm:text-sm mt-2">
            Traditional tools examine weather threats in isolation. ClimateTwin AI analyzes compounding interactions between atmospheric, hydrological, and anthropogenic factors.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Heat */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] hover:border-orange-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-orange-500/15 text-orange-400 flex items-center justify-center border border-orange-500/30">
              <Flame className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Extreme Heat Stress</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Detects urban heat islands, concrete thermal absorption, and dangerous wet-bulb temperatures threatening outdoor workforces.
            </p>
            <div className="text-[11px] font-mono text-orange-300 bg-orange-500/10 px-2 py-1 rounded inline-block">
              Thermal Index Scoring
            </div>
          </div>

          {/* Flood */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] hover:border-cyan-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-cyan-500/15 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
              <CloudRain className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Precipitation & Flooding</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Forecasts pluvial waterlogging, river confluence overflows, and stormwater canal choke points during intense monsoon cloudbursts.
            </p>
            <div className="text-[11px] font-mono text-cyan-300 bg-cyan-500/10 px-2 py-1 rounded inline-block">
              Hydrologic Saturation Modeling
            </div>
          </div>

          {/* Air Quality */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] hover:border-purple-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/15 text-purple-400 flex items-center justify-center border border-purple-500/30">
              <Wind className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Air Quality & Aerosol</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Monitors PM2.5 and PM10 dispersion, atmospheric boundary layer compression, and nocturnal thermal inversion smog traps.
            </p>
            <div className="text-[11px] font-mono text-purple-300 bg-purple-500/10 px-2 py-1 rounded inline-block">
              Boundary Inversion Tracking
            </div>
          </div>

          {/* Water Stress */}
          <div className="p-5 rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] hover:border-blue-500/40 transition-all space-y-3">
            <div className="w-10 h-10 rounded-xl bg-blue-500/15 text-blue-400 flex items-center justify-center border border-blue-500/30">
              <Droplets className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Aquifer & Water Stress</h3>
            <p className="text-xs text-slate-300 leading-relaxed">
              Computes groundwater draft deficits, municipal reservoir storage buffers, and agricultural irrigation replenishment demands.
            </p>
            <div className="text-[11px] font-mono text-blue-300 bg-blue-500/10 px-2 py-1 rounded inline-block">
              Basin Depletion Analytics
            </div>
          </div>
        </div>
      </section>

      {/* How It Works: 3-Stage Workflow */}
      <section className="py-16 px-4 sm:px-8 max-w-7xl mx-auto w-full border-t border-[#1A3954]/60 bg-[#061624]">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <div className="text-[10px] font-mono tracking-wider uppercase text-emerald-400 font-semibold mb-2">
            Architecture Blueprint
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white">
            Three-Stage End-to-End Workflow
          </h2>
          <p className="text-slate-300 text-xs sm:text-sm mt-2">
            From raw satellite multi-spectral bands to role-specific municipal action plans.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {WORKFLOW_STAGES.map((stage) => (
            <div
              key={stage.step}
              className="p-6 rounded-2xl bg-[#091E30] border border-[#1A3954] flex flex-col justify-between space-y-4"
            >
              <div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-3xl font-black font-mono text-cyan-400/40">
                    {stage.step}
                  </span>
                  <Badge variant="cyan" size="sm">
                    Stage {stage.step}
                  </Badge>
                </div>
                <h3 className="text-lg font-bold text-white tracking-tight">
                  {stage.title}
                </h3>
                <div className="text-xs font-mono text-cyan-300 mb-2">
                  {stage.subtitle}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed mb-4">
                  {stage.description}
                </p>
              </div>

              <div className="pt-3 border-t border-[#1A3954]/60 space-y-2">
                {stage.points.map((pt, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 text-xs text-slate-300"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                    <span>{pt}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Team PrithviNex Section */}
      <section className="py-16 px-4 sm:px-8 max-w-7xl mx-auto w-full border-t border-[#1A3954]/60">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold mb-2">
            Engineering & Leadership
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white">
            Team PrithviNex
          </h2>
          <p className="text-slate-300 text-xs sm:text-sm mt-2">
            Developed for <strong>PCCOE International Grand Challenge 2026</strong>.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {TEAM_MEMBERS.map((member) => (
            <div
              key={member.name}
              className="p-6 rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] flex flex-col justify-between space-y-4 shadow-xl"
            >
              <div>
                <div className="flex items-center justify-between mb-4">
                  <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-cyan-500 to-emerald-400 text-navy-950 font-black text-lg flex items-center justify-center shadow-md">
                    {member.avatar}
                  </div>
                  <Badge variant="cyan" size="sm">
                    {member.badge}
                  </Badge>
                </div>

                <h3 className="text-lg font-bold text-white tracking-tight">
                  {member.name}
                </h3>
                <div className="text-xs font-mono font-semibold text-emerald-400 mb-1">
                  {member.role}
                </div>
                <div className="text-[11px] text-slate-400 font-mono mb-3">
                  {member.focus}
                </div>
                <p className="text-xs text-slate-300 leading-relaxed">
                  {member.bio}
                </p>
              </div>

              <div className="pt-3 border-t border-[#1A3954]/60 space-y-1.5 text-[11px] text-slate-300">
                <span className="font-mono text-[10px] uppercase text-slate-400 block mb-1">
                  Key Deliverables:
                </span>
                {member.contributions.map((c, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
                    <span>{c}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Call to Action Banner */}
      <section className="py-14 px-4 sm:px-8 max-w-7xl mx-auto w-full">
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-r from-[#0C2842] via-[#0E3456] to-[#092238] border border-cyan-500/30 text-center space-y-6 shadow-2xl relative overflow-hidden">
          <div className="max-w-2xl mx-auto space-y-3">
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              Ready to Explore Localized Climate Risk Intelligence?
            </h2>
            <p className="text-xs sm:text-sm text-slate-300 leading-relaxed">
              Explore the real-time Pune baseline, simulate compound weather shocks, inspect geospatial Leaflet GIS layers, and review stakeholder mitigation protocols.
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-4">
            <Link href="/dashboard">
              <Button
                variant="primary"
                size="lg"
                icon={<ArrowRight className="w-4 h-4" />}
                className="shadow-emerald-500/30 text-sm font-bold"
              >
                Open Climate Dashboard
              </Button>
            </Link>
            <Link href="/simulation">
              <Button
                variant="secondary"
                size="lg"
                icon={<Sliders className="w-4 h-4" />}
                className="text-sm font-semibold"
              >
                What-If Simulation Lab
              </Button>
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
