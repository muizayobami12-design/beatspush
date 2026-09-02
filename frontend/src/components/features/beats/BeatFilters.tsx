'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams, usePathname } from 'next/navigation';
import { Search, SlidersHorizontal, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { BeatFilters as BeatFiltersType } from '@/types';

// ─── Constants ───────────────────────────────────────────────────────────────

const GENRES = [
  'Afrobeat',
  'Hip Hop',
  'Trap',
  'R&B',
  'Drill',
  'Amapiano',
  'Gospel',
  'Pop',
  'Dancehall',
  'Reggae',
  'Highlife',
  'Fuji',
];

const MUSICAL_KEYS = [
  'C major', 'C minor',
  'C# major', 'C# minor',
  'D major', 'D minor',
  'Eb major', 'Eb minor',
  'E major', 'E minor',
  'F major', 'F minor',
  'F# major', 'F# minor',
  'G major', 'G minor',
  'Ab major', 'Ab minor',
  'A major', 'A minor',
  'Bb major', 'Bb minor',
  'B major', 'B minor',
];

const SORT_OPTIONS = [
  { value: 'newest', label: 'Newest First' },
  { value: 'popular', label: 'Most Popular' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
];

// ─── Helpers ─────────────────────────────────────────────────────────────────

function paramsToFilters(params: URLSearchParams): Partial<BeatFiltersType> {
  return {
    search: params.get('search') || undefined,
    genre: params.getAll('genre').length > 0 ? params.getAll('genre') : undefined,
    key: params.get('key') || undefined,
    sortBy: (params.get('sortBy') as BeatFiltersType['sortBy']) || 'newest',
    tempoMin: params.get('tempoMin') ? Number(params.get('tempoMin')) : undefined,
    tempoMax: params.get('tempoMax') ? Number(params.get('tempoMax')) : undefined,
    priceMin: params.get('priceMin') ? Number(params.get('priceMin')) : undefined,
    priceMax: params.get('priceMax') ? Number(params.get('priceMax')) : undefined,
  };
}

function filtersToParams(filters: Partial<BeatFiltersType>): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.search) params.set('search', filters.search);
  if (filters.genre?.length) filters.genre.forEach((g) => params.append('genre', g));
  if (filters.key) params.set('key', filters.key);
  if (filters.sortBy && filters.sortBy !== 'newest') params.set('sortBy', filters.sortBy);
  if (filters.tempoMin != null) params.set('tempoMin', String(filters.tempoMin));
  if (filters.tempoMax != null) params.set('tempoMax', String(filters.tempoMax));
  if (filters.priceMin != null) params.set('priceMin', String(filters.priceMin));
  if (filters.priceMax != null) params.set('priceMax', String(filters.priceMax));
  return params;
}

// ─── Component ───────────────────────────────────────────────────────────────

interface BeatFiltersProps {
  filters: Partial<BeatFiltersType>;
  onFiltersChange: (filters: Partial<BeatFiltersType>) => void;
}

export function BeatFilters({ filters, onFiltersChange }: BeatFiltersProps) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const [showAdvanced, setShowAdvanced] = useState(false);
  // Local search state so we can debounce before applying
  const [searchInput, setSearchInput] = useState(filters.search || '');

  // Sync from URL on mount
  useEffect(() => {
    const fromUrl = paramsToFilters(searchParams);
    // Only apply if something is actually set in the URL
    const hasUrlFilters = searchParams.toString().length > 0;
    if (hasUrlFilters) {
      onFiltersChange(fromUrl);
      if (fromUrl.search) setSearchInput(fromUrl.search);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Push filter changes into the URL (for shareability / back-button)
  const pushToUrl = useCallback(
    (newFilters: Partial<BeatFiltersType>) => {
      const params = filtersToParams(newFilters);
      const query = params.toString();
      router.replace(`${pathname}${query ? `?${query}` : ''}`, { scroll: false });
    },
    [router, pathname]
  );

  const applyFilters = useCallback(
    (newFilters: Partial<BeatFiltersType>) => {
      onFiltersChange(newFilters);
      pushToUrl(newFilters);
    },
    [onFiltersChange, pushToUrl]
  );

  // Debounce search input (300 ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      if (searchInput !== (filters.search ?? '')) {
        applyFilters({ ...filters, search: searchInput || undefined });
      }
    }, 300);
    return () => clearTimeout(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchInput]);

  const handleGenreToggle = (genre: string) => {
    const current = filters.genre ?? [];
    const next = current.includes(genre)
      ? current.filter((g) => g !== genre)
      : [...current, genre];
    applyFilters({ ...filters, genre: next.length > 0 ? next : undefined });
  };

  const handleKeyChange = (key: string) => {
    applyFilters({ ...filters, key: key || undefined });
  };

  const handleSortChange = (sortBy: string) => {
    applyFilters({ ...filters, sortBy: sortBy as BeatFiltersType['sortBy'] });
  };

  const handlePriceChange = (min?: number, max?: number) => {
    applyFilters({ ...filters, priceMin: min, priceMax: max });
  };

  const handleTempoChange = (min?: number, max?: number) => {
    applyFilters({ ...filters, tempoMin: min, tempoMax: max });
  };

  const clearFilters = () => {
    setSearchInput('');
    setShowAdvanced(false);
    applyFilters({ sortBy: 'newest' });
  };

  const hasActiveFilters =
    !!filters.search ||
    (filters.genre && filters.genre.length > 0) ||
    !!filters.key ||
    filters.priceMin != null ||
    filters.priceMax != null ||
    filters.tempoMin != null ||
    filters.tempoMax != null;

  return (
    <div className="space-y-4">
      {/* ── Search + Sort ── */}
      <div className="flex flex-col md:flex-row gap-4">
        {/* Search input — controlled locally, debounced */}
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
          <Input
            type="search"
            placeholder="Search beats by title, producer, or tag..."
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            className="pl-10 pr-4"
          />
        </div>

        {/* Sort dropdown + toggles */}
        <div className="flex gap-2">
          <select
            value={filters.sortBy || 'newest'}
            onChange={(e) => handleSortChange(e.target.value)}
            className="px-4 py-2 rounded-md border border-input bg-background hover:bg-accent hover:text-accent-foreground focus:outline-none focus:ring-2 focus:ring-ring text-sm"
            aria-label="Sort beats"
          >
            {SORT_OPTIONS.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>

          <Button
            variant={showAdvanced ? 'default' : 'outline'}
            size="icon"
            onClick={() => setShowAdvanced(!showAdvanced)}
            title="Advanced Filters"
            aria-expanded={showAdvanced}
            aria-label="Toggle advanced filters"
          >
            <SlidersHorizontal className="h-4 w-4" />
          </Button>

          {hasActiveFilters && (
            <Button
              variant="ghost"
              size="icon"
              onClick={clearFilters}
              title="Clear all filters"
              aria-label="Clear all filters"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* ── Genre pill filters ── */}
      <div className="flex flex-wrap gap-2" role="group" aria-label="Genre filters">
        {GENRES.map((genre) => {
          const active = filters.genre?.includes(genre) ?? false;
          return (
            <button
              key={genre}
              onClick={() => handleGenreToggle(genre)}
              aria-pressed={active}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                active
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-secondary text-secondary-foreground hover:bg-secondary/80'
              }`}
            >
              {genre}
            </button>
          );
        })}
      </div>

      {/* ── Advanced Filters ── */}
      {showAdvanced && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 rounded-lg bg-muted/50 border">
          {/* Musical Key */}
          <div>
            <label className="block text-sm font-medium mb-2" htmlFor="key-select">
              Key
            </label>
            <select
              id="key-select"
              value={filters.key || ''}
              onChange={(e) => handleKeyChange(e.target.value)}
              className="w-full px-3 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring text-sm"
            >
              <option value="">Any key</option>
              {MUSICAL_KEYS.map((k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ))}
            </select>
          </div>

          {/* Price Range */}
          <div>
            <label className="block text-sm font-medium mb-2">Price Range (₦)</label>
            <div className="flex gap-2 items-center">
              <Input
                type="number"
                placeholder="Min"
                value={filters.priceMin ?? ''}
                onChange={(e) =>
                  handlePriceChange(
                    e.target.value ? Number(e.target.value) : undefined,
                    filters.priceMax
                  )
                }
                min="0"
                aria-label="Minimum price"
              />
              <span className="text-muted-foreground">–</span>
              <Input
                type="number"
                placeholder="Max"
                value={filters.priceMax ?? ''}
                onChange={(e) =>
                  handlePriceChange(
                    filters.priceMin,
                    e.target.value ? Number(e.target.value) : undefined
                  )
                }
                min="0"
                aria-label="Maximum price"
              />
            </div>
          </div>

          {/* BPM Range */}
          <div>
            <label className="block text-sm font-medium mb-2">BPM Range</label>
            <div className="flex gap-2 items-center">
              <Input
                type="number"
                placeholder="Min"
                value={filters.tempoMin ?? ''}
                onChange={(e) =>
                  handleTempoChange(
                    e.target.value ? Number(e.target.value) : undefined,
                    filters.tempoMax
                  )
                }
                min="60"
                max="200"
                aria-label="Minimum BPM"
              />
              <span className="text-muted-foreground">–</span>
              <Input
                type="number"
                placeholder="Max"
                value={filters.tempoMax ?? ''}
                onChange={(e) =>
                  handleTempoChange(
                    filters.tempoMin,
                    e.target.value ? Number(e.target.value) : undefined
                  )
                }
                min="60"
                max="200"
                aria-label="Maximum BPM"
              />
            </div>
          </div>
        </div>
      )}

      {/* ── Active filter summary chips ── */}
      {hasActiveFilters && (
        <div className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground">
          <span>Filters:</span>
          {filters.search && (
            <span className="px-2 py-1 rounded bg-primary/10 text-primary">
              "{filters.search}"
            </span>
          )}
          {filters.genre && filters.genre.length > 0 && (
            <span className="px-2 py-1 rounded bg-primary/10 text-primary">
              {filters.genre.length} genre{filters.genre.length > 1 ? 's' : ''}
            </span>
          )}
          {filters.key && (
            <span className="px-2 py-1 rounded bg-primary/10 text-primary">
              {filters.key}
            </span>
          )}
          {(filters.priceMin != null || filters.priceMax != null) && (
            <span className="px-2 py-1 rounded bg-primary/10 text-primary">
              ₦{filters.priceMin ?? 0} – ₦{filters.priceMax ?? '∞'}
            </span>
          )}
          {(filters.tempoMin != null || filters.tempoMax != null) && (
            <span className="px-2 py-1 rounded bg-primary/10 text-primary">
              {filters.tempoMin ?? 60} – {filters.tempoMax ?? 200} BPM
            </span>
          )}
        </div>
      )}
    </div>
  );
}
