/**
 * Notification Service - Phase 3 Implementation
 * Backend endpoints: /api/v1/notifications/*
 */

import apiClient from './apiClient';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export type NotificationType = 
  | 'new_message'
  | 'new_follower'
  | 'beat_purchase'
  | 'tip_received'
  | 'dj_submission_accepted'
  | 'dj_submission_declined'
  | 'fan_club_subscription'
  | 'comment'
  | 'like'
  | 'system';

export interface Notification {
  id: string;
  user_id: string;
  type: NotificationType;
  title: string;
  message: string;
  data?: Record<string, any>;
  read: boolean;
  created_at: string;
  read_at?: string;
}

export interface NotificationListResponse {
  notifications: Notification[];
  total: number;
  unread_count: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

// ============================================================================
// NOTIFICATION SERVICE
// ============================================================================

class NotificationService {
  
  /**
   * Get all notifications with pagination and filters
   */
  async getNotifications(params?: {
    page?: number;
    page_size?: number;
    unread_only?: boolean;
    type?: NotificationType;
  }): Promise<NotificationListResponse> {
    const response = await apiClient.get('/social/notifications', { params });
    return response.data;
  }

  /**
   * Get unread notification count
   */
  async getUnreadCount(): Promise<UnreadCountResponse> {
    const response = await apiClient.get('/social/notifications/unread-count');
    return response.data;
  }

  /**
   * Mark a single notification as read
   */
  async markAsRead(notificationId: string): Promise<void> {
    await apiClient.post(`/social/notifications/${notificationId}/read`);
  }

  /**
   * Mark a single notification as unread
   */
  async markAsUnread(notificationId: string): Promise<void> {
    await apiClient.post(`/social/notifications/${notificationId}/unread`);
  }

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<void> {
    await apiClient.post('/social/notifications/mark-all-read');
  }

  /**
   * Delete a notification
   */
  async deleteNotification(notificationId: string): Promise<void> {
    await apiClient.delete(`/social/notifications/${notificationId}`);
  }

  /**
   * Delete all read notifications
   */
  async deleteAllRead(): Promise<void> {
    await apiClient.delete('/social/notifications/read');
  }

  /**
   * Get notification preferences
   */
  async getPreferences(): Promise<{
    email_notifications: boolean;
    push_notifications: boolean;
    new_message: boolean;
    new_follower: boolean;
    beat_purchase: boolean;
    tip_received: boolean;
    dj_submission: boolean;
  }> {
    const response = await apiClient.get('/social/notifications/preferences');
    return response.data;
  }

  /**
   * Update notification preferences
   */
  async updatePreferences(preferences: {
    email_notifications?: boolean;
    push_notifications?: boolean;
    new_message?: boolean;
    new_follower?: boolean;
    beat_purchase?: boolean;
    tip_received?: boolean;
    dj_submission?: boolean;
  }): Promise<void> {
    await apiClient.put('/social/notifications/preferences', preferences);
  }
}

export default new NotificationService();
