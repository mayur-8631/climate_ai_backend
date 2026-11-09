'use client';

import React from 'react';
import Link from 'next/link';
import {
  Shield,
  Activity,
  Cpu,
  Database,
  Layers,
  Sparkles,
  Users2,
  CheckCircle2,
  ArrowRight,
  ExternalLink,
  Code2,
  Terminal,
  Globe2,
  Award,
} from 'lucide-react';
import { AppShell } from '@/components/layout/AppShell';
import { TEAM_MEMBERS, WORKFLOW_STAGES } from '@/services/mockData';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';

export default function AboutPage() {
  return (
    <AppShell>
      <div className="space-y-10 max-w-5xl mx-auto">
        {/* Hero Section */}
        <div className="p-8 sm:p-12 rounded-3xl bg-gradient-to-r from-[#0C243D] via-[#0F3150] to-[#091F33] border border-cyan-500/30 space-y-4 shadow-2xl relative overflow-hidden">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#081B2B] border border-cyan-500/30 text-xs text-cyan-300">
            <Award className="w-3.5 h-3.5 text-amber-400" />
            <span className="font-semibold">PCCOE International Grand Challenge 2026</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight leading-tight">
            ClimateTwin <span className="text-cyan-400 font-mono">AI</span>
          </h1>

          <p className="text-sm sm:text-base text-emerald-400 font-mono uppercase tracking-wider font-semibold">
            Predict. Assess. Protect.
          </p>

          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl leading-relaxed">
            A comprehensive, modern climate-intelligence web application engineered by <strong>Team PrithviNex</strong>. ClimateTwin AI bridges earth observation data, multi-hazard deep learning, and intuitive digital twin visualization to shield urban infrastructure, citizens, and agriculture from compounding climate shocks.
          </p>

          <div className="pt-2 flex flex-wrap gap-3">
            <Link href="/dashboard">
              <Button variant="primary" size="md" icon={<ArrowRight className="w-4 h-4" />}>
                Explore Live Platform
              </Button>
            </Link>
            <Link href="/simulation">
              <Button variant="outline" size="md">
                What-If Scenario Lab
              </Button>
            </Link>
          </div>
        </div>

        {/* Project Objectives */}
        <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-6 sm:p-8 shadow-xl space-y-5">
          <div className="border-b border-[#1A3954]/70 pb-3">
            <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold mb-1">
              Grand Challenge Vision
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white">
              Core Mission & Societal Objectives
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-5 text-xs text-slate-300 leading-relaxed">
            <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954] space-y-2">
              <div className="text-base font-bold text-cyan-300">
                1. Hyper-Local Accuracy
              </div>
              <p>
                Eliminate blanket regional weather warnings by mapping compounding vulnerability down to 100m² urban micro-grids and drainage basins.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954] space-y-2">
              <div className="text-base font-bold text-emerald-300">
                2. Multi-Hazard Coupling
              </div>
              <p>
                Unify extreme thermal stress, flood inundation, particulate air stagnation, and groundwater deficits into a single explainable risk index.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-[#081B2B] border border-[#1A3954] space-y-2">
              <div className="text-base font-bold text-amber-300">
                3. Actionable Playbooks
              </div>
              <p>
                Empower citizens, municipal leadership, farmers, and urban architects with prioritized, measurable mitigation checklists rather than raw numbers.
              </p>
            </div>
          </div>
        </div>

        {/* Section 11: Three-Stage Workflow Architecture */}
        <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-6 sm:p-8 shadow-xl space-y-6">
          <div className="border-b border-[#1A3954]/70 pb-3">
            <div className="text-[10px] font-mono tracking-wider uppercase text-emerald-400 font-semibold mb-1">
              System Pipeline
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white">
              The Three-Stage Engineering Workflow
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {WORKFLOW_STAGES.map((stage) => (
              <div
                key={stage.step}
                className="p-5 rounded-xl bg-[#081B2B] border border-[#1A3954] flex flex-col justify-between space-y-3"
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-2xl font-black font-mono text-cyan-400">
                      {stage.step}
                    </span>
                    <Badge variant="cyan" size="sm">
                      Stage {stage.step}
                    </Badge>
                  </div>
                  <h3 className="text-base font-bold text-white">
                    {stage.title}
                  </h3>
                  <div className="text-[11px] font-mono text-cyan-300 mb-2">
                    {stage.subtitle}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {stage.description}
                  </p>
                </div>

                <div className="pt-3 border-t border-[#1A3954]/50 space-y-1.5 text-xs text-slate-300">
                  {stage.points.map((pt, i) => (
                    <div key={i} className="flex items-center gap-1.5">
                      <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                      <span className="text-[11px]">{pt}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Section 11: Team Members and Responsibilities */}
        <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-6 sm:p-8 shadow-xl space-y-6">
          <div className="border-b border-[#1A3954]/70 pb-3">
            <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold mb-1">
              Team PrithviNex
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white">
              Team Leadership & Core Contributions
            </h2>
            <p className="text-xs text-slate-400 mt-1">
              Cross-functional team collaborating across machine learning, backend microservices, and interactive geospatial visualization.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {TEAM_MEMBERS.map((member) => (
              <div
                key={member.name}
                className="p-5 rounded-xl bg-[#081B2B] border border-[#1A3954] flex flex-col justify-between space-y-4 shadow-md"
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-cyan-500 to-emerald-400 text-navy-950 font-black text-lg flex items-center justify-center shadow-md">
                      {member.avatar}
                    </div>
                    <Badge variant="cyan" size="sm">
                      {member.badge}
                    </Badge>
                  </div>

                  <h3 className="text-base font-bold text-white">
                    {member.name}
                  </h3>
                  <div className="text-xs font-mono font-semibold text-emerald-400 mb-0.5">
                    {member.role}
                  </div>
                  <div className="text-[10px] text-slate-400 font-mono mb-2">
                    {member.focus}
                  </div>
                  <p className="text-xs text-slate-300 leading-relaxed">
                    {member.bio}
                  </p>
                </div>

                <div className="pt-3 border-t border-[#1A3954]/60 space-y-1 text-xs text-slate-300">
                  <span className="font-mono text-[10px] uppercase text-slate-400 block mb-1">
                    Deliverables:
                  </span>
                  {member.contributions.map((c, i) => (
                    <div key={i} className="flex items-center gap-1.5 text-[11px]">
                      <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0" />
                      <span>{c}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Technical Stack Specifications */}
        <div className="rounded-2xl bg-gradient-to-b from-[#0C2237] to-[#071928] border border-[#1A3954] p-6 sm:p-8 shadow-xl space-y-4">
          <div className="border-b border-[#1A3954]/70 pb-3">
            <div className="text-[10px] font-mono tracking-wider uppercase text-cyan-400 font-semibold mb-1">
              Technology Stack
            </div>
            <h2 className="text-xl font-bold text-white">
              Built with Modern Standards
            </h2>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
            <div className="p-3 rounded-lg bg-[#081B2B] border border-[#1A3954]">
              <span className="text-cyan-400 font-bold block mb-1">Frontend Core</span>
              <span className="text-slate-300 text-[11px]">Next.js 16 + React 19 + TypeScript</span>
            </div>
            <div className="p-3 rounded-lg bg-[#081B2B] border border-[#1A3954]">
              <span className="text-emerald-400 font-bold block mb-1">Styling & UI</span>
              <span className="text-slate-300 text-[11px]">Tailwind CSS v4 + Lucide Icons</span>
            </div>
            <div className="p-3 rounded-lg bg-[#081B2B] border border-[#1A3954]">
              <span className="text-amber-400 font-bold block mb-1">Geospatial GIS</span>
              <span className="text-slate-300 text-[11px]">React Leaflet + CartoDB Dark Tiles</span>
            </div>
            <div className="p-3 rounded-lg bg-[#081B2B] border border-[#1A3954]">
              <span className="text-purple-400 font-bold block mb-1">Data Visuals</span>
              <span className="text-slate-300 text-[11px]">Recharts 3 + Custom SVG Gauges</span>
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}

