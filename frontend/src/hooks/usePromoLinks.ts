import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { promoLinkService, CreatePromoLinkData } from '@/services/promoLinkService';
import { toast } from 'sonner';

/**
 * Hook to fetch all promo links
 */
export function usePromoLinks() {
  return useQuery({
    queryKey: ['promo-links'],
    queryFn: () => promoLinkService.getPromoLinks(),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch a single promo link
 */
export function usePromoLink(id: number) {
  return useQuery({
    queryKey: ['promo-links', id],
    queryFn: () => promoLinkService.getPromoLink(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a promo link
 */
export function useCreatePromoLink() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreatePromoLinkData) => promoLinkService.createPromoLink(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['promo-links'] });
      toast.success('Promo link created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create promo link');
    },
  });
}

/**
 * Hook to delete a promo link
 */
export function useDeletePromoLink() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => promoLinkService.deletePromoLink(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['promo-links'] });
      toast.success('Promo link deleted!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to delete promo link');
    },
  });
}

/**
 * Hook to toggle promo link status
 */
export function useTogglePromoLink() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, isActive }: { id: number; isActive: boolean }) =>
      promoLinkService.togglePromoLink(id, isActive),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['promo-links'] });
      toast.success('Promo link updated!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update promo link');
    },
  });
}

/**
 * Hook to get promo link analytics
 */
export function usePromoLinkAnalytics(id: number) {
  return useQuery({
    queryKey: ['promo-links', id, 'analytics'],
    queryFn: () => promoLinkService.getPromoLinkAnalytics(id),
    enabled: !!id,
  });
}
