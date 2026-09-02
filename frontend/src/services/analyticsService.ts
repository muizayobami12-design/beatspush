import apiClient from './apiClient';

export interface AnalyticsDashboard {
  overview: {
    total_tracks: number;
    total_plays: number;
    total_likes: number;
    total_campaigns: number;
    plays_growth?: number;
  };
  top_tracks: Array<{
    track_id: string;
    title: string;
    plays: number;
    likes: number;
    engagement_rate: number;
  }>;
  platform_stats: Array<{
    platform: string;
    plays: number;
    unique_listeners: number;
  }>;
  geographic_stats: Array<{
    country: string;
    listeners: number;
  }>;
  engagement_timeline: {
    dates: string[];
    plays: number[];
    likes: number[];
  };
  insights: string[];
}

class AnalyticsService {
  async getDashboard(days: number = 30): Promise<AnalyticsDashboard> {
    try {
      const response = await apiClient.get(`/analytics/dashboard?days=${days}`);
      return response.data;
    } catch (error) {
      console.error('Failed to fetch analytics dashboard:', error);
      throw error;
    }
  }

  async getTrackAnalytics(trackId: string) {
    try {
      const response = await apiClient.get(`/analytics/tracks/${trackId}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch track analytics:`, error);
      throw error;
    }
  }

  async getTrackRankings() {
    try {
      const response = await apiClient.get('/analytics/tracks/rankings');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch track rankings:', error);
      throw error;
    }
  }
}

export const analyticsService = new AnalyticsService();
export default analyticsService;
