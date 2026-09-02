'use client';

import { useMemo } from 'react';
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { useThemeStore } from '@/store/themeStore';
import { Loader2, Music } from 'lucide-react';

interface BeatData {
  name: string;
  plays: number;
  id: string;
}

interface TopBeatsChartProps {
  data: BeatData[];
  isLoading?: boolean;
  title?: string;
  maxBeats?: number;
}

export function TopBeatsChart({
  data,
  isLoading,
  title = 'Top Performing Beats',
  maxBeats = 5,
}: TopBeatsChartProps) {
  const theme = useThemeStore((state) => state.theme);
  const isDark = theme === 'dark';

  // Color palette for the pie chart
  const COLORS = [
    '#667eea',
    '#764ba2',
    '#f093fb',
    '#4facfe',
    '#43e97b',
    '#fa709a',
    '#fee140',
    '#30cfd0',
  ];

  const colors = useMemo(
    () => ({
      tooltip: isDark ? '#1f2937' : '#ffffff',
      text: isDark ? '#9ca3af' : '#6b7280',
    }),
    [isDark]
  );

  // Get top N beats
  const topBeats = useMemo(() => {
    if (!data || data.length === 0) return [];
    return [...data]
      .sort((a, b) => b.plays - a.plays)
      .slice(0, maxBeats);
  }, [data, maxBeats]);

  // Format number with commas
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  // Calculate total plays
  const totalPlays = useMemo(() => {
    return topBeats.reduce((sum, beat) => sum + beat.plays, 0);
  }, [topBeats]);

  // Calculate percentage
  const getPercentage = (plays: number) => {
    if (totalPlays === 0) return 0;
    return ((plays / totalPlays) * 100).toFixed(1);
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
          }}
        >
          <p className="text-sm font-medium mb-1">{data.name}</p>
          <p className="text-sm text-muted-foreground">
            {formatNumber(data.plays)} plays ({getPercentage(data.plays)}%)
          </p>
        </div>
      );
    }
    return null;
  };

  // Custom label
  const renderLabel = (entry: any) => {
    return `${getPercentage(entry.plays)}%`;
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
        <Music className="w-12 h-12 text-muted-foreground mb-3" />
        <p className="text-muted-foreground mb-2">No beat data available</p>
        <p className="text-sm text-muted-foreground">
          Upload beats to see performance metrics
        </p>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-lg border p-6">
      <h3 className="text-lg font-semibold mb-4">{title}</h3>
      
      {/* Pie Chart */}
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={topBeats}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderLabel}
            outerRadius={100}
            fill="#8884d8"
            dataKey="plays"
          >
            {topBeats.map((_entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Legend with stats */}
      <div className="mt-6 space-y-2">
        {topBeats.map((beat, index) => (
          <div key={beat.id} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div
                className="w-4 h-4 rounded"
                style={{ backgroundColor: COLORS[index % COLORS.length] }}
              />
              <span className="text-sm text-foreground truncate max-w-[200px]">
                {beat.name}
              </span>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-sm font-medium text-foreground">
                {formatNumber(beat.plays)}
              </span>
              <span className="text-xs text-muted-foreground w-12 text-right">
                {getPercentage(beat.plays)}%
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Total */}
      <div className="mt-4 pt-4 border-t flex items-center justify-between">
        <span className="text-sm font-medium text-muted-foreground">Total Plays</span>
        <span className="text-sm font-bold text-foreground">
          {formatNumber(totalPlays)}
        </span>
      </div>
    </div>
  );
}
