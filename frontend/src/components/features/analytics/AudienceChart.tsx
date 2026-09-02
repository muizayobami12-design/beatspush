'use client';

import { useMemo } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { useThemeStore } from '@/store/themeStore';
import { Loader2, Globe } from 'lucide-react';

interface AudienceData {
  country: string;
  listeners: number;
}

interface AudienceChartProps {
  data: AudienceData[];
  isLoading?: boolean;
  title?: string;
}

export function AudienceChart({
  data,
  isLoading,
  title = 'Audience by Country',
}: AudienceChartProps) {
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

  // Sort data by listeners (descending)
  const sortedData = useMemo(() => {
    if (!data) return [];
    return [...data].sort((a, b) => b.listeners - a.listeners);
  }, [data]);

  // Format number with commas
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  // Calculate total listeners
  const totalListeners = useMemo(() => {
    return sortedData.reduce((sum, item) => sum + item.listeners, 0);
  }, [sortedData]);

  // Calculate percentage
  const getPercentage = (listeners: number) => {
    if (totalListeners === 0) return 0;
    return ((listeners / totalListeners) * 100).toFixed(1);
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div
          className="rounded-lg border shadow-lg p-3"
          style={{
            backgroundColor: colors.tooltip,
            borderColor: colors.grid,
          }}
        >
          <p className="text-sm font-medium mb-1">{data.country}</p>
          <p className="text-sm text-muted-foreground">
            {formatNumber(data.listeners)} listeners ({getPercentage(data.listeners)}%)
          </p>
        </div>
      );
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-[400px] bg-card rounded-lg border">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-[400px] bg-card rounded-lg border">
        <Globe className="w-12 h-12 text-muted-foreground mb-3" />
        <p className="text-muted-foreground mb-2">No audience data available</p>
        <p className="text-sm text-muted-foreground">
          Data will appear as users from different countries listen to your beats
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      
      {/* Bar Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={sortedData}
          layout="vertical"
          margin={{ top: 5, right: 30, left: 100, bottom: 5 }}
        >
          <defs>
            <linearGradient id="audienceGradient" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor={colors.primary} stopOpacity={0.8} />
              <stop offset="100%" stopColor={colors.secondary} stopOpacity={0.8} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={colors.grid} />
          <XAxis
            type="number"
            stroke={colors.text}
            style={{ fontSize: '12px' }}
            tickFormatter={formatNumber}
          />
          <YAxis
            type="category"
            dataKey="country"
            stroke={colors.text}
            style={{ fontSize: '12px' }}
            width={90}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar
            dataKey="listeners"
            fill="url(#audienceGradient)"
            radius={[0, 8, 8, 0]}
          />
        </BarChart>
      </ResponsiveContainer>

      {/* Summary Stats */}
      <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Total Listeners</p>
          <p className="text-xl font-bold text-foreground">
            {formatNumber(totalListeners)}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Top Country</p>
          <p className="text-xl font-bold text-foreground">
            {sortedData[0]?.country || 'N/A'}
          </p>
        </div>
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Countries Reached</p>
          <p className="text-xl font-bold text-foreground">{sortedData.length}</p>
        </div>
        <div className="space-y-1">
          <p className="text-xs text-muted-foreground">Top Country Share</p>
          <p className="text-xl font-bold text-foreground">
            {sortedData[0] ? `${getPercentage(sortedData[0].listeners)}%` : 'N/A'}
          </p>
        </div>
      </div>
    </div>
  );
}
