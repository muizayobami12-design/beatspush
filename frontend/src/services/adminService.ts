import { apiClient } from '@/lib/api/client';

export interface PlatformStats {
  totalUsers: number;
  activeUsers: number;
  totalTracks: number;
  totalRevenue: number;
  newUsersToday: number;
  newUsersThisWeek: number;
  newUsersThisMonth: number;
}

export interface AdminUser {
  id: number;
  email: string;
  fullName: string;
  role: string;
  isActive: boolean;
  createdAt: string;
  lastLogin?: string;
}

class AdminService {
  /**
   * Get platform statistics
   */
  async getPlatformStats() {
    const response = await apiClient.get('/admin/stats');
    return response.data;
  }

  /**
   * Get all users
   */
  async getUsers(params?: { search?: string; role?: string; page?: number; limit?: number }) {
    const searchParams = new URLSearchParams();
    if (params?.search) searchParams.append('search', params.search);
    if (params?.role) searchParams.append('role', params.role);
    if (params?.page) searchParams.append('page', params.page.toString());
    if (params?.limit) searchParams.append('limit', params.limit.toString());

    const response = await apiClient.get(`/admin/users?${searchParams.toString()}`);
    return response.data;
  }

  /**
   * Get a single user by ID
   */
  async getUser(id: number) {
    const response = await apiClient.get(`/admin/users/${id}`);
    return response.data;
  }

  /**
   * Suspend a user
   */
  async suspendUser(id: number) {
    const response = await apiClient.post(`/admin/users/${id}/suspend`);
    return response.data;
  }

  /**
   * Activate a user
   */
  async activateUser(id: number) {
    const response = await apiClient.post(`/admin/users/${id}/activate`);
    return response.data;
  }

  /**
   * Delete a user
   */
  async deleteUser(id: number) {
    const response = await apiClient.delete(`/admin/users/${id}`);
    return response.data;
  }
}

export const adminService = new AdminService();
