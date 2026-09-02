/**
 * Messaging Service - Phase 2 Implementation
 * Backend endpoints: /api/v1/messaging/*
 */

import apiClient from './apiClient';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface MessageParticipant {
  id: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  user_type?: string;
}

export interface LastMessagePreview {
  id: string;
  content: string;
  sender_id: string;
  created_at: string;
  has_attachment: boolean;
}

export interface Conversation {
  id: string;
  participants: MessageParticipant[];
  last_message?: LastMessagePreview;
  unread_count: number;
  is_message_request: boolean;
  request_status?: 'pending' | 'accepted' | 'declined';
  last_activity_at: string;
  is_archived: boolean;
  is_muted: boolean;
}

export interface MessageAttachment {
  id: string;
  file_type: 'image' | 'audio' | 'document' | 'voice_note';
  original_filename: string;
  storage_url: string;
  file_size: number;
  mime_type: string;
  duration?: number;
  width?: number;
  height?: number;
  thumbnail_url?: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender: MessageParticipant;
  content: string;
  created_at: string;
  updated_at?: string;
  is_edited: boolean;
  read_by: string[];
  attachments?: MessageAttachment[];
  deleted_at?: string;
}

export interface MessageSettings {
  id: string;
  user_id: string;
  message_filter: 'everyone' | 'followers' | 'verified' | 'none';
  read_receipts_enabled: boolean;
  typing_indicators_enabled: boolean;
}

export interface BlockedUser {
  id: string;
  blocked_user: MessageParticipant;
  reason?: string;
  blocked_at: string;
}

// ============================================================================
// API REQUESTS
// ============================================================================

export interface CreateConversationRequest {
  recipient_id: string;
}

export interface SendMessageRequest {
  recipient_id?: string;
  conversation_id?: string;
  content: string;
}

export interface UpdateMessageRequest {
  content: string;
}

export interface UpdateSettingsRequest {
  message_filter?: 'everyone' | 'followers' | 'verified' | 'none';
  read_receipts_enabled?: boolean;
  typing_indicators_enabled?: boolean;
}

export interface BlockUserRequest {
  user_id: string;
  reason?: string;
}

export interface ReportMessageRequest {
  reason: 'spam' | 'harassment' | 'inappropriate' | 'other';
  details?: string;
}

// ============================================================================
// API RESPONSES
// ============================================================================

interface ConversationListResponse {
  conversations: Conversation[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

interface MessageListResponse {
  messages: Message[];
  has_more: boolean;
  next_cursor?: string;
}

interface UnreadCountResponse {
  unread_count: number;
  total?: number;
}

interface BlockedUsersListResponse {
  blocked_users: BlockedUser[];
  total: number;
  page: number;
  page_size: number;
}

// ============================================================================
// MESSAGING SERVICE
// ============================================================================

class MessagingService {
  
  // ==========================================================================
  // CONVERSATIONS
  // ==========================================================================
  
  async listConversations(params?: {
    page?: number;
    page_size?: number;
    unread_only?: boolean;
    search?: string;
  }): Promise<ConversationListResponse> {
    const response = await apiClient.get('/messaging/conversations', { params });
    return response.data;
  }

  async createConversation(recipientId: string): Promise<Conversation> {
    const response = await apiClient.post('/messaging/conversations', {
      recipient_id: recipientId
    });
    return response.data;
  }

  async getConversation(conversationId: string): Promise<Conversation> {
    const response = await apiClient.get(`/messaging/conversations/${conversationId}`);
    return response.data;
  }

  async leaveConversation(conversationId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/messaging/conversations/${conversationId}`);
    return response.data;
  }

  // ==========================================================================
  // MESSAGES
  // ==========================================================================

  async getMessages(conversationId: string, params?: {
    page?: number;
    page_size?: number;
    cursor?: string;
  }): Promise<MessageListResponse> {
    const response = await apiClient.get(
      `/messaging/conversations/${conversationId}/messages`,
      { params }
    );
    return response.data;
  }

  async sendMessage(data: SendMessageRequest): Promise<Message> {
    const response = await apiClient.post('/messaging/messages', data);
    return response.data;
  }

  async editMessage(messageId: string, content: string): Promise<Message> {
    const response = await apiClient.put(`/messaging/messages/${messageId}`, {
      content
    });
    return response.data;
  }

  async deleteMessage(messageId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/messaging/messages/${messageId}`);
    return response.data;
  }

  async markMessageRead(messageId: string): Promise<{ message: string }> {
    const response = await apiClient.post(`/messaging/messages/${messageId}/read`);
    return response.data;
  }

  async markConversationRead(conversationId: string): Promise<{ message: string }> {
    const response = await apiClient.post(
      `/messaging/conversations/${conversationId}/mark-read`
    );
    return response.data;
  }

  async uploadAttachment(
    messageId: string,
    file: File,
    fileType: 'image' | 'audio' | 'document' | 'voice_note'
  ): Promise<{ message: string; attachment: MessageAttachment }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post(
      `/messaging/messages/${messageId}/attachments?file_type=${fileType}`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    return response.data;
  }

  async getUnreadCount(conversationId?: string): Promise<UnreadCountResponse> {
    const params = conversationId ? { conversation_id: conversationId } : {};
    const response = await apiClient.get('/messaging/unread-count', { params });
    return response.data;
  }

  // ==========================================================================
  // MESSAGE REQUESTS
  // ==========================================================================

  async listMessageRequests(params?: {
    page?: number;
    page_size?: number;
  }): Promise<ConversationListResponse> {
    const response = await apiClient.get('/messaging/message-requests', { params });
    return response.data;
  }

  async acceptMessageRequest(conversationId: string): Promise<Conversation> {
    const response = await apiClient.post(
      `/messaging/message-requests/${conversationId}/accept`
    );
    return response.data;
  }

  async declineMessageRequest(conversationId: string): Promise<{ message: string }> {
    const response = await apiClient.post(
      `/messaging/message-requests/${conversationId}/decline`
    );
    return response.data;
  }

  // ==========================================================================
  // PRIVACY & SETTINGS
  // ==========================================================================

  async getSettings(): Promise<MessageSettings> {
    const response = await apiClient.get('/messaging/settings');
    return response.data;
  }

  async updateSettings(settings: UpdateSettingsRequest): Promise<MessageSettings> {
    const response = await apiClient.put('/messaging/settings', settings);
    return response.data;
  }

  async blockUser(userId: string, reason?: string): Promise<{ message: string }> {
    const response = await apiClient.post('/messaging/block', {
      user_id: userId,
      reason
    });
    return response.data;
  }

  async unblockUser(userId: string): Promise<{ message: string }> {
    const response = await apiClient.delete(`/messaging/block/${userId}`);
    return response.data;
  }

  async getBlockedUsers(params?: {
    page?: number;
    page_size?: number;
  }): Promise<BlockedUsersListResponse> {
    const response = await apiClient.get('/messaging/blocked-users', { params });
    return response.data;
  }

  async reportMessage(
    messageId: string,
    data: ReportMessageRequest
  ): Promise<{ id: string; message: string }> {
    const response = await apiClient.post(
      `/messaging/messages/${messageId}/report`,
      data
    );
    return response.data;
  }
}

export default new MessagingService();
