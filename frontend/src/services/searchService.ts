import { apiClient } from './apiClient';
import type { Beat } from '@/types';

export interface SearchFilters {
  query?: string;
  genres?: string[];
  bpmMin?: number;
  bpmMax?: number;
  priceMin?: number;
  priceMax?: number;
  moods?: string[];
  keys?: string[];
  sortBy?: 'relevance' | 'popular' | 'newest' | 'price_asc' | 'price_desc';
  page?: number;
  pageSize?: number;
}

export interface SearchResult {
  beats: Beat[];
  artists: any[];
  tracks: any[];
  total: number;
}

export interface TrendingContent {
  id: string;
  title: string;
  type: 'beat' | 'track' | 'artist';
  coverUrl?: string;
  plays: number;
  trend: 'up' | 'hot' | 'new';
}

export interface RecommendedContent {
  id: string;
  title: string;
  type: 'beat' | 'track';
  coverUrl?: string;
  reason: string; // "Similar to X", "Based on your taste", etc.
  score: number;
}

class SearchService {
  private readonly baseUrl = '/search';

  // Global search (beats, tracks, artists)
  async globalSearch(query: string, type?: 'all' | 'beats' | 'tracks' | 'artists'): Promise<SearchResult> {
    try {
      const params = new URLSearchParams();
      params.append('q', query);
      if (type && type !== 'all') {
        params.append('type', type);
      }

      const response = await apiClient.get(`${this.baseUrl}?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Search failed:', error);
      // Return mock data for demo
      return this.getMockSearchResults(query);
    }
  }

  // Advanced beat search with filters
  async searchBeats(filters: SearchFilters): Promise<{ beats: Beat[]; total: number }> {
    try {
      const params = new URLSearchParams();
      
      if (filters.query) params.append('q', filters.query);
      if (filters.genres) filters.genres.forEach(g => params.append('genre', g));
      if (filters.bpmMin) params.append('bpm_min', filters.bpmMin.toString());
      if (filters.bpmMax) params.append('bpm_max', filters.bpmMax.toString());
      if (filters.priceMin) params.append('price_min', filters.priceMin.toString());
      if (filters.priceMax) params.append('price_max', filters.priceMax.toString());
      if (filters.moods) filters.moods.forEach(m => params.append('mood', m));
      if (filters.keys) filters.keys.forEach(k => params.append('key', k));
      if (filters.sortBy) params.append('sort', filters.sortBy);
      params.append('page', (filters.page || 1).toString());
      params.append('limit', (filters.pageSize || 20).toString());

      const response = await apiClient.get(`/beats/search?${params.toString()}`);
      return response.data;
    } catch (error) {
      console.error('Beat search failed:', error);
      return { beats: [], total: 0 };
    }
  }

  // Get search suggestions (autocomplete)
  async getSuggestions(query: string): Promise<string[]> {
    if (query.length < 2) return [];
    
    try {
      const response = await apiClient.get(`${this.baseUrl}/suggestions?q=${query}`);
      return response.data.suggestions;
    } catch (error) {
      // Return mock suggestions
      return this.getMockSuggestions(query);
    }
  }

  // Get trending content
  async getTrending(type: 'beats' | 'tracks' | 'all' = 'all'): Promise<TrendingContent[]> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/trending?type=${type}`);
      return response.data.items;
    } catch (error) {
      return this.getMockTrending();
    }
  }

  // Get recommended content
  async getRecommended(userId?: string): Promise<RecommendedContent[]> {
    try {
      const url = userId 
        ? `${this.baseUrl}/recommended?user_id=${userId}`
        : `${this.baseUrl}/recommended`;
      const response = await apiClient.get(url);
      return response.data.items;
    } catch (error) {
      return this.getMockRecommended();
    }
  }

  // Get new releases
  async getNewReleases(limit: number = 10): Promise<Beat[]> {
    try {
      const response = await apiClient.get(`/beats/new?limit=${limit}`);
      return response.data.beats;
    } catch (error) {
      return [];
    }
  }

  // Save recent search
  saveRecentSearch(query: string): void {
    const recent = this.getRecentSearches();
    const updated = [query, ...recent.filter(q => q !== query)].slice(0, 10);
    localStorage.setItem('recent_searches', JSON.stringify(updated));
  }

  // Get recent searches
  getRecentSearches(): string[] {
    try {
      const stored = localStorage.getItem('recent_searches');
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  // Clear recent searches
  clearRecentSearches(): void {
    localStorage.removeItem('recent_searches');
  }

  // Mock data for demo
  private getMockSearchResults(query: string): SearchResult {
    return {
      beats: [],
      artists: [],
      tracks: [],
      total: 0,
    };
  }

  private getMockSuggestions(query: string): string[] {
    const suggestions = [
      'afrobeat',
      'afro vibes',
      'amapiano',
      'trap beat',
      'hip hop',
      'gospel',
      'dancehall',
      'r&b',
      'highlife',
      'afro trap',
    ];
    return suggestions.filter(s => 
      s.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 5);
  }

  private getMockTrending(): TrendingContent[] {
    return [
      {
        id: '1',
        title: 'Lagos Nights',
        type: 'beat',
        plays: 12543,
        trend: 'hot',
      },
      {
        id: '2',
        title: 'Afro Vibes',
        type: 'beat',
        plays: 10234,
        trend: 'up',
      },
      {
        id: '3',
        title: 'Summer Breeze',
        type: 'track',
        plays: 8765,
        trend: 'new',
      },
    ];
  }

  private getMockRecommended(): RecommendedContent[] {
    return [
      {
        id: '1',
        title: 'Midnight Flow',
        type: 'beat',
        reason: 'Based on your listening history',
        score: 0.95,
      },
      {
        id: '2',
        title: 'City Lights',
        type: 'beat',
        reason: 'Similar to beats you liked',
        score: 0.87,
      },
    ];
  }
}

export const searchService = new SearchService();
