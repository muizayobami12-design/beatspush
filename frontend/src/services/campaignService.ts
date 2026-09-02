import { apiClient } from '@/lib/api/client';

export interface Campaign {
  id: number;
  userId: number;
  trackId?: number;
  name: string;
  description?: string;
  platforms: string[];
  status: 'draft' | 'scheduled' | 'active' | 'completed' | 'paused';
  scheduledFor?: string;
  startedAt?: string;
  completedAt?: string;
  contentType: 'new_release' | 'promo' | 'announcement' | 'engagement' | 'custom';
  generatedContent?: Record<string, any>;
  stats?: {
    reach?: number;
    engagement?: number;
    clicks?: number;
    shares?: number;
  };
  createdAt: string;
  updatedAt: string;
}

export interface CreateCampaignData {
  trackId?: number;
  name: string;
  description?: string;
  platforms: string[];
  contentType: 'new_release' | 'promo' | 'announcement' | 'engagement' | 'custom';
  scheduledFor?: string;
  customContent?: Record<string, any>;
}

export interface UpdateCampaignData {
  name?: string;
  description?: string;
  platforms?: string[];
  status?: 'draft' | 'scheduled' | 'active' | 'completed' | 'paused';
  scheduledFor?: string;
  customContent?: Record<string, any>;
}

export interface CampaignFilters {
  status?: string;
  platform?: string;
  contentType?: string;
  search?: string;
  page?: number;
  limit?: number;
}

class CampaignService {
  /**
   * Get all campaigns for the current user
   */
  async getCampaigns(filters?: CampaignFilters) {
    const params = new URLSearchParams();
    if (filters?.status) params.append('status', filters.status);
    if (filters?.platform) params.append('platform', filters.platform);
    if (filters?.contentType) params.append('content_type', filters.contentType);
    if (filters?.search) params.append('search', filters.search);
    if (filters?.page) params.append('page', filters.page.toString());
    if (filters?.limit) params.append('limit', filters.limit.toString());

    const response = await apiClient.get(`/campaigns?${params.toString()}`);
    // Backend returns {campaigns: [], total: 0, ...}
    // Return just the campaigns array
    return response.data?.campaigns || [];
  }

  /**
   * Get a single campaign by ID
   */
  async getCampaign(id: number) {
    const response = await apiClient.get(`/campaigns/${id}`);
    return response.data;
  }

  /**
   * Create a new campaign
   */
  async createCampaign(data: CreateCampaignData) {
    const response = await apiClient.post('/campaigns', data);
    return response.data;
  }

  /**
   * Update an existing campaign
   */
  async updateCampaign(id: number, data: UpdateCampaignData) {
    const response = await apiClient.put(`/campaigns/${id}`, data);
    return response.data;
  }

  /**
   * Delete a campaign
   */
  async deleteCampaign(id: number) {
    const response = await apiClient.delete(`/campaigns/${id}`);
    return response.data;
  }

  /**
   * Start a campaign (change status to active)
   */
  async startCampaign(id: number) {
    const response = await apiClient.post(`/campaigns/${id}/start`);
    return response.data;
  }

  /**
   * Pause a campaign
   */
  async pauseCampaign(id: number) {
    const response = await apiClient.post(`/campaigns/${id}/pause`);
    return response.data;
  }

  /**
   * Complete a campaign
   */
  async completeCampaign(id: number) {
    const response = await apiClient.post(`/campaigns/${id}/complete`);
    return response.data;
  }

  /**
   * Generate AI content for a campaign
   */
  async generateContent(id: number, platform: string) {
    const response = await apiClient.post(`/campaigns/${id}/generate-content`, {
      platform,
    });
    return response.data;
  }

  /**
   * Get campaign analytics
   */
  async getCampaignAnalytics(id: number) {
    const response = await apiClient.get(`/campaigns/${id}/analytics`);
    return response.data;
  }

  /**
   * Publish campaign content to platforms
   */
  async publishCampaign(id: number, platforms?: string[]) {
    const response = await apiClient.post(`/campaigns/${id}/publish`, {
      platforms,
    });
    return response.data;
  }
}

export const campaignService = new CampaignService();
