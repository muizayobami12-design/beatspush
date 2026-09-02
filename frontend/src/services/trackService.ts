import { apiClient } from './apiClient';

export interface Track {
  id: string;
  title: string;
  artist_user_id: string;
  artist_name: string;
  audio_url: string;
  cover_art_url?: string;
  genre: string;
  duration: number;
  is_premium: boolean;
  price?: number;
  play_count: number;
  like_count: number;
  download_count: number;
  is_liked?: boolean;
  is_purchased?: boolean;
  created_at: string;
  updated_at: string;
}

export interface TrackUploadData {
  title: string;
  description?: string;
  genre: string;
  is_premium: boolean;
  price?: number;
  audio_url: string;
  cover_art_url?: string;
  lyrics?: string;
}

class TrackService {
  private readonly baseUrl = '/tracks';

  async getTracks(params: {
    search?: string;
    genre?: string;
    page?: number;
    page_size?: number;
  } = {}): Promise<{ tracks: Track[]; total: number }> {
    const response = await apiClient.get(this.baseUrl, { params });
    return response.data;
  }

  async getTrackById(id: string): Promise<Track> {
    const response = await apiClient.get(`${this.baseUrl}/${id}`);
    return response.data;
  }

  async createTrack(data: TrackUploadData): Promise<Track> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async updateTrack(id: string, data: Partial<TrackUploadData>): Promise<Track> {
    const response = await apiClient.put(`${this.baseUrl}/${id}`, data);
    return response.data;
  }

  async deleteTrack(id: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}`);
  }

  async likeTrack(id: string): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${id}/like`);
  }

  async unlikeTrack(id: string): Promise<void> {
    await apiClient.delete(`${this.baseUrl}/${id}/like`);
  }

  async playTrack(id: string): Promise<void> {
    await apiClient.post(`${this.baseUrl}/${id}/play`);
  }

  async getMyTracks(): Promise<Track[]> {
    const response = await apiClient.get(`${this.baseUrl}/my-tracks`);
    return response.data.tracks;
  }
}

export const trackService = new TrackService();
