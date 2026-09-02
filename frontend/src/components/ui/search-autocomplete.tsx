'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { Search, X, Clock, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

export interface SearchSuggestion {
  id: string;
  label: string;
  category: 'beats' | 'artists' | 'playlists' | 'sounds';
  icon?: React.ReactNode;
}

interface SearchAutocompleteProps {
  onSearch?: (query: string) => void;
  onSuggestionSelect?: (suggestion: SearchSuggestion) => void;
  placeholder?: string;
  className?: string;
  getSuggestions?: (query: string) => Promise<SearchSuggestion[]>;
}

const CATEGORY_COLORS = {
  beats: 'text-secondary',
  artists: 'text-tertiary',
  playlists: 'text-clay',
  sounds: 'text-secondary-fixed',
};

const CATEGORY_ICONS = {
  beats: '♪',
  artists: '👤',
  playlists: '📋',
  sounds: '🔊',
};

const RECENT_SEARCHES_KEY = 'beatspush_recent_searches';
const MAX_RECENT_SEARCHES = 5;

export function SearchAutocomplete({
  onSearch,
  onSuggestionSelect,
  placeholder = 'Search beats, artists, sounds...',
  className,
  getSuggestions,
}: SearchAutocompleteProps) {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SearchSuggestion[]>([]);
  const [recentSearches, setRecentSearches] = useState<SearchSuggestion[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout>();

  // Load recent searches from localStorage
  useEffect(() => {
    const saved = localStorage.getItem(RECENT_SEARCHES_KEY);
    if (saved) {
      try {
        setRecentSearches(JSON.parse(saved));
      } catch (e) {
        console.error('Failed to load recent searches', e);
      }
    }
  }, []);

  // Default suggestions if no custom getSuggestions provided
  const defaultGetSuggestions = useCallback(
    (q: string): SearchSuggestion[] => {
      if (!q.trim()) return [];

      const mockData: Record<string, SearchSuggestion[]> = {
        beats: [
          { id: 'beat1', label: 'Midnight Voyage', category: 'beats' },
          { id: 'beat2', label: 'Lagos Nights', category: 'beats' },
          { id: 'beat3', label: 'Heritage', category: 'beats' },
        ],
        artists: [
          { id: 'artist1', label: 'Oluwa Beats', category: 'artists' },
          { id: 'artist2', label: 'Sound Engineer', category: 'artists' },
        ],
        playlists: [
          { id: 'pl1', label: 'Afrobeats Collection', category: 'playlists' },
          { id: 'pl2', label: 'Deep House Vibes', category: 'playlists' },
        ],
        sounds: [
          { id: 'sound1', label: 'Drum Loop', category: 'sounds' },
          { id: 'sound2', label: 'Ambient Pad', category: 'sounds' },
        ],
      };

      const lowerQ = q.toLowerCase();
      const results: SearchSuggestion[] = [];

      Object.entries(mockData).forEach(([_, items]) => {
        items.forEach((item) => {
          if (item.label.toLowerCase().includes(lowerQ)) {
            results.push(item);
          }
        });
      });

      return results.slice(0, 8);
    },
    []
  );

  // Fetch suggestions with debounce
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    if (!query.trim()) {
      setSuggestions([]);
      setSelectedIndex(-1);
      return;
    }

    setIsLoading(true);
    debounceTimerRef.current = setTimeout(async () => {
      try {
        const results = getSuggestions
          ? await getSuggestions(query)
          : defaultGetSuggestions(query);
        setSuggestions(results);
        setSelectedIndex(-1);
      } catch (error) {
        console.error('Failed to fetch suggestions', error);
        setSuggestions([]);
      } finally {
        setIsLoading(false);
      }
    }, 300); // 300ms debounce

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current);
      }
    };
  }, [query, getSuggestions, defaultGetSuggestions]);

  // Handle click outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Save search to recent searches
  const saveSearch = (suggestion: SearchSuggestion) => {
    const updated = [
      suggestion,
      ...recentSearches.filter((s) => s.id !== suggestion.id),
    ].slice(0, MAX_RECENT_SEARCHES);

    setRecentSearches(updated);
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
  };

  // Handle suggestion selection
  const handleSelectSuggestion = (suggestion: SearchSuggestion) => {
    setQuery(suggestion.label);
    saveSearch(suggestion);
    onSuggestionSelect?.(suggestion);
    setIsOpen(false);
  };

  // Handle search submission
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      const suggestion: SearchSuggestion = {
        id: `search_${Date.now()}`,
        label: query,
        category: 'beats',
      };
      saveSearch(suggestion);
      onSearch?.(query);
      setIsOpen(false);
    }
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    const displaySuggestions =
      query.trim() && suggestions.length > 0 ? suggestions : recentSearches;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setIsOpen(true);
        setSelectedIndex((prev) =>
          prev < displaySuggestions.length - 1 ? prev + 1 : 0
        );
        break;

      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev > 0 ? prev - 1 : displaySuggestions.length - 1
        );
        break;

      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && displaySuggestions[selectedIndex]) {
          handleSelectSuggestion(displaySuggestions[selectedIndex]);
        } else {
          handleSearch(e as any);
        }
        break;

      case 'Escape':
        setIsOpen(false);
        setSelectedIndex(-1);
        break;

      default:
        break;
    }
  };

  // Clear search
  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    setSelectedIndex(-1);
    inputRef.current?.focus();
  };

  // Delete recent search
  const handleDeleteRecent = (id: string) => {
    const updated = recentSearches.filter((s) => s.id !== id);
    setRecentSearches(updated);
    localStorage.setItem(RECENT_SEARCHES_KEY, JSON.stringify(updated));
  };

  const displaySuggestions =
    query.trim() && suggestions.length > 0 ? suggestions : recentSearches;
  const showDropdown = isOpen && displaySuggestions.length > 0;

  // Group suggestions by category
  const groupedSuggestions = displaySuggestions.reduce(
    (acc, suggestion) => {
      if (!acc[suggestion.category]) {
        acc[suggestion.category] = [];
      }
      acc[suggestion.category].push(suggestion);
      return acc;
    },
    {} as Record<string, SearchSuggestion[]>
  );

  return (
    <div
      ref={containerRef}
      className={cn('relative w-full', className)}
      onFocus={() => setIsOpen(true)}
    >
      {/* Input Container */}
      <form
        onSubmit={handleSearch}
        className={cn(
          'relative flex items-center gap-2 px-3 py-2 rounded-lg',
          'bg-surface-container border border-outline-variant/30',
          'focus-within:ring-2 focus-within:ring-secondary/40 focus-within:border-secondary/50',
          'transition-all'
        )}
      >
        <Search className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={cn(
            'flex-1 bg-transparent outline-none',
            'text-on-surface placeholder-on-surface-variant/50',
            'font-body-md text-body-md'
          )}
          aria-label="Search"
          aria-autocomplete="list"
          aria-expanded={showDropdown}
        />

        {/* Loading indicator */}
        {isLoading && (
          <div className="flex items-center justify-center">
            <div className="h-4 w-4 rounded-full border-2 border-secondary/30 border-t-secondary animate-spin" />
          </div>
        )}

        {/* Clear button */}
        {query && (
          <button
            type="button"
            onClick={handleClear}
            className={cn(
              'p-1 rounded hover:bg-surface-container-low',
              'text-on-surface-variant hover:text-on-surface',
              'transition-colors flex-shrink-0'
            )}
            aria-label="Clear search"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </form>

      {/* Dropdown */}
      {showDropdown && (
        <div
          className={cn(
            'absolute top-full left-0 right-0 mt-2 z-50',
            'bg-surface-container border border-outline-variant/30 rounded-lg shadow-lg',
            'max-h-96 overflow-y-auto'
          )}
        >
          {Object.entries(groupedSuggestions).map(([category, items]) => (
            <div key={category}>
              {/* Category header */}
              <div className="px-3 py-2 sticky top-0 bg-surface-container-low">
                <p
                  className={cn(
                    'font-label-xs text-label-xs uppercase tracking-wider',
                    'text-on-surface-variant'
                  )}
                >
                  {category === 'beats'
                    ? '♪ Beats'
                    : category === 'artists'
                      ? '👤 Artists'
                      : category === 'playlists'
                        ? '📋 Playlists'
                        : '🔊 Sounds'}
                </p>
              </div>

              {/* Suggestions */}
              {items.map((suggestion, idx) => {
                const globalIndex = displaySuggestions.indexOf(suggestion);
                const isSelected = selectedIndex === globalIndex;
                const isRecent =
                  query.trim() === '' && recentSearches.includes(suggestion);

                return (
                  <div key={suggestion.id}>
                    <button
                      type="button"
                      onClick={() => handleSelectSuggestion(suggestion)}
                      onMouseEnter={() => setSelectedIndex(globalIndex)}
                      className={cn(
                        'w-full px-3 py-2 flex items-center gap-3 text-left',
                        'transition-colors',
                        isSelected
                          ? 'bg-secondary/20 text-secondary'
                          : 'hover:bg-surface-container-low text-on-surface'
                      )}
                    >
                      {/* Icon */}
                      <span
                        className={cn(
                          'text-base flex-shrink-0',
                          CATEGORY_COLORS[suggestion.category]
                        )}
                      >
                        {CATEGORY_ICONS[suggestion.category]}
                      </span>

                      {/* Label with highlight */}
                      <span className="flex-1 truncate font-body-sm text-body-sm">
                        {query.trim() &&
                          !isRecent &&
                          highlightMatch(suggestion.label, query)}
                        {!query.trim() || isRecent ? suggestion.label : null}
                      </span>

                      {/* Recent indicator or delete button */}
                      {isRecent ? (
                        <Clock className="h-4 w-4 text-on-surface-variant flex-shrink-0" />
                      ) : (
                        <Zap className="h-4 w-4 text-on-surface-variant/40 flex-shrink-0" />
                      )}
                    </button>

                    {/* Delete recent search on hover */}
                    {isRecent && isSelected && (
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteRecent(suggestion.id);
                        }}
                        className={cn(
                          'w-full px-3 py-2 text-left font-body-sm text-body-sm',
                          'text-destructive hover:bg-destructive/10',
                          'transition-colors'
                        )}
                      >
                        Remove from recent
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// Helper function to highlight matching text
function highlightMatch(text: string, query: string): React.ReactNode {
  if (!query) return text;

  const parts = text.split(new RegExp(`(${query})`, 'gi'));

  return parts.map((part, i) =>
    part.toLowerCase() === query.toLowerCase() ? (
      <mark key={i} className="bg-secondary/30 font-bold">
        {part}
      </mark>
    ) : (
      part
    )
  );
}
