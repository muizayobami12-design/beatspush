'use client';

import { useState, useCallback, useMemo } from 'react';
import { Compass, Music, Search, Filter, TrendingUp, Star, Users, ListMusic, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { BeatCard } from '@/components/features/beats/BeatCard';
import { useBeats, useBeatCategories, useSearchBeats } from '@/hooks/useBeatQueries';
import { useApiError } from '@/hooks/useApiError';
import { cn } from '@/lib/utils';
import { PAGINATION } from '@/lib/constants';

// Placeholder categories (will be replaced with real ones from API)
const CATEGORIES = [
  { id: 'trending', icon: TrendingUp, label: 'Trending', color: 'text-secondary' },
  { id: 'new', icon: Star, label: 'New Releases', color: 'text-tertiary' },
  { id: 'artists', icon: Users, label: 'Top Artists', color: 'text-clay' },
  { id: 'playlists', icon: ListMusic, label: 'Playlists', color: 'text-secondary-fixed' },
];

export default function DiscoverPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState('trending');
  const [showFilters, setShowFilters] = useState(false);
  const [sortBy, setSortBy] = useState<'trending' | 'newest' | 'popular'>('trending');
  const [page, setPage] = useState(1);
  const { handleError } = useApiError();

  // Fetch categories
  const { data: categoriesData, isLoading: categoriesLoading } = useBeatCategories();

  // Fetch beats with current filters
  const { 
    data: beatsData, 
    isLoading: beatsLoading, 
    error: beatsError 
  } = useBeats(
    page,
    PAGINATION.DEFAULT_PAGE_SIZE,
    {
      genre: selectedGenre,
      sort_by: sortBy as any,
    },
    undefined // no search query, using fetch all
  );

  // Search beats if query exists
  const {
    data: searchData,
    isLoading: searchLoading,
    error: searchError,
  } = useSearchBeats(
    searchQuery,
    page,
    PAGINATION.DEFAULT_PAGE_SIZE,
    {
      genre: selectedGenre,
      sort_by: sortBy as any,
    }
  );

  // Handle errors
  if (beatsError) {
    handleError(beatsError, { customMessage: 'Failed to load beats. Please try again.' });
  }

  if (searchError) {
    handleError(searchError, { customMessage: 'Failed to search beats. Please try again.' });
  }

  // Use search results if search query exists, otherwise use browse results
  const beats = searchQuery && searchData ? searchData.beats : beatsData?.beats || [];
  const total = searchQuery && searchData ? searchData.total : beatsData?.total || 0;
  const hasMore = searchQuery && searchData ? searchData.has_more : beatsData?.has_more || false;
  const totalPages = searchQuery && searchData ? searchData.total_pages : beatsData?.total_pages || 1;

  const isLoading = searchQuery ? searchLoading : beatsLoading;
  const categories = categoriesData || [];

  const CategoryIcon = CATEGORIES.find(c => c.id === selectedCategory)?.icon || Music;
  const categoryColor = CATEGORIES.find(c => c.id === selectedCategory)?.color || 'text-secondary';

  const handleLoadMore = useCallback(() => {
    if (hasMore && page < totalPages) {
      setPage(page + 1);
    }
  }, [hasMore, page, totalPages]);

  const handleResetFilters = useCallback(() => {
    setSelectedGenre(null);
    setSortBy('trending');
    setPage(1);
  }, []);

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
              <Compass className={cn('h-6 w-6', categoryColor)} />
            </div>
            <div>
              <h1 className={cn(
                'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
                'text-on-surface'
              )}>
                Discover
              </h1>
              <p className={cn(
                'font-body-md text-body-md',
                'text-on-surface-variant'
              )}>
                Explore trending beats and new sounds
              </p>
            </div>
          </div>
        </div>

        {/* Category Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-gutter mb-stack-lg">
          {CATEGORIES.map((category) => {
            const Icon = category.icon;
            const isActive = selectedCategory === category.id;

            return (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={cn(
                  'p-4 rounded-lg border ghost-border transition-all duration-200',
                  'flex flex-col items-center justify-center text-center gap-2',
                  isActive
                    ? 'bg-secondary/20 border-secondary'
                    : 'bg-surface-container-low hover:bg-surface-container'
                )}
              >
                <Icon className={cn('h-6 w-6', isActive ? 'text-secondary' : 'text-on-surface-variant')} />
                <span className={cn(
                  'font-label-sm text-label-sm',
                  isActive ? 'text-secondary font-bold' : 'text-on-surface'
                )}>
                  {category.label}
                </span>
              </button>
            );
          })}
        </div>

        {/* Search & Filters */}
        <div className={cn(
          'rounded-lg border ghost-border p-stack-md mb-stack-lg',
          'bg-surface-container-low space-y-4'
        )}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-on-surface-variant" />
              <Input
                type="text"
                placeholder="Search beats, artists..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  setPage(1);
                }}
                className={cn(
                  'pl-10',
                  'bg-surface-container border border-outline-variant/30',
                  'text-on-surface placeholder-on-surface-variant/50',
                  'focus:outline-none focus:ring-2 focus:ring-secondary/40'
                )}
              />
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value as typeof sortBy);
                setPage(1);
              }}
              className={cn(
                'px-3 py-2 rounded-lg',
                'bg-surface-container border border-outline-variant/30',
                'text-on-surface font-body-md',
                'focus:outline-none focus:ring-2 focus:ring-secondary/40'
              )}
            >
              <option value="trending">Trending</option>
              <option value="newest">Newest</option>
              <option value="popular">Most Popular</option>
            </select>
          </div>

          {/* Genre Filter Toggle */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="gap-2 w-full md:w-auto"
          >
            <Filter className="h-4 w-4" />
            Filter by Genre
            {selectedGenre && (
              <span className="ml-1 text-xs">({selectedGenre})</span>
            )}
          </Button>

          {/* Genre Filter */}
          {showFilters && (
            <div className="space-y-3 pt-4 border-t border-outline-variant/20">
              <p className={cn(
                'font-label-sm text-label-sm',
                'text-on-surface-variant uppercase tracking-wider'
              )}>
                Genres
              </p>
              
              {categoriesLoading ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="h-4 w-4 animate-spin text-on-surface-variant" />
                </div>
              ) : (
                <div className="flex flex-wrap gap-2">
                  <button
                    onClick={() => {
                      setSelectedGenre(null);
                      setPage(1);
                    }}
                    className={cn(
                      'px-3 py-2 rounded-lg font-label-sm text-label-sm border transition-all',
                      !selectedGenre
                        ? 'bg-secondary text-on-secondary border-secondary'
                        : 'bg-surface-container border-outline-variant/30 text-on-surface hover:border-outline-variant/60'
                    )}
                  >
                    All Genres
                  </button>
                  {categories.map((genre) => (
                    <button
                      key={genre}
                      onClick={() => {
                        setSelectedGenre(genre);
                        setPage(1);
                      }}
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
              )}
            </div>
          )}

          {/* Active Filters Display */}
          {(selectedGenre || sortBy !== 'trending') && (
            <div className="flex items-center justify-between pt-2 border-t border-outline-variant/20">
              <div className="flex gap-2 flex-wrap">
                {selectedGenre && (
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs',
                    'bg-secondary/20 text-secondary'
                  )}>
                    Genre: {selectedGenre}
                  </span>
                )}
                {sortBy !== 'trending' && (
                  <span className={cn(
                    'px-2 py-1 rounded-full text-xs',
                    'bg-secondary/20 text-secondary'
                  )}>
                    Sort: {sortBy}
                  </span>
                )}
              </div>
              <button
                onClick={handleResetFilters}
                className={cn(
                  'text-xs font-label-xs text-secondary hover:text-secondary-dim',
                  'transition-colors'
                )}
              >
                Clear All
              </button>
            </div>
          )}
        </div>

        {/* Beats Grid */}
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
              Loading beats...
            </p>
          </div>
        ) : beats.length > 0 ? (
          <div className="space-y-stack-md">
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              Showing {beats.length} of {total} beat{total !== 1 ? 's' : ''}
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-gutter">
              {beats.map((beat) => (
                <BeatCard
                  key={beat.id}
                  id={beat.id}
                  title={beat.title}
                  artist={beat.artist_name}
                  genre={beat.genre}
                  plays={beat.plays}
                  price={beat.price}
                />
              ))}
            </div>

            {/* Load More Button */}
            {hasMore && (
              <div className="flex justify-center pt-stack-lg">
                <Button
                  onClick={handleLoadMore}
                  disabled={isLoading}
                  className="gap-2"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Load More Beats'
                  )}
                </Button>
              </div>
            )}
          </div>
        ) : (
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <Music className="h-12 w-12 text-on-surface-variant/50 mx-auto mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              {searchQuery ? 'No beats match your search' : 'No beats found. Try adjusting your filters.'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
