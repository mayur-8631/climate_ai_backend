'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Search, MapPin, Check, X, Compass } from 'lucide-react';
import { useClimate } from '@/context/ClimateContext';
import { Badge } from './Badge';

export function LocationSearch({ className = '' }: { className?: string }) {
  const {
    selectedLocation,
    locationsList,
    selectLocationById,
    searchAndSelectLocation,
    isLoading,
  } = useClimate();

  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const wrapperRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filtered = locationsList.filter((loc) => {
    const term = searchTerm.toLowerCase();
    const name = loc.name?.toLowerCase() ?? '';
    const state = loc.state?.toLowerCase() ?? '';
    return name.includes(term) || state.includes(term);
  });

  const handleSelect = (id: string) => {
    selectLocationById(id);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (filtered.length > 0) {
        handleSelect(filtered[0].id);
      } else if (searchTerm.trim()) {
        searchAndSelectLocation(searchTerm.trim());
        setIsOpen(false);
      }
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  return (
    <div ref={wrapperRef} className={`relative w-full max-w-md ${className}`}>
      <div className="relative flex items-center">
        <MapPin className="absolute left-3 w-4 h-4 text-cyan-400 pointer-events-none" />
        <input
          type="text"
          value={searchTerm}
          onChange={(e) => {
            setSearchTerm(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          onKeyDown={handleKeyDown}
          placeholder={`Current: ${selectedLocation.name}, ${selectedLocation.state}... (search city)`}
          className="w-full pl-9 pr-9 py-2 bg-[#0C2033] hover:bg-[#10273D] focus:bg-[#10273D] border border-[#1A3954] focus:border-cyan-400 text-slate-100 placeholder-slate-400 text-sm rounded-lg outline-none transition-all duration-150 shadow-inner"
        />
        {searchTerm ? (
          <button
            onClick={() => setSearchTerm('')}
            className="absolute right-3 text-slate-400 hover:text-slate-200"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        ) : (
          <Search className="absolute right-3 w-4 h-4 text-slate-500 pointer-events-none" />
        )}
      </div>

      {/* Suggested Locations Dropdown */}
      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1.5 bg-[#0C2033] border border-[#1A3954] rounded-xl shadow-2xl shadow-black/60 overflow-hidden z-50 animate-in fade-in slide-in-from-top-1 duration-150">
          <div className="p-2 border-b border-[#1A3954]/60 flex items-center justify-between text-[11px] text-slate-400 font-medium px-3 bg-[#071827]/60">
            <span className="flex items-center gap-1.5">
              <Compass className="w-3 h-3 text-cyan-400" /> Suggested Monitoring Nodes
            </span>
            <span>{filtered.length} nodes available</span>
          </div>

          <div className="max-h-64 overflow-y-auto divide-y divide-[#1A3954]/40">
            {filtered.length > 0 ? (
              filtered.map((loc) => {
                const isSelected = loc.id === selectedLocation.id;
                return (
                  <button
                    key={loc.id}
                    onClick={() => handleSelect(loc.id)}
                    className={`w-full px-3.5 py-2.5 flex items-center justify-between text-left transition-colors duration-100 ${
                      isSelected
                        ? 'bg-cyan-500/15 text-white'
                        : 'hover:bg-[#122A42] text-slate-200'
                    }`}
                  >
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${
                          isSelected
                            ? 'bg-cyan-500/20 text-cyan-300'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        <MapPin className="w-3.5 h-3.5" />
                      </div>
                      <div>
                        <div className="text-sm font-medium flex items-center gap-1.5">
                          {loc.name}
                          {loc.id === 'pune' && (
                            <span className="text-[10px] text-emerald-400 font-mono bg-emerald-500/10 px-1 rounded">
                              DEFAULT
                            </span>
                          )}
                        </div>
                        <div className="text-xs text-slate-400">
                          {loc.state}, {loc.country}
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-2 shrink-0">
                      <Badge riskLevel={loc.risk_level} size="sm">
                        Score {loc.climate_risk_score}
                      </Badge>
                      {isSelected && (
                        <Check className="w-4 h-4 text-cyan-400" />
                      )}
                    </div>
                  </button>
                );
              })
            ) : (
              <div className="p-4 text-center text-xs text-slate-400">
                No matching cached location found for &ldquo;{searchTerm}&rdquo;. Press Enter to query backend API.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

