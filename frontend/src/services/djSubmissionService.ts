import { apiClient } from './apiClient';

export interface DJ {
  id: string;
  full_name: string;
  username: string;
  avatar_url?: string;
  bio?: string;
  genres: string[];
  follower_count: number;
  submission_price: number;
  accepts_submissions: boolean;
  avg_response_time_hours: number;
  acceptance_rate: number;
  is_verified: boolean;
}

export interface DJSubmission {
  id: string;
  artist_user_id: string;
  artist_name: string;
  dj_user_id: string;
  dj_name: string;
  track_id: string;
  track_title: string;
  message?: string;
  status: 'pending' | 'accepted' | 'rejected' | 'played';
  submission_price: number;
  payment_status: string;
  dj_feedback?: string;
  created_at: string;
  responded_at?: string;
}

export interface SubmitTrackRequest {
  dj_user_id: string;
  track_id: string;
  message?: string;
}

class DJSubmissionService {
  private readonly baseUrl = '/dj-submissions';

  async getDJs(params: {
    search?: string;
    genre?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<{ djs: DJ[]; total: number }> {
    const response = await apiClient.get('/users/djs', { params });
    return response.data;
  }

  async getDJById(id: string): Promise<DJ> {
    const response = await apiClient.get(`/users/${id}`);
    return response.data;
  }

  async submitTrack(data: SubmitTrackRequest): Promise<DJSubmission> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async getMySubmissions(params: {
    status?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<{ submissions: DJSubmission[]; total: number }> {
    const response = await apiClient.get(`${this.baseUrl}/my-submissions`, { params });
    return response.data;
  }

  async getSubmissionsForDJ(params: {
    status?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<{ submissions: DJSubmission[]; total: number }> {
    const response = await apiClient.get(`${this.baseUrl}/for-me`, { params });
    return response.data;
  }

  async respondToSubmission(
    id: string,
    action: 'accept' | 'reject',
    feedback?: string
  ): Promise<DJSubmission> {
    const response = await apiClient.post(`${this.baseUrl}/${id}/respond`, {
      action,
      feedback,
    });
    return response.data;
  }

  async markAsPlayed(id: string): Promise<DJSubmission> {
    const response = await apiClient.post(`${this.baseUrl}/${id}/played`);
    return response.data;
  }
}

export const djSubmissionService = new DJSubmissionService();
