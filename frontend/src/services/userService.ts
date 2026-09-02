/**
 * User Service
 * Handles all user-related API operations including authentication, profiles, and social features
 */

import { apiClient, getErrorMessage } from '@/lib/apiClient';
import { QUERY_KEYS, PAGINATION } from '@/lib/constants';

/**
 * User profile data model
 */
export interface UserProfile {
  id: string;
  username: string;
  email: string;
  full_name: string;
  bio?: string;
  avatar_url?: string;
  cover_url?: string;
  location?: string;
  website?: string;
  role: 'artist' | 'dj' | 'producer' | 'fan' | 'admin';
  is_verified: boolean;
  follower_count: number;
  following_count: number;
  beat_count: number;
  is_following?: boolean;
  is_blocked?: boolean;
  created_at: string;
  updated_at: string;
}

/**
 * User search result
 */
export interface UserSearchResult {
  id: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  role: string;
  is_verified: boolean;
  is_following?: boolean;
}

/**
 * Follow status
 */
export interface FollowStatus {
  is_following: boolean;
  follower_count: number;
  following_count: number;
}

/**
 * User statistics
 */
export interface UserStats {
  total_beats: number;
  total_plays: number;
  total_downloads: number;
  total_earnings: number;
  total_followers: number;
  total_following: number;
}

/**
 * Auth credentials
 */
export interface AuthCredentials {
  email: string;
  password: string;
}

/**
 * Auth response
 */
export interface AuthResponse {
  user: UserProfile;
  access_token: string;
  refresh_token: string;
  expires_in: number;
}

/**
 * Registration data
 */
export interface RegistrationData {
  email: string;
  password: string;
  full_name: string;
  username: string;
  role: 'artist' | 'dj' | 'producer' | 'fan';
}

/**
 * Update profile data
 */
export interface UpdateProfileData {
  full_name?: string;
  bio?: string;
  location?: string;
  website?: string;
  avatar_url?: string;
  cover_url?: string;
}

/**
 * Paginated users response
 */
export interface UsersResponse {
  users: UserSearchResult[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_more: boolean;
}

/**
 * Login user
 */
export async function loginUser(credentials: AuthCredentials): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/auth/login', credentials);
    return response.data;
  } catch (error) {
    console.error('Login failed:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Register new user
 */
export async function registerUser(data: RegistrationData): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    return response.data;
  } catch (error) {
    console.error('Registration failed:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Logout user
 */
export async function logoutUser(): Promise<void> {
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
    console.error('Logout failed:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Refresh access token
 */
export async function refreshToken(refreshToken: string): Promise<AuthResponse> {
  try {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  } catch (error) {
    console.error('Token refresh failed:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get current user profile
 */
export async function getCurrentUser(): Promise<UserProfile> {
  try {
    const response = await apiClient.get<UserProfile>('/users/me');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch current user:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get user profile by ID or username
 */
export async function getUserProfile(userIdOrUsername: string): Promise<UserProfile> {
  try {
    const response = await apiClient.get<UserProfile>(`/users/${userIdOrUsername}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch user ${userIdOrUsername}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Update current user profile
 */
export async function updateUserProfile(data: UpdateProfileData): Promise<UserProfile> {
  try {
    const response = await apiClient.patch<UserProfile>('/users/me', data);
    return response.data;
  } catch (error) {
    console.error('Failed to update profile:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Upload user avatar
 */
export async function uploadAvatar(file: File): Promise<{ avatar_url: string }> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<{ avatar_url: string }>(
      '/users/me/avatar',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to upload avatar:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Upload user cover image
 */
export async function uploadCover(file: File): Promise<{ cover_url: string }> {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<{ cover_url: string }>(
      '/users/me/cover',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to upload cover:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Search users
 */
export async function searchUsers(
  query: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE
): Promise<UsersResponse> {
  try {
    const params = new URLSearchParams({
      q: query,
      page: page.toString(),
      page_size: Math.min(page_size, PAGINATION.MAX_PAGE_SIZE).toString(),
    });

    const response = await apiClient.get<UsersResponse>(`/users/search?${params}`);
    return response.data;
  } catch (error) {
    console.error('Failed to search users:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get user followers
 */
export async function getUserFollowers(
  userId: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE
): Promise<UsersResponse> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: Math.min(page_size, PAGINATION.MAX_PAGE_SIZE).toString(),
    });

    const response = await apiClient.get<UsersResponse>(
      `/users/${userId}/followers?${params}`
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch followers for ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get user following list
 */
export async function getUserFollowing(
  userId: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE
): Promise<UsersResponse> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: Math.min(page_size, PAGINATION.MAX_PAGE_SIZE).toString(),
    });

    const response = await apiClient.get<UsersResponse>(`/users/${userId}/following?${params}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch following list for ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Follow a user
 */
export async function followUser(userId: string): Promise<FollowStatus> {
  try {
    const response = await apiClient.post<FollowStatus>(`/users/${userId}/follow`);
    return response.data;
  } catch (error) {
    console.error(`Failed to follow user ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Unfollow a user
 */
export async function unfollowUser(userId: string): Promise<FollowStatus> {
  try {
    const response = await apiClient.post<FollowStatus>(`/users/${userId}/unfollow`);
    return response.data;
  } catch (error) {
    console.error(`Failed to unfollow user ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Check if following a user
 */
export async function checkFollowStatus(userId: string): Promise<FollowStatus> {
  try {
    const response = await apiClient.get<FollowStatus>(`/users/${userId}/follow-status`);
    return response.data;
  } catch (error) {
    console.error(`Failed to check follow status for ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Block a user
 */
export async function blockUser(userId: string): Promise<{ blocked: boolean }> {
  try {
    const response = await apiClient.post<{ blocked: boolean }>(`/users/${userId}/block`);
    return response.data;
  } catch (error) {
    console.error(`Failed to block user ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Unblock a user
 */
export async function unblockUser(userId: string): Promise<{ blocked: boolean }> {
  try {
    const response = await apiClient.post<{ blocked: boolean }>(`/users/${userId}/unblock`);
    return response.data;
  } catch (error) {
    console.error(`Failed to unblock user ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get blocked users list
 */
export async function getBlockedUsers(
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE
): Promise<UsersResponse> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: Math.min(page_size, PAGINATION.MAX_PAGE_SIZE).toString(),
    });

    const response = await apiClient.get<UsersResponse>(`/users/me/blocked?${params}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch blocked users:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get user statistics
 */
export async function getUserStats(userId: string): Promise<UserStats> {
  try {
    const response = await apiClient.get<UserStats>(`/users/${userId}/stats`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch statistics for user ${userId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Change password
 */
export async function changePassword(
  oldPassword: string,
  newPassword: string
): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>(
      '/users/me/change-password',
      { old_password: oldPassword, new_password: newPassword }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to change password:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Request password reset
 */
export async function requestPasswordReset(email: string): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>('/auth/forgot-password', {
      email,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to request password reset:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Reset password with token
 */
export async function resetPassword(
  token: string,
  newPassword: string
): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>('/auth/reset-password', {
      token,
      new_password: newPassword,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to reset password:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Verify email
 */
export async function verifyEmail(token: string): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>('/auth/verify-email', {
      token,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to verify email:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Resend verification email
 */
export async function resendVerificationEmail(): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>(
      '/auth/resend-verification'
    );
    return response.data;
  } catch (error) {
    console.error('Failed to resend verification email:', getErrorMessage(error));
    throw error;
  }
}

export default {
  loginUser,
  registerUser,
  logoutUser,
  refreshToken,
  getCurrentUser,
  getUserProfile,
  updateUserProfile,
  uploadAvatar,
  uploadCover,
  searchUsers,
  getUserFollowers,
  getUserFollowing,
  followUser,
  unfollowUser,
  checkFollowStatus,
  blockUser,
  unblockUser,
  getBlockedUsers,
  getUserStats,
  changePassword,
  requestPasswordReset,
  resetPassword,
  verifyEmail,
  resendVerificationEmail,
};
