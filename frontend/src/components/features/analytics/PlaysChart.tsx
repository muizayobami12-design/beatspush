'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { useThemeStore } from '@/store/themeStore';
import { Loader2 } from 'lucide-react';

interface PlaysData {
  date: string;
  plays: number;
  uniqueListeners?: number;
}

interface PlaysChartProps {
  data: PlaysData[];
  isLoading?: boolean;
  title?: string;
}

export function PlaysChart({ data, isLoading, title = 'Plays Over Time' }: PlaysChartProps) {
  const theme = useThemeStore((state) => state.theme);
  const isDark = theme === 'dark';

  // Chart colors based on theme
  const colors = useMemo(
    () => ({
      primary: '#667eea',
      secondary: '#764ba2',
      grid: isDark ? '#374151' : '#e5e7eb',
      text: isDark ? '#9ca3af' : '#6b7280',
      tooltip: isDark ? '#1f2937' : '#ffffff',
    }),
    [isDark]
  );

  // Format date for display
  const formatXAxis = (dateStr: string) => {
    // If already formatted (like "Jan 1"), return as-is
    if (!dateStr.includes('-') && !dateStr.includes('/')) {
      return dateStr;
    }
    // Otherwise parse and format
    const date = new Date(dateStr);
    if (isNaN(date.getTime())) {
      return dateStr; // Return original if invalid
    }
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Format number with commas
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div
          className="rounded-lg border shadow-lg p-3"
          style={{
            backgroundColor: colors.tooltip,
            borderColor: colors.grid,
          }}
        >
          <p className="text-sm font-medium mb-2">{formatXAxis(label)}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: entry.color }}
              />
              <span className="text-muted-foreground">{entry.name}:</span>
              <span className="font-semibold">{formatNumber(entry.value)}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[300px] bg-card rounded-lg border">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[300px] bg-card rounded-lg border">
        <p className="text-muted-foreground mb-2">No play data available</p>
        <p className="text-sm text-muted-foreground">
          Data will appear once users start playing your beats
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart
          data={data}
          margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis
            dataKey="date"
            tickFormatter={formatXAxis}
            stroke={colors.text}
            style={{ fontSize: '12px' }}
          />
          <YAxis
            stroke={colors.text}
            style={{ fontSize: '12px' }}
            tickFormatter={formatNumber}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '14px' }}
            iconType="circle"
          />
          <Line
            type="monotone"
            dataKey="plays"
            name="Total Plays"
            stroke={colors.primary}
            strokeWidth={2}
            dot={{ fill: colors.primary, r: 4 }}
            activeDot={{ r: 6 }}
          />
          {data[0]?.uniqueListeners !== undefined && (
            <Line
              type="monotone"
              dataKey="uniqueListeners"
              name="Unique Listeners"
              stroke={colors.secondary}
              strokeWidth={2}
              dot={{ fill: colors.secondary, r: 4 }}
              activeDot={{ r: 6 }}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
