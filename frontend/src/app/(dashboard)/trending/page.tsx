'use client';

import { useState, useMemo } from 'react';
import { TrendingUp, Zap, Music, Play, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { BeatCard } from '@/components/features/beats/BeatCard';
import { useTrendingBeats, useBeatCategories } from '@/hooks/useBeatQueries';
import { useApiError } from '@/hooks/useApiError';
import { cn } from '@/lib/utils';

type TimeRange = 'daily' | 'weekly' | 'monthly' | 'alltime';

export default function TrendingPage() {
  const [timeRange, setTimeRange] = useState<TimeRange>('daily');
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const { handleError } = useApiError();

  // Fetch trending beats from API
  const {
    data: beatsData = [],
    isLoading,
    error,
  } = useTrendingBeats(timeRange, 50, selectedGenre || undefined);

  // Fetch categories for genre filter
  const { data: categoriesData = [] } = useBeatCategories();

  // Handle errors
  if (error) {
    handleError(error, { customMessage: 'Failed to load trending beats. Please try again.' });
  }

  // Add rank to beats based on their position
  const beatsWithRank = useMemo(() => {
    return beatsData.map((beat, idx) => ({
      ...beat,
      rank: idx + 1,
    }));
  }, [beatsData]);

  const getTimeRangeLabel = (range: TimeRange): string => {
    const labels: Record<TimeRange, string> = {
      daily: 'Last 24 Hours',
      weekly: 'Last 7 Days',
      monthly: 'Last 30 Days',
      alltime: 'All Time',
    };
    return labels[range];
  };

  return (
    <div className="min-h-screen bg-background pb-8">
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        {/* Header */}
        <div className="mb-stack-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className={cn(
              'p-3 rounded-lg',
              'bg-surface-container border border-outline-variant/20'
            )}>
              <TrendingUp className="h-6 w-6 text-secondary" />
            </div>
            <div>
              <h1 className={cn(
                'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
                'text-on-surface'
              )}>
                Trending
              </h1>
              <p className={cn(
                'font-body-md text-body-md',
                'text-on-surface-variant'
              )}>
                Top beats {getTimeRangeLabel(timeRange).toLowerCase()}
              </p>
            </div>
          </div>
        </div>

        {/* Time Range Tabs */}
        <div className={cn(
          'flex gap-2 mb-stack-lg overflow-x-auto pb-2',
          'border-b border-outline-variant/20'
        )}>
          {(['daily', 'weekly', 'monthly', 'alltime'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={cn(
                'px-4 py-2 rounded-lg font-label-md text-label-md whitespace-nowrap',
                'transition-all border border-outline-variant/30',
                timeRange === range
                  ? 'bg-secondary text-on-secondary border-secondary'
                  : 'bg-surface-container-low hover:bg-surface-container text-on-surface'
              )}
            >
              {getTimeRangeLabel(range)}
            </button>
          ))}
        </div>

        {/* Controls */}
        <div className={cn(
          'rounded-lg border ghost-border p-stack-md mb-stack-lg',
          'bg-surface-container-low space-y-4'
        )}>
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            {/* Genre Filter */}
            <div className="flex-1 w-full">
              <p className={cn(
                'font-label-sm text-label-sm uppercase tracking-wider mb-3',
                'text-on-surface-variant'
              )}>
                Filter by Genre
              </p>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setSelectedGenre(null)}
                  className={cn(
                    'px-3 py-2 rounded-lg font-label-sm text-label-sm border transition-all',
                    !selectedGenre
                      ? 'bg-secondary text-on-secondary border-secondary'
                      : 'bg-surface-container border-outline-variant/30 text-on-surface hover:border-outline-variant/60'
                  )}
                >
                  All Genres
                </button>
                {categoriesData.map((genre) => (
                  <button
                    key={genre}
                    onClick={() => setSelectedGenre(genre)}
                    className={cn(
                      'px-3 py-2 rounded-lg font-label-sm text-label-sm border transition-all',
                      selectedGenre === genre
                        ? 'bg-secondary text-on-secondary border-secondary'
                        : 'bg-surface-container border-outline-variant/30 text-on-surface hover:border-outline-variant/60'
                    )}
                  >
                    {genre}
                  </button>
                ))}
              </div>
            </div>

            {/* View Mode Toggle */}
            <div className="flex items-center gap-2">
              <button
                onClick={() => setViewMode('grid')}
                className={cn(
                  'p-2 rounded-lg border transition-all',
                  viewMode === 'grid'
                    ? 'bg-secondary text-on-secondary border-secondary'
                    : 'bg-surface-container border-outline-variant/30 text-on-surface-variant hover:text-on-surface'
                )}
              >
                <Zap className="h-4 w-4" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={cn(
                  'p-2 rounded-lg border transition-all',
                  viewMode === 'list'
                    ? 'bg-secondary text-on-secondary border-secondary'
                    : 'bg-surface-container border-outline-variant/30 text-on-surface-variant hover:text-on-surface'
                )}
              >
                <Music className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Beats Display */}
        {isLoading ? (
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low flex flex-col items-center justify-center min-h-64'
          )}>
            <Loader2 className="h-8 w-8 text-secondary animate-spin mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              Loading trending beats...
            </p>
          </div>
        ) : beatsWithRank.length > 0 ? (
          <>
            {/* Stats */}
            <p className={cn(
              'font-body-md text-body-md mb-stack-md',
              'text-on-surface-variant'
            )}>
              Showing {beatsWithRank.length} beat{beatsWithRank.length !== 1 ? 's' : ''}
            </p>

            {viewMode === 'grid' ? (
              /* Grid View */
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-gutter">
                {beatsWithRank.map((beat) => (
                  <div key={beat.id} className="relative">
                    {/* Rank Badge */}
                    {beat.rank && (
                      <div
                        className={cn(
                          'absolute top-3 right-3 z-10',
                          'w-8 h-8 rounded-full',
                          'flex items-center justify-center',
                          'bg-secondary text-on-secondary',
                          'font-label-sm font-bold'
                        )}
                      >
                        #{beat.rank}
                      </div>
                    )}
                    <BeatCard
                      id={beat.id}
                      title={beat.title}
                      artist={beat.artist_name}
                      genre={beat.genre}
                      plays={beat.plays}
                      price={beat.price}
                    />
                  </div>
                ))}
              </div>
            ) : (
              /* List View */
              <div className={cn(
                'rounded-lg border ghost-border overflow-hidden',
                'bg-surface-container'
              )}>
                {beatsWithRank.map((beat, idx) => (
                  <div
                    key={beat.id}
                    className={cn(
                      'flex items-center gap-4 p-stack-md',
                      idx !== beatsWithRank.length - 1 && 'border-b border-outline-variant/20'
                    )}
                  >
                    {/* Rank */}
                    {beat.rank && (
                      <div
                        className={cn(
                          'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
                          'bg-secondary/20 text-secondary',
                          'font-label-md font-bold'
                        )}
                      >
                        #{beat.rank}
                      </div>
                    )}

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <h3 className={cn(
                        'font-body-md text-body-md',
                        'text-on-surface truncate'
                      )}>
                        {beat.title}
                      </h3>
                      <p className={cn(
                        'font-body-sm text-body-sm',
                        'text-on-surface-variant truncate'
                      )}>
                        {beat.artist_name}
                      </p>
                    </div>

                    {/* Stats */}
                    <div className="flex items-center gap-6 flex-shrink-0">
                      <div className="text-right">
                        <p className={cn(
                          'font-body-sm text-body-sm',
                          'text-on-surface-variant'
                        )}>
                          Plays
                        </p>
                        <p className={cn(
                          'font-label-md text-label-md',
                          'text-on-surface font-bold'
                        )}>
                          {(beat.plays / 1000).toFixed(1)}K
                        </p>
                      </div>

                      <div className="text-right">
                        <p className={cn(
                          'font-body-sm text-body-sm',
                          'text-on-surface-variant'
                        )}>
                          Favorites
                        </p>
                        <p className={cn(
                          'font-label-md text-label-md',
                          'text-secondary font-bold'
                        )}>
                          {beat.favorites}
                        </p>
                      </div>

                      {/* Action */}
                      <Button size="sm" variant="default" className="gap-2">
                        <Play className="h-4 w-4" />
                        <span className="hidden md:inline">Listen</span>
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        ) : (
          /* Empty State */
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <Music className="h-12 w-12 text-on-surface-variant/50 mx-auto mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              No trending beats found for this selection
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
