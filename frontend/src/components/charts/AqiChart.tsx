'use client';

import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import { HistoricalDataPoint } from '@/types/climate';

interface AqiChartProps {
  data: HistoricalDataPoint[];
}

export function AqiChart({ data }: AqiChartProps) {
  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 10, left: -20, bottom: 0 }}
        >
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
            unit=" AQI"
          />
          {/* WHO / CPCB Moderate Threshold Line at 100 */}
          <ReferenceLine
            y={100}
            stroke="#F59E0B"
            strokeDasharray="4 4"
            label={{
              value: 'Mod Threshold (100)',
              fill: '#F59E0B',
              fontSize: 10,
              position: 'insideTopRight',
            }}
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
            formatter={(value: any) => [`${value} AQI`, 'Air Quality']}
            labelFormatter={(label) => `Time: ${label}`}
          />
          <Line
            type="monotone"
            dataKey="aqi"
            stroke="#A855F7"
            strokeWidth={2.5}
            dot={{ fill: '#A855F7', r: 3 }}
            activeDot={{ r: 6, fill: '#C084FC', stroke: '#071827', strokeWidth: 2 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

