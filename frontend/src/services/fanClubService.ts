import { apiClient } from './apiClient';

export interface FanClub {
  id: string;
  artist_user_id: string;
  artist_name: string;
  name: string;
  description: string;
  cover_image_url?: string;
  member_count: number;
  is_member?: boolean;
  created_at: string;
}

export interface FanClubTier {
  id: string;
  fan_club_id: string;
  name: string;
  description: string;
  price_monthly: number;
  benefits: string[];
  is_subscribed?: boolean;
}

export interface FanClubPost {
  id: string;
  fan_club_id: string;
  artist_name: string;
  content: string;
  media_url?: string;
  tier_id?: string;
  like_count: number;
  comment_count: number;
  is_liked?: boolean;
  created_at: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  fan_club_id: string;
  tier_id: string;
  tier_name: string;
  price_monthly: number;
  status: 'active' | 'cancelled' | 'expired';
  current_period_start: string;
  current_period_end: string;
  cancel_at_period_end: boolean;
}

class FanClubService {
  private readonly baseUrl = '/fan-clubs';

  async getFanClubs(params: {
    search?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<{ fan_clubs: FanClub[]; total: number }> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getFanClubById(id: string): Promise<FanClub> {
    const response = await apiClient.get(`${this.baseUrl}/${id}`);
    return response.data;
  }

  async createFanClub(data: {
    name: string;
    description: string;
    cover_image_url?: string;
  }): Promise<FanClub> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async updateFanClub(
    id: string,
    data: Partial<{ name: string; description: string; cover_image_url: string }>
  ): Promise<FanClub> {
    const response = await apiClient.put(`${this.baseUrl}/${id}`, data);
    return response.data;
  }

  async getTiers(fanClubId: string): Promise<FanClubTier[]> {
    const response = await apiClient.get(`${this.baseUrl}/${fanClubId}/tiers`);
    return response.data.tiers;
  }

  async createTier(
    fanClubId: string,
    data: {
      name: string;
      description: string;
      price_monthly: number;
      benefits: string[];
    }
  ): Promise<FanClubTier> {
    const response = await apiClient.post(`${this.baseUrl}/${fanClubId}/tiers`, data);
    return response.data;
  }

  async subscribe(fanClubId: string, tierId: string): Promise<Subscription> {
    const response = await apiClient.post(`${this.baseUrl}/${fanClubId}/subscribe`, {
      tier_id: tierId,
    });
    return response.data;
  }

  async unsubscribe(fanClubId: string): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${fanClubId}/unsubscribe`);
  }

  async getMySubscriptions(): Promise<Subscription[]> {
    const response = await apiClient.get(`${this.baseUrl}/my-subscriptions`);
    return response.data.subscriptions;
  }

  async getPosts(
    fanClubId: string,
    params: { page?: number; page_size?: number } = {}
  ): Promise<{ posts: FanClubPost[]; total: number }> {
    const response = await apiClient.get(`${this.baseUrl}/${fanClubId}/posts`, { params });
    return response.data;
  }

  async createPost(
    fanClubId: string,
    data: {
      content: string;
      media_url?: string;
      tier_id?: string;
    }
  ): Promise<FanClubPost> {
    const response = await apiClient.post(`${this.baseUrl}/${fanClubId}/posts`, data);
    return response.data;
  }

  async likePost(postId: string): Promise<void> {
    await apiClient.post(`${this.baseUrl}/posts/${postId}/like`);
  }

  async unlikePost(postId: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/posts/${postId}/like`);
  }
}

export const fanClubService = new FanClubService();
