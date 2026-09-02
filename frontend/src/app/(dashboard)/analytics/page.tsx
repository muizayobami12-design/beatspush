'use client';

import { TrendingUp, Users, Music, DollarSign, Eye, Heart, Download, Filter, Calendar, BarChart3, Loader2 } from 'lucide-react';
import { useState, useMemo } from 'react';
import { StatsCard } from '@/components/features/analytics/StatsCard';
import { PlaysChart } from '@/components/features/analytics/PlaysChart';
import { TopBeatsChart } from '@/components/features/analytics/TopBeatsChart';
import { RevenueChart } from '@/components/features/analytics/RevenueChart';
import { AudienceChart } from '@/components/features/analytics/AudienceChart';
import { RevenueBreakdownCard } from '@/components/features/analytics/RevenueBreakdownCard';
import { AudienceInsights } from '@/components/features/analytics/AudienceInsights';
import { TopPerforming } from '@/components/features/analytics/TopPerforming';
import { GrowthIndicator } from '@/components/features/analytics/GrowthIndicator';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/useToast';

export default function AnalyticsPage() {
  console.log('AnalyticsPage: Rendering');

  const { toast } = useToast();
  const [dateRange, setDateRange] = useState<'week' | 'month' | 'year' | 'custom'>('month');
  const [selectedMetrics, setSelectedMetrics] = useState({
    plays: true,
    revenue: true,
    followers: true,
    likes: true,
  });
  const [isExporting, setIsExporting] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedGenres, setSelectedGenres] = useState<string[]>([]);
  const [minPlays, setMinPlays] = useState(0);
  
  // Mock data - will be replaced with real API data
  const stats = [
    {
      title: 'Total Plays',
      value: '12,543',
      change: { value: 12.5, label: 'from last month' },
      icon: Eye,
      trend: 'up' as const,
    },
    {
      title: 'Followers',
      value: '3,421',
      change: { value: 8.2, label: 'from last month' },
      icon: Users,
      trend: 'up' as const,
    },
    {
      title: 'Beats Sold',
      value: '47',
      change: { value: 23.1, label: 'from last month' },
      icon: Music,
      trend: 'up' as const,
    },
    {
      title: 'Revenue',
      value: '$2,350',
      change: { value: 18.4, label: 'from last month' },
      icon: DollarSign,
      trend: 'up' as const,
    },
    {
      title: 'Favorites',
      value: '1,892',
      change: { value: 5.3, label: 'from last month' },
      icon: Heart,
      trend: 'up' as const,
    },
    {
      title: 'Engagement',
      value: '34.2%',
      change: { value: -2.1, label: 'from last month' },
      icon: TrendingUp,
      trend: 'down' as const,
    },
  ];

  // Mock chart data - will be replaced with real API data
  const playsData = [
    { date: 'Jan 1', plays: 850, uniqueListeners: 420 },
    { date: 'Jan 8', plays: 1200, uniqueListeners: 580 },
    { date: 'Jan 15', plays: 980, uniqueListeners: 490 },
    { date: 'Jan 22', plays: 1450, uniqueListeners: 720 },
    { date: 'Jan 29', plays: 1680, uniqueListeners: 840 },
    { date: 'Feb 5', plays: 1920, uniqueListeners: 960 },
    { date: 'Feb 12', plays: 2100, uniqueListeners: 1050 },
  ];

  const topBeatsData = [
    { id: '1', name: 'Sunset Vibes', plays: 2543 },
    { id: '2', name: 'Midnight Flow', plays: 2112 },
    { id: '3', name: 'Summer Breeze', plays: 1876 },
    { id: '4', name: 'City Lights', plays: 1654 },
    { id: '5', name: 'Ocean Waves', plays: 1432 },
  ];

  const revenueData = [
    { date: '2026-08-01', revenue: 850, beatsSold: 17 },
    { date: '2026-09-01', revenue: 1200, beatsSold: 24 },
    { date: '2026-10-01', revenue: 980, beatsSold: 20 },
    { date: '2026-11-01', revenue: 1450, beatsSold: 29 },
    { date: '2026-12-01', revenue: 1680, beatsSold: 34 },
    { date: '2027-01-01', revenue: 1920, beatsSold: 38 },
    { date: '2027-02-01', revenue: 2350, beatsSold: 47 },
  ];

  const audienceData = [
    { country: 'Nigeria', listeners: 3421 },
    { country: 'South Africa', listeners: 2834 },
    { country: 'Kenya', listeners: 1987 },
    { country: 'Ghana', listeners: 1543 },
    { country: 'Tanzania', listeners: 1234 },
    { country: 'Others', listeners: 2524 },
  ];

  // New: Revenue breakdown data
  const revenueBreakdownData = {
    totalRevenue: 385000, // ₦385,000
    revenueBySource: {
      beatSales: 180000, // ₦180,000 (46.8%)
      tips: 95000, // ₦95,000 (24.7%)
      subscriptions: 65000, // ₦65,000 (16.9%)
      djSubmissions: 25000, // ₦25,000 (6.5%)
      premiumMixes: 20000, // ₦20,000 (5.2%)
    },
    growth: 18.4, // 18.4% growth
  };

  // New: Audience insights data
  const audienceInsightsData = {
    totalListeners: 12543,
    uniqueListeners: 8932,
    repeatListenerRate: 42, // 42%
    avgSessionDuration: 23, // 23 minutes
    demographics: [
      { ageGroup: '18-24', percentage: 35, count: 4390 },
      { ageGroup: '25-34', percentage: 45, count: 5644 },
      { ageGroup: '35-44', percentage: 15, count: 1881 },
      { ageGroup: '45+', percentage: 5, count: 628 },
    ],
    topLocations: [
      { city: 'Lagos', state: 'Lagos State', count: 4523, percentage: 36 },
      { city: 'Abuja', state: 'FCT', count: 2108, percentage: 17 },
      { city: 'Port Harcourt', state: 'Rivers State', count: 1755, percentage: 14 },
      { city: 'Ibadan', state: 'Oyo State', count: 1380, percentage: 11 },
      { city: 'Kano', state: 'Kano State', count: 1129, percentage: 9 },
    ],
    listeningPatterns: [
      { timeOfDay: 'Morning', plays: 2500, percentage: 20 },
      { timeOfDay: 'Afternoon', plays: 3800, percentage: 30 },
      { timeOfDay: 'Evening', plays: 4500, percentage: 36 },
      { timeOfDay: 'Night', plays: 1743, percentage: 14 },
    ],
    growth: 12.5, // 12.5% growth
  };

  // New: Top performing content
  const topPerformingData = [
    {
      id: '1',
      title: 'Sunset Vibes',
      coverUrl: '', // Would be real image URL
      artist: 'You',
      plays: 2543,
      likes: 892,
      revenue: 85000,
      growth: 23.5,
      type: 'beat' as const,
    },
    {
      id: '2',
      title: 'Midnight Flow',
      coverUrl: '',
      artist: 'You',
      plays: 2112,
      likes: 745,
      revenue: 72000,
      growth: 18.2,
      type: 'beat' as const,
    },
    {
      id: '3',
      title: 'Summer Breeze',
      coverUrl: '',
      artist: 'You',
      plays: 1876,
      likes: 623,
      revenue: 58000,
      growth: 15.8,
      type: 'track' as const,
    },
    {
      id: '4',
      title: 'City Lights',
      coverUrl: '',
      artist: 'You',
      plays: 1654,
      likes: 548,
      revenue: 45000,
      growth: 12.3,
      type: 'beat' as const,
    },
    {
      id: '5',
      title: 'Ocean Waves Mix',
      coverUrl: '',
      artist: 'You',
      plays: 1432,
      likes: 487,
      revenue: 38000,
      growth: 9.7,
      type: 'mix' as const,
    },
  ];

  // Growth comparison data
  const growthData = {
    plays: { current: 12543, previous: 11156, label: 'Total Plays' },
    revenue: { current: 385000, previous: 325000, label: 'Total Revenue' },
    followers: { current: 3421, previous: 3161, label: 'Followers' },
  };

  // Export functionality
  const handleExportCSV = async () => {
    setIsExporting(true);
    try {
      // Create CSV content
      const csvContent = [
        ['Analytics Report', new Date().toLocaleDateString()],
        [],
        ['Key Metrics'],
        ['Metric', 'Value', 'Change'],
        ...stats.map((s) => [
          s.title,
          s.value,
          `${s.change.value > 0 ? '+' : ''}${s.change.value}%`,
        ]),
        [],
        ['Top Beats'],
        ['Rank', 'Beat Name', 'Plays'],
        ...topBeatsData.map((b, i) => [i + 1, b.name, b.plays]),
        [],
        ['Revenue Data'],
        ['Month', 'Revenue', 'Beats Sold'],
        ...revenueData.map((r) => [
          new Date(r.date).toLocaleDateString(),
          `₦${r.revenue.toLocaleString()}`,
          r.beatsSold,
        ]),
        [],
        ['Audience by Country'],
        ['Country', 'Listeners'],
        ...audienceData.map((a) => [a.country, a.listeners]),
      ]
        .map((row) => row.join(','))
        .join('\n');

      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Success',
        description: 'Analytics report exported as CSV',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to export report',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  const handleExportJSON = async () => {
    setIsExporting(true);
    try {
      const reportData = {
        generatedAt: new Date().toISOString(),
        dateRange,
        stats,
        topBeats: topBeatsData,
        revenue: revenueData,
        audience: audienceData,
        growthMetrics: growthData,
      };

      const blob = new Blob([JSON.stringify(reportData, null, 2)], {
        type: 'application/json',
      });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics-report-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Success',
        description: 'Analytics report exported as JSON',
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to export report',
        variant: 'destructive',
      });
    } finally {
      setIsExporting(false);
    }
  };

  const filteredTopBeats = useMemo(() => {
    return topBeatsData.filter((beat) => beat.plays >= minPlays);
  }, [minPlays]);

  const genres = ['Afrobeat', 'Hip Hop', 'Electronic', 'R&B', 'Pop', 'Jazz', 'Rock'];

  const toggleGenre = (genre: string) => {
    setSelectedGenres((prev) =>
      prev.includes(genre) ? prev.filter((g) => g !== genre) : [...prev, genre]
    );
  };

  const toggleMetric = (metric: keyof typeof selectedMetrics) => {
    setSelectedMetrics((prev) => ({
      ...prev,
      [metric]: !prev[metric],
    }));
  };

  return (
    <div className="container mx-auto px-4 py-8 space-y-8">
      {/* Header with Export and Filter Controls */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight bg-gradient-to-r from-purple-500 via-pink-500 to-cyan-500 bg-clip-text text-transparent">
            Analytics Dashboard
          </h1>
          <p className="text-muted-foreground mt-2">
            Track your performance, reach, and revenue in real-time
          </p>
        </div>

        <div className="flex gap-2 flex-wrap justify-end">
          <Button
            variant="outline"
            size="sm"
            className="gap-2"
            onClick={() => setShowFilters(!showFilters)}
          >
            <Filter className="w-4 h-4" />
            Filters
          </Button>

          <div className="relative group">
            <Button
              variant="outline"
              size="sm"
              className="gap-2"
              disabled={isExporting}
            >
              {isExporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Exporting...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Export
                </>
              )}
            </Button>

            {!isExporting && (
              <div className="absolute top-full right-0 mt-2 bg-card border border-border rounded-lg shadow-lg opacity-0 group-hover:opacity-100 pointer-events-none group-hover:pointer-events-auto z-10 transition-opacity">
                <button
                  onClick={handleExportCSV}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-800 text-sm text-gray-300 hover:text-white first:rounded-t-lg"
                >
                  Export as CSV
                </button>
                <button
                  onClick={handleExportJSON}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-800 text-sm text-gray-300 hover:text-white last:rounded-b-lg"
                >
                  Export as JSON
                </button>
              </div>
            )}
          </div>

          <select
            value={dateRange}
            onChange={(e) => setDateRange(e.target.value as any)}
            className="px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white text-sm focus:outline-none focus:border-purple-500"
          >
            <option value="week">Last 7 days</option>
            <option value="month">Last 30 days</option>
            <option value="year">Last 12 months</option>
            <option value="custom">Custom Range</option>
          </select>
        </div>
      </div>

      {/* Advanced Filters */}
      {showFilters && (
        <div className="bg-card rounded-lg border border-border p-6 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Metric Selection */}
            <div>
              <h3 className="text-sm font-semibold text-white mb-3">Show Metrics</h3>
              <div className="space-y-2">
                {Object.entries(selectedMetrics).map(([key, value]) => (
                  <label
                    key={key}
                    className="flex items-center gap-2 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={value}
                      onChange={() =>
                        toggleMetric(key as keyof typeof selectedMetrics)
                      }
                      className="w-4 h-4 rounded border-gray-600 bg-gray-800 text-purple-600"
                    />
                    <span className="text-sm text-gray-300 capitalize">{key}</span>
                  </label>
                ))}
              </div>
            </div>

            {/* Genre Filter */}
            <div>
              <h3 className="text-sm font-semibold text-white mb-3">Genres</h3>
              <div className="flex flex-wrap gap-2">
                {genres.map((genre) => (
                  <button
                    key={genre}
                    onClick={() => toggleGenre(genre)}
                    className={`px-3 py-1 rounded-full border text-xs font-medium transition ${
                      selectedGenres.includes(genre)
                        ? 'bg-purple-600 border-purple-600 text-white'
                        : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-purple-500'
                    }`}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            </div>

            {/* Min Plays Filter */}
            <div>
              <h3 className="text-sm font-semibold text-white mb-3">
                Minimum Plays: {minPlays}
              </h3>
              <input
                type="range"
                min={0}
                max={5000}
                step={100}
                value={minPlays}
                onChange={(e) => setMinPlays(Number(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
              />
              <p className="text-xs text-gray-400 mt-2">
                Showing {filteredTopBeats.length} of {topBeatsData.length} beats
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats
          .filter((stat) => {
            if (stat.title === 'Total Plays' && !selectedMetrics.plays) return false;
            if (stat.title === 'Revenue' && !selectedMetrics.revenue) return false;
            if (stat.title === 'Followers' && !selectedMetrics.followers) return false;
            if (stat.title === 'Favorites' && !selectedMetrics.likes) return false;
            return true;
          })
          .map((stat) => (
            <StatsCard key={stat.title} {...stat} />
          ))}
      </div>

      {/* Growth Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {selectedMetrics.plays && (
          <div className="bg-card rounded-xl border p-6">
            <GrowthIndicator data={growthData.plays} format="number" />
          </div>
        )}
        {selectedMetrics.revenue && (
          <div className="bg-card rounded-xl border p-6">
            <GrowthIndicator data={growthData.revenue} format="currency" />
          </div>
        )}
        {selectedMetrics.followers && (
          <div className="bg-card rounded-xl border p-6">
            <GrowthIndicator data={growthData.followers} format="number" />
          </div>
        )}
      </div>

      {/* Revenue Breakdown & Top Performing - Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {selectedMetrics.revenue && (
          <RevenueBreakdownCard
            totalRevenue={revenueBreakdownData.totalRevenue}
            revenueBySource={revenueBreakdownData.revenueBySource}
            growth={revenueBreakdownData.growth}
            period="month"
          />
        )}
        <TopPerforming
          content={topPerformingData.filter((item) =>
            selectedGenres.length === 0 ||
            selectedGenres.includes('All') ||
            true // In real app, check genre
          )}
          period="month"
        />
      </div>

      {/* Charts */}
      <div className="space-y-6">
        {/* Plays Chart - Full Width */}
        {selectedMetrics.plays && <PlaysChart data={playsData} />}

        {/* Revenue and Audience Insights - Side by Side */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {selectedMetrics.revenue && <RevenueChart data={revenueData} />}
          <AudienceInsights
            totalListeners={audienceInsightsData.totalListeners}
            uniqueListeners={audienceInsightsData.uniqueListeners}
            repeatListenerRate={audienceInsightsData.repeatListenerRate}
            avgSessionDuration={audienceInsightsData.avgSessionDuration}
            demographics={audienceInsightsData.demographics}
            topLocations={audienceInsightsData.topLocations}
            listeningPatterns={audienceInsightsData.listeningPatterns}
            growth={audienceInsightsData.growth}
          />
        </div>

        {/* Legacy Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TopBeatsChart
            data={filteredTopBeats.length > 0 ? filteredTopBeats : topBeatsData}
          />
          <AudienceChart data={audienceData} />
        </div>
      </div>
    </div>
  );
}
