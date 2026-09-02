import { useQuery, useMutation, useQueryClient, useInfiniteQuery } from '@tanstack/react-query';
import { beatService, type BeatFilters, type UploadBeatData, type UpdateBeatData } from '@/services/beatService';
import type { Beat } from '@/types';

/**
 * Hook to fetch paginated beats with filters
 */
export function useBeats(filters: BeatFilters = {}) {
  return useQuery({
    queryKey: ['beats', filters],
    queryFn: () => beatService.getBeats(filters),
  });
}

/**
 * Hook to fetch infinite scroll beats
 */
export function useInfiniteBeats(filters: Omit<BeatFilters, 'page'> = {}) {
  return useInfiniteQuery({
    queryKey: ['beats', 'infinite', filters],
    queryFn: ({ pageParam = 1 }) =>
      beatService.getBeats({ ...filters, page: pageParam }),
    getNextPageParam: (lastPage) => {
      // Calculate total pages from total and page_size
      const totalPages = Math.ceil(lastPage.total / lastPage.page_size);
      return lastPage.page < totalPages ? lastPage.page + 1 : undefined;
    },
    initialPageParam: 1,
  });
}

/**
 * Hook to fetch a single beat by ID
 */
export function useBeat(id: string) {
  return useQuery({
    queryKey: ['beat', id],
    queryFn: () => beatService.getBeatById(id),
    enabled: !!id,
  });
}

/**
 * Hook to upload a new beat
 */
export function useUploadBeat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UploadBeatData) => beatService.uploadBeat(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beats'] });
    },
  });
}

/**
 * Hook to update a beat
 */
export function useUpdateBeat(id: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateBeatData) => beatService.updateBeat(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beat', id] });
      queryClient.invalidateQueries({ queryKey: ['beats'] });
    },
  });
}

/**
 * Hook to delete a beat
 */
export function useDeleteBeat() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => beatService.deleteBeat(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['beats'] });
    },
  });
}

/**
 * Hook to favorite/unfavorite a beat with optimistic updates
 */
export function useFavoriteBeat(id: string) {
  const queryClient = useQueryClient();

  const favoriteMutation = useMutation({
    mutationFn: () => beatService.favoriteBeat(id),
    onMutate: async () => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['beat', id] });

      // Snapshot previous value
      const previousBeat = queryClient.getQueryData(['beat', id]);

      // Optimistically update
      queryClient.setQueryData(['beat', id], (old: Beat | undefined) => {
        if (!old) return old;
        return { ...old, isFavorited: true, favoriteCount: (old.favoriteCount || 0) + 1 };
      });

      return { previousBeat };
    },
    onError: (_error, _variables, context) => {
      // Rollback on error
      if (context?.previousBeat) {
        queryClient.setQueryData(['beat', id], context.previousBeat);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['beat', id] });
    },
  });

  const unfavoriteMutation = useMutation({
    mutationFn: () => beatService.unfavoriteBeat(id),
    onMutate: async () => {
      await queryClient.cancelQueries({ queryKey: ['beat', id] });

      const previousBeat = queryClient.getQueryData(['beat', id]);

      queryClient.setQueryData(['beat', id], (old: Beat | undefined) => {
        if (!old) return old;
        return { ...old, isFavorited: false, favoriteCount: Math.max(0, (old.favoriteCount || 0) - 1) };
      });

      return { previousBeat };
    },
    onError: (_error, _variables, context) => {
      if (context?.previousBeat) {
        queryClient.setQueryData(['beat', id], context.previousBeat);
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['beat', id] });
    },
  });

  return {
    favorite: favoriteMutation.mutate,
    unfavorite: unfavoriteMutation.mutate,
    isFavoriting: favoriteMutation.isPending,
    isUnfavoriting: unfavoriteMutation.isPending,
  };
}

/**
 * Hook to fetch favorite beats
 */
export function useFavoriteBeats(page = 1, limit = 20) {
  return useQuery({
    queryKey: ['beats', 'favorites', page, limit],
    queryFn: () => beatService.getFavoriteBeats(page, limit),
  });
}

/**
 * Hook to fetch beats by creator
 */
export function useBeatsByCreator(username: string, page = 1, limit = 20) {
  return useQuery({
    queryKey: ['beats', 'creator', username, page, limit],
    queryFn: () => beatService.getBeatsByCreator(username, page, limit),
    enabled: !!username,
  });
}

/**
 * Hook to purchase a beat
 */
export function usePurchaseBeat() {
  return useMutation({
    mutationFn: (id: string) => beatService.purchaseBeat(id),
    onSuccess: (data) => {
      // Redirect to payment URL
      if (data.paymentUrl) {
        window.location.href = data.paymentUrl;
      }
    },
  });
}
