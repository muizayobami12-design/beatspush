/**
 * Beat Service
 * Handles all beat-related API operations
 */

import { apiClient, getErrorMessage } from '@/lib/apiClient';
import { QUERY_KEYS, PAGINATION } from '@/lib/constants';

/**
 * Beat data model
 */
export interface Beat {
  id: string;
  title: string;
  description?: string;
  artist_id: string;
  artist_name: string;
  artist_avatar?: string;
  genre: string;
  mood?: string;
  bpm?: number;
  key?: string;
  duration?: number;
  audio_url: string;
  cover_url?: string;
  plays: number;
  downloads: number;
  favorites: number;
  price: number;
  status: 'draft' | 'published' | 'archived';
  license_types: string[];
  tags?: string[];
  created_at: string;
  updated_at: string;
}

/**
 * Beat filter options
 */
export interface BeatFilters {
  genre?: string;
  mood?: string;
  min_bpm?: number;
  max_bpm?: number;
  min_price?: number;
  max_price?: number;
  sort_by?: 'trending' | 'newest' | 'popular' | 'rating';
  status?: 'draft' | 'published' | 'archived';
}

/**
 * Paginated beats response
 */
export interface BeatsResponse {
  beats: Beat[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_more: boolean;
}

/**
 * Get all beats with pagination and filtering
 */
export async function getAllBeats(
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  filters?: BeatFilters,
  search?: string
): Promise<BeatsResponse> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: Math.min(page_size, PAGINATION.MAX_PAGE_SIZE).toString(),
    });

    // Add filters
    if (filters) {
      if (filters.genre) params.append('genre', filters.genre);
      if (filters.mood) params.append('mood', filters.mood);
      if (filters.min_bpm) params.append('min_bpm', filters.min_bpm.toString());
      if (filters.max_bpm) params.append('max_bpm', filters.max_bpm.toString());
      if (filters.min_price) params.append('min_price', filters.min_price.toString());
      if (filters.max_price) params.append('max_price', filters.max_price.toString());
      if (filters.sort_by) params.append('sort_by', filters.sort_by);
      if (filters.status) params.append('status', filters.status);
    }

    // Add search
    if (search) params.append('q', search);

    const response = await apiClient.get<BeatsResponse>(`/beats?${params}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch beats:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get a single beat by ID
 */
export async function getBeat(beatId: string): Promise<Beat> {
  try {
    const response = await apiClient.get<Beat>(`/beats/${beatId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch beat ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Search beats by query
 */
export async function searchBeats(
  query: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  filters?: BeatFilters
): Promise<BeatsResponse> {
  try {
    return await getAllBeats(page, page_size, filters, query);
  } catch (error) {
    console.error('Failed to search beats:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get trending beats
 */
export async function getTrendingBeats(
  time_range: 'daily' | 'weekly' | 'monthly' | 'alltime' = 'weekly',
  limit: number = 50,
  genre?: string
): Promise<Beat[]> {
  try {
    const params = new URLSearchParams({
      time_range,
      limit: limit.toString(),
    });

    if (genre) params.append('genre', genre);

    const response = await apiClient.get<{ beats: Beat[] }>(`/beats/trending?${params}`);
    return response.data.beats;
  } catch (error) {
    console.error('Failed to fetch trending beats:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get beats by artist ID
 */
export async function getArtistBeats(
  artistId: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  filters?: BeatFilters
): Promise<BeatsResponse> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: Math.min(page_size, PAGINATION.MAX_PAGE_SIZE).toString(),
    });

    if (filters?.status) params.append('status', filters.status);
    if (filters?.sort_by) params.append('sort_by', filters.sort_by);

    const response = await apiClient.get<BeatsResponse>(`/artists/${artistId}/beats?${params}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch beats for artist ${artistId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get beats by multiple IDs
 */
export async function getBeatsByIds(beatIds: string[]): Promise<Beat[]> {
  try {
    if (beatIds.length === 0) return [];

    const response = await apiClient.post<{ beats: Beat[] }>('/beats/batch', {
      ids: beatIds,
    });
    return response.data.beats;
  } catch (error) {
    console.error('Failed to fetch beats in batch:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get similar beats based on a beat ID
 */
export async function getSimilarBeats(
  beatId: string,
  limit: number = 10
): Promise<Beat[]> {
  try {
    const response = await apiClient.get<{ beats: Beat[] }>(
      `/beats/${beatId}/similar?limit=${limit}`
    );
    return response.data.beats;
  } catch (error) {
    console.error(`Failed to fetch similar beats for ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get beat download link (for licensed beats)
 */
export async function getBeatDownloadLink(
  beatId: string,
  license_type: string
): Promise<{ download_url: string; expires_at: string }> {
  try {
    const response = await apiClient.post<{ download_url: string; expires_at: string }>(
      `/beats/${beatId}/download`,
      { license_type }
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to get download link for beat ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Favorite/unfavorite a beat
 */
export async function toggleBeatFavorite(beatId: string): Promise<{ favorited: boolean }> {
  try {
    const response = await apiClient.post<{ favorited: boolean }>(
      `/beats/${beatId}/favorite`
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to toggle favorite for beat ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Add beat to cart
 */
export async function addBeatToCart(
  beatId: string,
  license_type: string
): Promise<{ cart_id: string; item_id: string }> {
  try {
    const response = await apiClient.post<{ cart_id: string; item_id: string }>(
      '/cart/items',
      {
        beat_id: beatId,
        license_type,
      }
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to add beat ${beatId} to cart:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get beat analytics (for beat owner)
 */
export async function getBeatAnalytics(beatId: string): Promise<{
  plays: number;
  downloads: number;
  favorites: number;
  revenue: number;
  top_regions: Array<{ country: string; count: number }>;
}> {
  try {
    const response = await apiClient.get(`/beats/${beatId}/analytics`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch analytics for beat ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Report a beat
 */
export async function reportBeat(
  beatId: string,
  reason: string,
  details?: string
): Promise<{ report_id: string }> {
  try {
    const response = await apiClient.post<{ report_id: string }>(
      `/beats/${beatId}/report`,
      { reason, details }
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to report beat ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get beat categories
 */
export async function getBeatCategories(): Promise<string[]> {
  try {
    const response = await apiClient.get<{ categories: string[] }>('/beats/categories');
    return response.data.categories;
  } catch (error) {
    console.error('Failed to fetch beat categories:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get beat statistics
 */
export async function getBeatStats(): Promise<{
  total_beats: number;
  total_downloads: number;
  total_plays: number;
  featured_beats: Beat[];
}> {
  try {
    const response = await apiClient.get('/beats/stats');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch beat statistics:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Delete a beat (owner only)
 */
export async function deleteBeat(beatId: string): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.delete<{ success: boolean }>(`/beats/${beatId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to delete beat ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Update beat metadata
 */
export async function updateBeat(
  beatId: string,
  data: Partial<Beat>
): Promise<Beat> {
  try {
    const response = await apiClient.put<Beat>(`/beats/${beatId}`, data);
    return response.data;
  } catch (error) {
    console.error(`Failed to update beat ${beatId}:`, getErrorMessage(error));
    throw error;
  }
}

export default {
  getAllBeats,
  getBeat,
  searchBeats,
  getTrendingBeats,
  getArtistBeats,
  getBeatsByIds,
  getSimilarBeats,
  getBeatDownloadLink,
  toggleBeatFavorite,
  addBeatToCart,
  getBeatAnalytics,
  reportBeat,
  getBeatCategories,
  getBeatStats,
  deleteBeat,
  updateBeat,
};
