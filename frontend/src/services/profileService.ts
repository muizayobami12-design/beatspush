import { apiClient } from '@/lib/api/client';
import type { Profile } from '@/types';

export interface UpdateProfileData {
  fullName?: string;
  bio?: string;
  location?: string;
  website?: string;
  socialLinks?: {
    twitter?: string;
    instagram?: string;
    facebook?: string;
    youtube?: string;
    spotify?: string;
    soundcloud?: string;
  };
}

export interface ProfileResponse {
  profile: Profile;
}

class ProfileService {
  /**
   * Get profile by username
   */
  async getProfile(username: string): Promise<Profile> {
    const response = await apiClient.get<ProfileResponse>(`/profiles/${username}`);
    return response.data.profile;
  }

  /**
   * Update current user's profile
   */
  async updateProfile(data: UpdateProfileData): Promise<Profile> {
    const response = await apiClient.put<ProfileResponse>('/profiles/me', data);
    return response.data.profile;
  }

  /**
   * Upload avatar image
   */
  async uploadAvatar(file: File): Promise<Profile> {
    const formData = new FormData();
    formData.append('avatar', file);

    const response = await apiClient.post<ProfileResponse>(
      '/profiles/avatar',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.profile;
  }

  /**
   * Upload cover photo
   */
  async uploadCoverPhoto(file: File): Promise<Profile> {
    const formData = new FormData();
    formData.append('cover', file);

    const response = await apiClient.post<ProfileResponse>(
      '/profiles/cover',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data.profile;
  }

  /**
   * Follow a user
   */
  async followUser(username: string): Promise<void> {
    await apiClient.post(`/profiles/${username}/follow`);
  }

  /**
   * Unfollow a user
   */
  async unfollowUser(username: string): Promise<void> {
    await apiClient.delete(`/profiles/${username}/follow`);
  }

  /**
   * Get user's followers
   */
  async getFollowers(username: string, page = 1, limit = 20): Promise<Profile[]> {
    const response = await apiClient.get<{ followers: Profile[] }>(
      `/profiles/${username}/followers`,
      {
        params: { page, limit },
      }
    );
    return response.data.followers;
  }

  /**
   * Get users that the user is following
   */
  async getFollowing(username: string, page = 1, limit = 20): Promise<Profile[]> {
    const response = await apiClient.get<{ following: Profile[] }>(
      `/profiles/${username}/following`,
      {
        params: { page, limit },
      }
    );
    return response.data.following;
  }
}

export const profileService = new ProfileService();
