import { useState, useCallback } from 'react';

export interface SearchResult {
  id: string;
  title: string;
  category: 'beats' | 'artists' | 'playlists' | 'sounds';
  description?: string;
  metadata?: Record<string, any>;
}

interface UseSearchOptions {
  debounceMs?: number;
  minQueryLength?: number;
}

export function useSearch(options: UseSearchOptions = {}) {
  const { debounceMs = 300, minQueryLength = 1 } = options;

  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Search handler - can be customized per component
  const search = useCallback(
    async (searchQuery: string, searchFn?: (q: string) => Promise<SearchResult[]>) => {
      if (searchQuery.length < minQueryLength) {
        setResults([]);
        return;
      }

      setQuery(searchQuery);
      setIsLoading(true);
      setError(null);

      try {
        if (searchFn) {
          const searchResults = await searchFn(searchQuery);
          setResults(searchResults);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Search failed');
        setResults([]);
      } finally {
        setIsLoading(false);
      }
    },
    [minQueryLength]
  );

  const clear = useCallback(() => {
    setQuery('');
    setResults([]);
    setError(null);
  }, []);

  return {
    query,
    results,
    isLoading,
    error,
    search,
    clear,
  };
}
