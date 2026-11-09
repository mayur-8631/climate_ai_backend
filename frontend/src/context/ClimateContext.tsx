'use client';

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from 'react';
import { LocationData } from '@/types/climate';
import { climateApi } from '@/services/api';
import { MOCK_LOCATIONS } from '@/services/mockData';

interface ClimateContextType {
  selectedLocation: LocationData;
  locationsList: LocationData[];
  isLoading: boolean;
  isMockMode: boolean;
  dataSourceInfo: string;
  theme: 'dark' | 'light';
  toggleTheme: () => void;
  selectLocationById: (id: string) => Promise<void>;
  searchAndSelectLocation: (query: string) => Promise<void>;
  refreshCurrentLocation: () => Promise<void>;
}

const ClimateContext = createContext<ClimateContextType | undefined>(undefined);

export function ClimateProvider({ children }: { children: ReactNode }) {
  // Default location is Pune, Maharashtra, India matching section 5B & 10
  const [selectedLocation, setSelectedLocation] = useState<LocationData>(
    MOCK_LOCATIONS[0]
  );
  const [locationsList, setLocationsList] = useState<LocationData[]>(MOCK_LOCATIONS);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isMockMode, setIsMockMode] = useState<boolean>(true);
  const [dataSourceInfo, setDataSourceInfo] = useState<string>(
    'Illustrative Sample Baseline'
  );
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  // Load initial locations
  useEffect(() => {
    let mounted = true;
    async function loadData() {
      setIsLoading(true);
      try {
        const res = await climateApi.getClimateSummary('pune');
        if (mounted) {
          setSelectedLocation(res.data);
          setIsMockMode(res.isMock);
          setDataSourceInfo(
            res.isMock
              ? 'Illustrative Demo Dataset (Pune Baseline)'
              : 'Live FastAPI Connected (Mayuresh Kamble /api/risk-score)'
          );
        }
        const locsRes = await climateApi.getLocations();
        if (mounted && locsRes.data.length > 0) {
          setLocationsList(locsRes.data);
        }
      } catch (err) {
        console.warn('Initial data load notice:', err);
      } finally {
        if (mounted) setIsLoading(false);
      }
    }

    loadData();
    return () => {
      mounted = false;
    };
  }, []);

  // Theme toggle
  const toggleTheme = () => {
    setTheme((prev) => {
      const next = prev === 'dark' ? 'light' : 'dark';
      if (typeof document !== 'undefined') {
        if (next === 'light') {
          document.documentElement.classList.add('light-mode');
          document.documentElement.classList.remove('dark');
        } else {
          document.documentElement.classList.remove('light-mode');
          document.documentElement.classList.add('dark');
        }
      }
      return next;
    });
  };

  const selectLocationById = async (id: string) => {
    setIsLoading(true);
    try {
      const res = await climateApi.getClimateSummary(id);
      setSelectedLocation(res.data);
      setIsMockMode(res.isMock);
      setDataSourceInfo(
        res.isMock
          ? `Illustrative Demo Dataset (${res.data.name})`
          : `Live FastAPI (${res.data.name})`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const searchAndSelectLocation = async (query: string) => {
    if (!query.trim()) return;
    setIsLoading(true);
    try {
      const res = await climateApi.getClimateSummary(query);
      setSelectedLocation(res.data);
      setIsMockMode(res.isMock);
      setDataSourceInfo(
        res.isMock
          ? `Illustrative Demo Dataset (${res.data.name})`
          : `Live FastAPI (${res.data.name})`
      );
    } finally {
      setIsLoading(false);
    }
  };

  const refreshCurrentLocation = async () => {
    setIsLoading(true);
    try {
      const res = await climateApi.getClimateSummary(selectedLocation.id);
      setSelectedLocation(res.data);
      setIsMockMode(res.isMock);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <ClimateContext.Provider
      value={{
        selectedLocation,
        locationsList,
        isLoading,
        isMockMode,
        dataSourceInfo,
        theme,
        toggleTheme,
        selectLocationById,
        searchAndSelectLocation,
        refreshCurrentLocation,
      }}
    >
      {children}
    </ClimateContext.Provider>
  );
}

export function useClimate() {
  const context = useContext(ClimateContext);
  if (!context) {
    throw new Error('useClimate must be used within a ClimateProvider');
  }
  return context;
}

