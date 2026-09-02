import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { campaignService, CreateCampaignData, UpdateCampaignData, CampaignFilters } from '@/services/campaignService';
import { toast } from 'sonner';

/**
 * Hook to fetch campaigns with filters
 */
export function useCampaigns(filters?: CampaignFilters) {
  return useQuery({
    queryKey: ['campaigns', filters],
    queryFn: () => campaignService.getCampaigns(filters),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

/**
 * Hook to fetch a single campaign
 */
export function useCampaign(id: number) {
  return useQuery({
    queryKey: ['campaigns', id],
    queryFn: () => campaignService.getCampaign(id),
    enabled: !!id,
  });
}

/**
 * Hook to create a new campaign
 */
export function useCreateCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: CreateCampaignData) => campaignService.createCampaign(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      toast.success('Campaign created successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to create campaign');
    },
  });
}

/**
 * Hook to update a campaign
 */
export function useUpdateCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: UpdateCampaignData }) =>
      campaignService.updateCampaign(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaigns', variables.id] });
      toast.success('Campaign updated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to update campaign');
    },
  });
}

/**
 * Hook to delete a campaign
 */
export function useDeleteCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => campaignService.deleteCampaign(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      toast.success('Campaign deleted successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to delete campaign');
    },
  });
}

/**
 * Hook to start a campaign
 */
export function useStartCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => campaignService.startCampaign(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaigns', id] });
      toast.success('Campaign started!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to start campaign');
    },
  });
}

/**
 * Hook to pause a campaign
 */
export function usePauseCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => campaignService.pauseCampaign(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaigns', id] });
      toast.success('Campaign paused!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to pause campaign');
    },
  });
}

/**
 * Hook to complete a campaign
 */
export function useCompleteCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => campaignService.completeCampaign(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaigns', id] });
      toast.success('Campaign completed!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to complete campaign');
    },
  });
}

/**
 * Hook to generate AI content for a campaign
 */
export function useGenerateCampaignContent() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, platform }: { id: number; platform: string }) =>
      campaignService.generateContent(id, platform),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns', variables.id] });
      toast.success('Content generated successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to generate content');
    },
  });
}

/**
 * Hook to get campaign analytics
 */
export function useCampaignAnalytics(id: number) {
  return useQuery({
    queryKey: ['campaigns', id, 'analytics'],
    queryFn: () => campaignService.getCampaignAnalytics(id),
    enabled: !!id,
  });
}

/**
 * Hook to publish a campaign
 */
export function usePublishCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, platforms }: { id: number; platforms?: string[] }) =>
      campaignService.publishCampaign(id, platforms),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['campaigns'] });
      queryClient.invalidateQueries({ queryKey: ['campaigns', variables.id] });
      toast.success('Campaign published successfully!');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Failed to publish campaign');
    },
  });
}
