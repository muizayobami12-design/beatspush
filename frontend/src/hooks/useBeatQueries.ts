/**
 * React Query hooks for beat operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  getAllBeats,
  getBeat,
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
  Beat,
  BeatsResponse,
  BeatFilters,
} from '@/services/beatService';
import { QUERY_KEYS, PAGINATION } from '@/lib/constants';

/**
 * Fetch all beats with pagination and filtering
 */
export function useBeats(
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  filters?: BeatFilters,
  search?: string
) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, page, page_size, filters, search],
    queryFn: () => getAllBeats(page, page_size, filters, search),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes (was cacheTime)
  });
}

/**
 * Fetch a single beat by ID
 */
export function useBeat(beatId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEAT, beatId],
    queryFn: () => getBeat(beatId),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Search beats
 */
export function useSearchBeats(
  query: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  filters?: BeatFilters
) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'search', query, page, filters],
    queryFn: () => getAllBeats(page, page_size, filters, query),
    enabled: query.length > 0,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch trending beats
 */
export function useTrendingBeats(
  time_range: 'daily' | 'weekly' | 'monthly' | 'alltime' = 'weekly',
  limit: number = 50,
  genre?: string
) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'trending', time_range, genre],
    queryFn: () => getTrendingBeats(time_range, limit, genre),
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Fetch beats by artist ID
 */
export function useArtistBeats(
  artistId: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  filters?: BeatFilters,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'artist', artistId, page, filters],
    queryFn: () => getArtistBeats(artistId, page, page_size, filters),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Fetch beats by multiple IDs
 */
export function useBeatsByIds(beatIds: string[]) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'batch', beatIds],
    queryFn: () => getBeatsByIds(beatIds),
    enabled: beatIds.length > 0,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Fetch similar beats
 */
export function useSimilarBeats(beatId: string, limit: number = 10, enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEAT, beatId, 'similar'],
    queryFn: () => getSimilarBeats(beatId, limit),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Fetch beat categories
 */
export function useBeatCategories() {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'categories'],
    queryFn: () => getBeatCategories(),
    staleTime: 1 * 60 * 60 * 1000, // 1 hour
    gcTime: 2 * 60 * 60 * 1000, // 2 hours
  });
}

/**
 * Fetch beat statistics
 */
export function useBeatStats() {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'stats'],
    queryFn: () => getBeatStats(),
    staleTime: 30 * 60 * 1000, // 30 minutes
    gcTime: 1 * 60 * 60 * 1000, // 1 hour
  });
}

/**
 * Fetch beat analytics (owner only)
 */
export function useBeatAnalytics(beatId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEAT, beatId, 'analytics'],
    queryFn: () => getBeatAnalytics(beatId),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Toggle beat favorite
 */
export function useToggleBeatFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (beatId: string) => toggleBeatFavorite(beatId),
    onSuccess: () => {
      // Invalidate beats and favorites queries
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS] });
    },
  });
}

/**
 * Add beat to cart
 */
export function useAddBeatToCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ beatId, licenseType }: { beatId: string; licenseType: string }) =>
      addBeatToCart(beatId, licenseType),
    onSuccess: () => {
      // Optionally invalidate cart queries
      queryClient.invalidateQueries({ queryKey: ['cart'] });
    },
  });
}

/**
 * Get beat download link
 */
export function useGetBeatDownloadLink() {
  return useMutation({
    mutationFn: ({ beatId, licenseType }: { beatId: string; licenseType: string }) =>
      getBeatDownloadLink(beatId, licenseType),
  });
}

/**
 * Report a beat
 */
export function useReportBeat() {
  return useMutation({
    mutationFn: ({
      beatId,
      reason,
      details,
    }: {
      beatId: string;
      reason: string;
      details?: string;
    }) => reportBeat(beatId, reason, details),
  });
}

/**
 * Delete a beat
 */
export function useDeleteBeat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (beatId: string) => deleteBeat(beatId),
    onSuccess: () => {
      // Invalidate artist beats and all beats queries
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS] });
    },
  });
}

/**
 * Update beat metadata
 */
export function useUpdateBeat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ beatId, data }: { beatId: string; data: Partial<Beat> }) =>
      updateBeat(beatId, data),
    onSuccess: (updatedBeat) => {
      // Update cache for this specific beat
      queryClient.setQueryData([QUERY_KEYS.BEAT, updatedBeat.id], updatedBeat);
      // Invalidate artist beats list
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'artist'] });
    },
  });
}

export default {
  useBeats,
  useBeat,
  useSearchBeats,
  useTrendingBeats,
  useArtistBeats,
  useBeatsByIds,
  useSimilarBeats,
  useBeatCategories,
  useBeatStats,
  useBeatAnalytics,
  useToggleBeatFavorite,
  useAddBeatToCart,
  useGetBeatDownloadLink,
  useReportBeat,
  useDeleteBeat,
  useUpdateBeat,
};
