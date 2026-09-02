import { apiClient } from '@/lib/api/client';
import { User } from '@/types';

export interface LoginCredentials {
  email: string;
  password: string;
  device_id?: string;
  device_info?: string;
  turnstile_token?: string | null;
}

export interface RegisterData {
  email: string;
  password: string;
  full_name: string;
  role: 'artist' | 'dj' | 'producer' | 'fan' | 'admin';
  bio?: string;
  location?: string;
}

export interface AuthResponse {
  user: User;
  token: string;
  access_token?: string;
  refresh_token?: string;
  token_type?: string;
}

export const authService = {
  /**
   * Login with email and password (with security metadata)
   */
  async login(
    email: string,
    password: string,
    securityData?: {
      device_id?: string;
      device_info?: string;
      turnstile_token?: string | null;
    }
  ): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/login', {
      email,
      password,
      ...securityData,
    });

    // Normalize response to include 'token' field
    const data = response.data;
    return {
      ...data,
      token: data.token || data.access_token || '',
    };
  },

  /**
   * Register a new user
   */
  async register(data: RegisterData): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/register', data);
    // Normalize response to include 'token' field
    const responseData = response.data;
    return {
      ...responseData,
      token: responseData.token || responseData.access_token || '',
    };
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    await apiClient.post('/auth/logout');
  },

  /**
   * Get current user profile
   */
  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/auth/me');
    return response.data;
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/auth/password-reset/request',
      { email }
    );
    return response.data;
  },

  /**
   * Confirm password reset with token
   */
  async confirmPasswordReset(
    token: string,
    newPassword: string
  ): Promise<{ message: string }> {
    const response = await apiClient.post<{ message: string }>(
      '/auth/password-reset/confirm',
      { token, new_password: newPassword }
    );
    return response.data;
  },

  /**
   * Refresh access token
   */
  async refreshToken(refreshToken: string): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    });
    return response.data;
  },
};
