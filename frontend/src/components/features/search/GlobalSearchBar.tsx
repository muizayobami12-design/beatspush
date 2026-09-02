'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { Search, X, Clock, TrendingUp, Loader2 } from 'lucide-react';
import { searchService } from '@/services/searchService';
import { cn } from '@/lib/utils';

interface GlobalSearchBarProps {
  placeholder?: string;
  className?: string;
  autoFocus?: boolean;
}

export function GlobalSearchBar({ 
  placeholder = 'Search beats, artists, tracks...',
  className,
  autoFocus = false,
}: GlobalSearchBarProps) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Load recent searches on mount
  useEffect(() => {
    setRecentSearches(searchService.getRecentSearches());
  }, []);

  // Fetch suggestions when query changes
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (query.length >= 2) {
        setIsLoading(true);
        const results = await searchService.getSuggestions(query);
        setSuggestions(results);
        setIsLoading(false);
      } else {
        setSuggestions([]);
      }
    };

    const debounce = setTimeout(fetchSuggestions, 300);
    return () => clearTimeout(debounce);
  }, [query]);

  // Handle keyboard shortcuts (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
        setIsOpen(true);
      }
      if (e.key === 'Escape') {
        setIsOpen(false);
        inputRef.current?.blur();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(e.target as Node) &&
        !inputRef.current?.contains(e.target as Node)
      ) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (searchQuery: string) => {
    if (!searchQuery.trim()) return;

    searchService.saveRecentSearch(searchQuery);
    setRecentSearches(searchService.getRecentSearches());
    router.push(`/search?q=${encodeURIComponent(searchQuery)}`);
    setIsOpen(false);
    setQuery('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleSearch(query);
  };

  const handleClear = () => {
    setQuery('');
    setSuggestions([]);
    inputRef.current?.focus();
  };

  const handleClearRecent = () => {
    searchService.clearRecentSearches();
    setRecentSearches([]);
  };

  const showDropdown = isOpen && (suggestions.length > 0 || recentSearches.length > 0 || query.length >= 2);

  return (
    <div className={cn('relative', className)}>
      {/* Search Input */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-primary transition-colors" />
          
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => setIsOpen(true)}
            placeholder={placeholder}
            autoFocus={autoFocus}
            className={cn(
              'w-full h-11 pl-10 pr-24 rounded-lg border bg-background',
              'focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary',
              'transition-all duration-200',
              'placeholder:text-muted-foreground'
            )}
          />

          {/* Keyboard Shortcut Hint */}
          {!query && (
            <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 text-xs text-muted-foreground">
              <kbd className="px-2 py-1 rounded bg-muted font-mono">
                {typeof navigator !== 'undefined' && navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}
              </kbd>
              <kbd className="px-2 py-1 rounded bg-muted font-mono">K</kbd>
            </div>
          )}

          {/* Clear Button */}
          {query && (
            <button
              type="button"
              onClick={handleClear}
              className="absolute right-3 top-1/2 -translate-y-1/2 p-1 rounded-md hover:bg-muted transition-colors"
            >
              <X className="h-4 w-4 text-muted-foreground" />
            </button>
          )}

          {/* Loading Spinner */}
          {isLoading && (
            <div className="absolute right-12 top-1/2 -translate-y-1/2">
              <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
            </div>
          )}
        </div>
      </form>

      {/* Dropdown */}
      {showDropdown && (
        <div
          ref={dropdownRef}
          className="absolute top-full left-0 right-0 mt-2 bg-card border rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto"
        >
          {/* Suggestions */}
          {suggestions.length > 0 && (
            <div className="p-2">
              <div className="flex items-center gap-2 px-3 py-2 text-xs font-semibold text-muted-foreground">
                <TrendingUp className="h-4 w-4" />
                Suggestions
              </div>
              {suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => handleSearch(suggestion)}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted transition-colors text-left"
                >
                  <Search className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <span className="flex-1 truncate">{suggestion}</span>
                </button>
              ))}
            </div>
          )}

          {/* Recent Searches */}
          {query.length === 0 && recentSearches.length > 0 && (
            <div className="p-2 border-t">
              <div className="flex items-center justify-between px-3 py-2">
                <div className="flex items-center gap-2 text-xs font-semibold text-muted-foreground">
                  <Clock className="h-4 w-4" />
                  Recent Searches
                </div>
                <button
                  onClick={handleClearRecent}
                  className="text-xs text-muted-foreground hover:text-foreground transition-colors"
                >
                  Clear
                </button>
              </div>
              {recentSearches.map((recent, index) => (
                <button
                  key={index}
                  onClick={() => handleSearch(recent)}
                  className="w-full flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted transition-colors text-left group"
                >
                  <Clock className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <span className="flex-1 truncate">{recent}</span>
                  <X 
                    className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity"
                    onClick={(e) => {
                      e.stopPropagation();
                      const updated = recentSearches.filter((_, i) => i !== index);
                      localStorage.setItem('recent_searches', JSON.stringify(updated));
                      setRecentSearches(updated);
                    }}
                  />
                </button>
              ))}
            </div>
          )}

          {/* No Results */}
          {query.length >= 2 && suggestions.length === 0 && !isLoading && (
            <div className="p-8 text-center text-muted-foreground">
              <p className="text-sm">No suggestions found for "{query}"</p>
              <p className="text-xs mt-1">Press Enter to search anyway</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
