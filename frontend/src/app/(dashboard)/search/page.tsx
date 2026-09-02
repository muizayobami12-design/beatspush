'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Search, SlidersHorizontal, X } from 'lucide-react';
import { GlobalSearchBar } from '@/components/features/search/GlobalSearchBar';
import { AdvancedFilters } from '@/components/features/search/AdvancedFilters';
import { BeatGrid } from '@/components/features/beats/BeatGrid';
import { Button } from '@/components/ui/button';
import { searchService, type SearchFilters } from '@/services/searchService';
import type { Beat } from '@/types';

function SearchPageContent() {
  const searchParams = useSearchParams();
  const query = searchParams.get('q') || '';
  
  const [beats, setBeats] = useState<Beat[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    query,
    sortBy: 'relevance',
  });

  // Update filters when URL query changes
  useEffect(() => {
    if (query) {
      setFilters(prev => ({ ...prev, query }));
    }
  }, [query]);

  // Fetch search results
  useEffect(() => {
    const fetchResults = async () => {
      if (!filters.query) return;
      
      setIsLoading(true);
      try {
        const results = await searchService.searchBeats(filters);
        setBeats(results.beats);
        setTotal(results.total);
      } catch (error) {
        console.error('Search failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchResults();
  }, [filters]);

  const handleFiltersChange = (newFilters: SearchFilters) => {
    setFilters({ ...newFilters, query: filters.query });
  };

  const activeFilterCount = 
    (filters.genres?.length || 0) +
    (filters.moods?.length || 0) +
    (filters.keys?.length || 0) +
    (filters.bpmMin ? 1 : 0) +
    (filters.bpmMax ? 1 : 0) +
    (filters.priceMin ? 1 : 0) +
    (filters.priceMax ? 1 : 0);

  return (
    <div className="min-h-screen bg-background">
      {/* Header with Search */}
      <div className="border-b bg-card sticky top-0 z-40">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center gap-4">
            <div className="flex-1">
              <GlobalSearchBar />
            </div>
            <Button
              variant={showFilters ? 'default' : 'outline'}
              size="lg"
              onClick={() => setShowFilters(!showFilters)}
              className="gap-2"
            >
              <SlidersHorizontal className="h-5 w-5" />
              Filters
              {activeFilterCount > 0 && (
                <span className="ml-1 px-2 py-0.5 rounded-full bg-primary-foreground text-primary text-xs font-semibold">
                  {activeFilterCount}
                </span>
              )}
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Search Query Display */}
        {query && (
          <div className="mb-6">
            <h1 className="text-3xl font-bold mb-2">
              Search Results for "{query}"
            </h1>
            <p className="text-muted-foreground">
              {isLoading ? (
                'Searching...'
              ) : (
                `Found ${total.toLocaleString()} ${total === 1 ? 'result' : 'results'}`
              )}
            </p>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          {showFilters && (
            <div className="lg:col-span-1">
              <div className="sticky top-24">
                <AdvancedFilters
                  filters={filters}
                  onChange={handleFiltersChange}
                  onClose={() => setShowFilters(false)}
                />
              </div>
            </div>
          )}

          {/* Results */}
          <div className={showFilters ? 'lg:col-span-3' : 'lg:col-span-4'}>
            {/* Active Filters Display */}
            {activeFilterCount > 0 && (
              <div className="mb-6 flex flex-wrap gap-2">
                {filters.genres?.map((genre) => (
                  <FilterChip
                    key={genre}
                    label={genre}
                    onRemove={() => {
                      setFilters({
                        ...filters,
                        genres: filters.genres?.filter(g => g !== genre),
                      });
                    }}
                  />
                ))}
                {filters.moods?.map((mood) => (
                  <FilterChip
                    key={mood}
                    label={mood}
                    onRemove={() => {
                      setFilters({
                        ...filters,
                        moods: filters.moods?.filter(m => m !== mood),
                      });
                    }}
                  />
                ))}
                {filters.keys?.map((key) => (
                  <FilterChip
                    key={key}
                    label={`Key: ${key}`}
                    onRemove={() => {
                      setFilters({
                        ...filters,
                        keys: filters.keys?.filter(k => k !== key),
                      });
                    }}
                  />
                ))}
                {(filters.bpmMin || filters.bpmMax) && (
                  <FilterChip
                    label={`BPM: ${filters.bpmMin || '0'}-${filters.bpmMax || '∞'}`}
                    onRemove={() => {
                      setFilters({
                        ...filters,
                        bpmMin: undefined,
                        bpmMax: undefined,
                      });
                    }}
                  />
                )}
                {(filters.priceMin || filters.priceMax) && (
                  <FilterChip
                    label={`Price: ₦${filters.priceMin || '0'}-₦${filters.priceMax || '∞'}`}
                    onRemove={() => {
                      setFilters({
                        ...filters,
                        priceMin: undefined,
                        priceMax: undefined,
                      });
                    }}
                  />
                )}
              </div>
            )}

            {/* Results Grid */}
            {!query ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="p-4 rounded-full bg-muted mb-4">
                  <Search className="h-12 w-12 text-muted-foreground" />
                </div>
                <h3 className="text-xl font-semibold mb-2">Start Searching</h3>
                <p className="text-muted-foreground max-w-md">
                  Use the search bar above to find beats, tracks, and artists
                </p>
              </div>
            ) : isLoading ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((i) => (
                  <div key={i} className="h-96 bg-muted rounded-lg animate-pulse" />
                ))}
              </div>
            ) : beats.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="p-4 rounded-full bg-muted mb-4">
                  <Search className="h-12 w-12 text-muted-foreground" />
                </div>
                <h3 className="text-xl font-semibold mb-2">No Results Found</h3>
                <p className="text-muted-foreground max-w-md mb-4">
                  We couldn't find any beats matching "{query}"
                </p>
                <Button
                  onClick={() => {
                    setFilters({ query, sortBy: 'relevance' });
                  }}
                >
                  Clear Filters
                </Button>
              </div>
            ) : (
              <BeatGrid filters={{}} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function FilterChip({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium">
      <span>{label}</span>
      <button
        onClick={onRemove}
        className="hover:bg-primary/20 rounded-full p-0.5 transition-colors"
      >
        <X className="h-3 w-3" />
      </button>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="p-8">Loading search...</div>}>
      <SearchPageContent />
    </Suspense>
  );
}
