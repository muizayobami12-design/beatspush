'use client';

import { Users, MapPin, Clock, Repeat, TrendingUp } from 'lucide-react';
import { useMemo } from 'react';

interface DemographicData {
  ageGroup: string;
  percentage: number;
  count: number;
}

interface LocationData {
  city: string;
  state: string;
  count: number;
  percentage: number;
}

interface ListeningPattern {
  timeOfDay: string;
  plays: number;
  percentage: number;
}

interface AudienceInsightsProps {
  totalListeners: number;
  uniqueListeners: number;
  repeatListenerRate: number;
  avgSessionDuration: number; // in minutes
  demographics: DemographicData[];
  topLocations: LocationData[];
  listeningPatterns: ListeningPattern[];
  growth: number; // percentage
}

export function AudienceInsights({
  totalListeners,
  uniqueListeners,
  repeatListenerRate,
  avgSessionDuration,
  demographics,
  topLocations,
  listeningPatterns,
  growth,
}: AudienceInsightsProps) {
  // Find peak listening time
  const peakListeningTime = useMemo(() => {
    return listeningPatterns.reduce((max, pattern) =>
      pattern.plays > max.plays ? pattern : max
    );
  }, [listeningPatterns]);

  // Format duration
  const formatDuration = (minutes: number) => {
    if (minutes < 60) {
      return `${Math.round(minutes)}m`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = Math.round(minutes % 60);
    return `${hours}h ${mins}m`;
  };

  // Format number
  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('en-US').format(num);
  };

  return (
    <div className="bg-card rounded-xl border p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold mb-1">Audience Insights</h3>
          <p className="text-sm text-muted-foreground">
            Understand who's listening to your music
          </p>
        </div>
        <div className="p-3 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-500">
          <Users className="h-6 w-6 text-white" />
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 gap-4">
        {/* Total Listeners */}
        <div className="p-4 rounded-lg bg-gradient-to-br from-purple-500/10 to-pink-500/10 border border-purple-500/20">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-4 w-4 text-purple-500" />
            <span className="text-xs font-medium text-muted-foreground">Total Listeners</span>
          </div>
          <div className="text-2xl font-bold">{formatNumber(totalListeners)}</div>
          <div className="flex items-center gap-1 mt-1 text-xs text-green-600 dark:text-green-400">
            <TrendingUp className="h-3 w-3" />
            <span>+{growth}% growth</span>
          </div>
        </div>

        {/* Unique Listeners */}
        <div className="p-4 rounded-lg bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20">
          <div className="flex items-center gap-2 mb-2">
            <Users className="h-4 w-4 text-cyan-500" />
            <span className="text-xs font-medium text-muted-foreground">Unique</span>
          </div>
          <div className="text-2xl font-bold">{formatNumber(uniqueListeners)}</div>
          <div className="text-xs text-muted-foreground mt-1">
            {((uniqueListeners / totalListeners) * 100).toFixed(1)}% of total
          </div>
        </div>

        {/* Repeat Listener Rate */}
        <div className="p-4 rounded-lg bg-gradient-to-br from-orange-500/10 to-amber-500/10 border border-orange-500/20">
          <div className="flex items-center gap-2 mb-2">
            <Repeat className="h-4 w-4 text-orange-500" />
            <span className="text-xs font-medium text-muted-foreground">Repeat Rate</span>
          </div>
          <div className="text-2xl font-bold">{repeatListenerRate}%</div>
          <div className="text-xs text-muted-foreground mt-1">
            Come back for more
          </div>
        </div>

        {/* Avg Session Duration */}
        <div className="p-4 rounded-lg bg-gradient-to-br from-green-500/10 to-emerald-500/10 border border-green-500/20">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-green-500" />
            <span className="text-xs font-medium text-muted-foreground">Avg Session</span>
          </div>
          <div className="text-2xl font-bold">{formatDuration(avgSessionDuration)}</div>
          <div className="text-xs text-muted-foreground mt-1">
            Per listening session
          </div>
        </div>
      </div>

      {/* Demographics */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <Users className="h-4 w-4" />
          Age Demographics
        </h4>
        {demographics.map((demo) => (
          <div key={demo.ageGroup} className="space-y-1">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">{demo.ageGroup}</span>
              <span className="font-medium">{demo.percentage}%</span>
            </div>
            <div className="relative w-full h-2 bg-muted rounded-full overflow-hidden">
              <div
                className="absolute top-0 left-0 h-full bg-gradient-to-r from-purple-500 to-pink-500 transition-all duration-500"
                style={{ width: `${demo.percentage}%` }}
              />
            </div>
          </div>
        ))}
      </div>

      {/* Top Locations */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <MapPin className="h-4 w-4" />
          Top Locations
        </h4>
        <div className="space-y-2">
          {topLocations.slice(0, 5).map((location, index) => (
            <div
              key={`${location.city}-${location.state}`}
              className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              <div className="flex items-center gap-3">
                <div className="flex items-center justify-center w-6 h-6 rounded-full bg-primary/20 text-primary text-xs font-semibold">
                  {index + 1}
                </div>
                <div>
                  <div className="text-sm font-medium">{location.city}</div>
                  <div className="text-xs text-muted-foreground">{location.state}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="text-sm font-semibold">{formatNumber(location.count)}</div>
                <div className="text-xs text-muted-foreground">{location.percentage}%</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Listening Patterns */}
      <div className="space-y-3">
        <h4 className="text-sm font-semibold flex items-center gap-2">
          <Clock className="h-4 w-4" />
          Peak Listening Time
        </h4>
        <div className="p-4 rounded-lg bg-gradient-to-br from-cyan-500/10 to-blue-500/10 border border-cyan-500/20">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-2xl font-bold">{peakListeningTime.timeOfDay}</div>
              <div className="text-sm text-muted-foreground">Best time to release</div>
            </div>
            <Clock className="h-8 w-8 text-cyan-500" />
          </div>
          <div className="grid grid-cols-4 gap-2">
            {listeningPatterns.map((pattern) => (
              <div
                key={pattern.timeOfDay}
                className="text-center p-2 rounded bg-background/50"
              >
                <div className="text-xs text-muted-foreground mb-1">
                  {pattern.timeOfDay}
                </div>
                <div className="relative w-full h-16 bg-muted rounded overflow-hidden">
                  <div
                    className={`absolute bottom-0 left-0 w-full bg-gradient-to-t transition-all duration-500 ${
                      pattern.timeOfDay === peakListeningTime.timeOfDay
                        ? 'from-cyan-500 to-blue-500'
                        : 'from-purple-500 to-pink-500'
                    }`}
                    style={{ height: `${pattern.percentage}%` }}
                  />
                </div>
                <div className="text-xs font-medium mt-1">
                  {formatNumber(pattern.plays)}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
