'use client';

import React from 'react';
import {
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

interface RiskComparisonProps {
  risks: {
    heat: number;
    flood: number;
    air_quality: number;
    water_stress: number;
  };
  locationName: string;
}

export function RiskComparisonRadar({ risks, locationName }: RiskComparisonProps) {
  const radarData = [
    { subject: 'Extreme Heat', score: risks.heat, benchmark: 50 },
    { subject: 'Precipitation/Flood', score: risks.flood, benchmark: 50 },
    { subject: 'Air Quality (AQI)', score: risks.air_quality, benchmark: 50 },
    { subject: 'Water Stress', score: risks.water_stress, benchmark: 50 },
  ];

  return (
    <div className="h-64 w-full flex items-center justify-center">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart cx="50%" cy="50%" outerRadius="75%" data={radarData}>
          <PolarGrid stroke="#1A3954" />
          <PolarAngleAxis
            dataKey="subject"
            stroke="#94A3B8"
            fontSize={11}
            tickLine={false}
          />
          <PolarRadiusAxis
            angle={30}
            domain={[0, 100]}
            stroke="#475569"
            fontSize={9}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#0C2033',
              borderColor: '#1A3954',
              borderRadius: '0.75rem',
              color: '#F8FAFC',
              fontSize: '12px',
              boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)',
            }}
            formatter={(value: any, name: any) => [
              `${value} / 100`,
              name === 'score' ? locationName : 'Safe Threshold',
            ]}
          />
          <Radar
            name="score"
            dataKey="score"
            stroke="#10B981"
            fill="#10B981"
            fillOpacity={0.4}
            strokeWidth={2}
          />
          <Radar
            name="benchmark"
            dataKey="benchmark"
            stroke="#22D3EE"
            fill="#22D3EE"
            fillOpacity={0.1}
            strokeDasharray="3 3"
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}

