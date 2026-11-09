'use client';

import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { HistoricalDataPoint } from '@/types/climate';

interface RainfallChartProps {
  data: HistoricalDataPoint[];
}

export function RainfallChart({ data }: RainfallChartProps) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
          <defs>
            <linearGradient id="rainGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22D3EE" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#0891B2" stopOpacity={0.4} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1A3954" opacity={0.6} />
          <XAxis
            dataKey="timeLabel"
            stroke="#64748B"
            fontSize={11}
            tickLine={false}
          />
          <YAxis
            stroke="#64748B"
            fontSize={11}
            tickLine={false}
            unit="mm"
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
            formatter={(value: any) => [`${value} mm`, 'Rainfall']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Bar
            dataKey="rainfall"
            fill="url(#rainGradient)"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

