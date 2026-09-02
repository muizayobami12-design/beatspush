import { apiClient } from '@/lib/api/client';

export interface PromoLink {
  id: number;
  userId: number;
  trackId?: number;
  title: string;
  description?: string;
  shortUrl: string;
  fullUrl: string;
  qrCode?: string;
  clicks: number;
  isActive: boolean;
  expiresAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreatePromoLinkData {
  trackId?: number;
  title: string;
  description?: string;
  expiresAt?: string;
}

class PromoLinkService {
  /**
   * Get all promo links for the current user
   */
  async getPromoLinks() {
    const response = await apiClient.get('/promo-links');
    // Backend might return {links: [], total: 0} or just array
    // Ensure we always return an array
    return response.data?.links || response.data || [];
  }

  /**
   * Get a single promo link by ID
   */
  async getPromoLink(id: number) {
    const response = await apiClient.get(`/promo-links/${id}`);
    return response.data;
  }

  /**
   * Create a new promo link
   */
  async createPromoLink(data: CreatePromoLinkData) {
    const response = await apiClient.post('/promo-links', data);
    return response.data;
  }

  /**
   * Delete a promo link
   */
  async deletePromoLink(id: number) {
    const response = await apiClient.delete(`/promo-links/${id}`);
    return response.data;
  }

  /**
   * Get click analytics for a promo link
   */
  async getPromoLinkAnalytics(id: number) {
    const response = await apiClient.get(`/promo-links/${id}/analytics`);
    return response.data;
  }

  /**
   * Toggle promo link active status
   */
  async togglePromoLink(id: number, isActive: boolean) {
    const response = await apiClient.put(`/promo-links/${id}`, { isActive });
    return response.data;
  }
}

export const promoLinkService = new PromoLinkService();
