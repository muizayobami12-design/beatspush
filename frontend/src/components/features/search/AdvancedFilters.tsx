'use client';

import { useState } from 'react';
import { SlidersHorizontal, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import type { SearchFilters } from '@/services/searchService';

interface AdvancedFiltersProps {
  filters: SearchFilters;
  onChange: (filters: SearchFilters) => void;
  onClose?: () => void;
}

const GENRES = [
  'Afrobeat',
  'Amapiano',
  'Hip Hop',
  'Trap',
  'R&B',
  'Gospel',
  'Dancehall',
  'Reggae',
  'Highlife',
  'Pop',
  'Drill',
  'Afro Trap',
];

const MOODS = [
  'Energetic',
  'Chill',
  'Dark',
  'Happy',
  'Sad',
  'Aggressive',
  'Romantic',
  'Uplifting',
  'Melancholic',
  'Party',
];

const KEYS = [
  'C', 'C#', 'D', 'D#', 'E', 'F',
  'F#', 'G', 'G#', 'A', 'A#', 'B',
];

const SORT_OPTIONS = [
  { value: 'relevance', label: 'Most Relevant' },
  { value: 'popular', label: 'Most Popular' },
  { value: 'newest', label: 'Newest First' },
  { value: 'price_asc', label: 'Price: Low to High' },
  { value: 'price_desc', label: 'Price: High to Low' },
];

export function AdvancedFilters({ filters, onChange, onClose }: AdvancedFiltersProps) {
  const [localFilters, setLocalFilters] = useState<SearchFilters>(filters);

  const updateFilter = (key: keyof SearchFilters, value: any) => {
    const updated = { ...localFilters, [key]: value };
    setLocalFilters(updated);
  };

  const toggleGenre = (genre: string) => {
    const current = localFilters.genres || [];
    const updated = current.includes(genre)
      ? current.filter(g => g !== genre)
      : [...current, genre];
    updateFilter('genres', updated);
  };

  const toggleMood = (mood: string) => {
    const current = localFilters.moods || [];
    const updated = current.includes(mood)
      ? current.filter(m => m !== mood)
      : [...current, mood];
    updateFilter('moods', updated);
  };

  const toggleKey = (key: string) => {
    const current = localFilters.keys || [];
    const updated = current.includes(key)
      ? current.filter(k => k !== key)
      : [...current, key];
    updateFilter('keys', updated);
  };

  const handleApply = () => {
    onChange(localFilters);
    onClose?.();
  };

  const handleReset = () => {
    const resetFilters: SearchFilters = {
      sortBy: 'relevance',
    };
    setLocalFilters(resetFilters);
    onChange(resetFilters);
  };

  const activeFilterCount = 
    (localFilters.genres?.length || 0) +
    (localFilters.moods?.length || 0) +
    (localFilters.keys?.length || 0) +
    (localFilters.bpmMin ? 1 : 0) +
    (localFilters.bpmMax ? 1 : 0) +
    (localFilters.priceMin ? 1 : 0) +
    (localFilters.priceMax ? 1 : 0);

  return (
    <div className="bg-card rounded-lg border p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-semibold">Advanced Filters</h3>
          {activeFilterCount > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-primary text-primary-foreground text-xs font-semibold">
              {activeFilterCount}
            </span>
          )}
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-1 rounded-md hover:bg-muted transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {/* Sort By */}
      <div>
        <label className="block text-sm font-medium mb-3">Sort By</label>
        <div className="grid grid-cols-2 gap-2">
          {SORT_OPTIONS.map((option) => (
            <button
              key={option.value}
              onClick={() => updateFilter('sortBy', option.value)}
              className={cn(
                'px-4 py-2 rounded-lg border text-sm font-medium transition-all',
                localFilters.sortBy === option.value
                  ? 'bg-primary text-primary-foreground border-primary'
                  : 'bg-background hover:bg-muted border-border'
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Genre */}
      <div>
        <label className="block text-sm font-medium mb-3">
          Genre {localFilters.genres && localFilters.genres.length > 0 && (
            <span className="text-muted-foreground">({localFilters.genres.length})</span>
          )}
        </label>
        <div className="flex flex-wrap gap-2">
          {GENRES.map((genre) => (
            <button
              key={genre}
              onClick={() => toggleGenre(genre)}
              className={cn(
                'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
                localFilters.genres?.includes(genre)
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted hover:bg-muted/80 text-foreground'
              )}
            >
              {genre}
            </button>
          ))}
        </div>
      </div>

      {/* BPM Range */}
      <div>
        <label className="block text-sm font-medium mb-3">BPM Range</label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <input
              type="number"
              placeholder="Min"
              value={localFilters.bpmMin || ''}
              onChange={(e) => updateFilter('bpmMin', e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
          <div>
            <input
              type="number"
              placeholder="Max"
              value={localFilters.bpmMax || ''}
              onChange={(e) => updateFilter('bpmMax', e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
        </div>
        <div className="mt-2 flex items-center justify-between text-xs text-muted-foreground">
          <span>Typical: 60-180 BPM</span>
        </div>
      </div>

      {/* Price Range (Nigerian Naira) */}
      <div>
        <label className="block text-sm font-medium mb-3">Price Range (₦)</label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <input
              type="number"
              placeholder="Min"
              value={localFilters.priceMin || ''}
              onChange={(e) => updateFilter('priceMin', e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
          <div>
            <input
              type="number"
              placeholder="Max"
              value={localFilters.priceMax || ''}
              onChange={(e) => updateFilter('priceMax', e.target.value ? parseInt(e.target.value) : undefined)}
              className="w-full px-3 py-2 rounded-lg border bg-background focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
            />
          </div>
        </div>
      </div>

      {/* Mood */}
      <div>
        <label className="block text-sm font-medium mb-3">
          Mood {localFilters.moods && localFilters.moods.length > 0 && (
            <span className="text-muted-foreground">({localFilters.moods.length})</span>
          )}
        </label>
        <div className="flex flex-wrap gap-2">
          {MOODS.map((mood) => (
            <button
              key={mood}
              onClick={() => toggleMood(mood)}
              className={cn(
                'px-3 py-1.5 rounded-full text-sm font-medium transition-all',
                localFilters.moods?.includes(mood)
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white'
                  : 'bg-muted hover:bg-muted/80 text-foreground'
              )}
            >
              {mood}
            </button>
          ))}
        </div>
      </div>

      {/* Musical Key */}
      <div>
        <label className="block text-sm font-medium mb-3">
          Musical Key {localFilters.keys && localFilters.keys.length > 0 && (
            <span className="text-muted-foreground">({localFilters.keys.length})</span>
          )}
        </label>
        <div className="flex flex-wrap gap-2">
          {KEYS.map((key) => (
            <button
              key={key}
              onClick={() => toggleKey(key)}
              className={cn(
                'w-12 h-12 rounded-lg text-sm font-semibold transition-all',
                localFilters.keys?.includes(key)
                  ? 'bg-gradient-to-br from-cyan-500 to-blue-500 text-white'
                  : 'bg-muted hover:bg-muted/80 text-foreground'
              )}
            >
              {key}
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3 pt-4 border-t">
        <Button
          onClick={handleReset}
          variant="outline"
          className="flex-1"
          disabled={activeFilterCount === 0}
        >
          Reset All
        </Button>
        <Button
          onClick={handleApply}
          className="flex-1"
        >
          Apply Filters
        </Button>
      </div>
    </div>
  );
}
