/**
 * Social Service - Comments, Likes, Follows, Shares
 * Phase 4: Social Features Implementation
 */

import apiClient from './apiClient';

// ============================================================================
// TYPES & INTERFACES
// ============================================================================

export interface Comment {
  id: string;
  user_id: string;
  content_type: 'beat' | 'track' | 'mix';
  content_id: string;
  content: string;
  parent_id?: string;
  created_at: string;
  updated_at?: string;
  user: {
    id: string;
    username: string;
    full_name: string;
    avatar_url?: string;
    user_type?: string;
  };
  replies?: Comment[];
  likes_count: number;
  is_liked?: boolean;
}

export interface Like {
  id: string;
  user_id: string;
  content_type: 'beat' | 'track' | 'mix' | 'comment';
  content_id: string;
  created_at: string;
}

export interface Follow {
  id: string;
  follower_id: string;
  following_id: string;
  created_at: string;
  follower?: {
    id: string;
    username: string;
    full_name: string;
    avatar_url?: string;
    user_type?: string;
  };
  following?: {
    id: string;
    username: string;
    full_name: string;
    avatar_url?: string;
    user_type?: string;
  };
}

// ============================================================================
// SOCIAL SERVICE
// ============================================================================

class SocialService {
  
  // ==========================================================================
  // COMMENTS
  // ==========================================================================
  
  /**
   * Get comments for content (beat, track, mix)
   */
  async getComments(params: {
    content_type: 'beat' | 'track' | 'mix';
    content_id: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    comments: Comment[];
    total: number;
    page: number;
    page_size: number;
  }> {
    const response = await apiClient.get('/social/comments', { params });
    return response.data;
  }

  /**
   * Post a comment
   */
  async postComment(data: {
    content_type: 'beat' | 'track' | 'mix';
    content_id: string;
    content: string;
    parent_id?: string;
  }): Promise<Comment> {
    const response = await apiClient.post('/social/comments', data);
    return response.data;
  }

  /**
   * Update a comment
   */
  async updateComment(commentId: string, content: string): Promise<Comment> {
    const response = await apiClient.put(`/social/comments/${commentId}`, { content });
    return response.data;
  }

  /**
   * Delete a comment
   */
  async deleteComment(commentId: string): Promise<void> {
    await apiClient.delete(`/social/comments/${commentId}`);
  }

  // ==========================================================================
  // LIKES
  // ==========================================================================

  /**
   * Like content (beat, track, mix, comment)
   */
  async like(data: {
    content_type: 'beat' | 'track' | 'mix' | 'comment';
    content_id: string;
  }): Promise<Like> {
    const response = await apiClient.post('/social/likes', data);
    return response.data;
  }

  /**
   * Unlike content
   */
  async unlike(data: {
    content_type: 'beat' | 'track' | 'mix' | 'comment';
    content_id: string;
  }): Promise<void> {
    await apiClient.delete('/social/likes', { data });
  }

  /**
   * Get likes count for content
   */
  async getLikesCount(params: {
    content_type: 'beat' | 'track' | 'mix' | 'comment';
    content_id: string;
  }): Promise<{ count: number; is_liked: boolean }> {
    const response = await apiClient.get('/social/likes/count', { params });
    return response.data;
  }

  /**
   * Get users who liked content
   */
  async getLikes(params: {
    content_type: 'beat' | 'track' | 'mix' | 'comment';
    content_id: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    likes: Like[];
    total: number;
  }> {
    const response = await apiClient.get('/social/likes', { params });
    return response.data;
  }

  // ==========================================================================
  // FOLLOWS
  // ==========================================================================

  /**
   * Follow a user
   */
  async followUser(userId: string): Promise<Follow> {
    const response = await apiClient.post(`/social/follow/${userId}`);
    return response.data;
  }

  /**
   * Unfollow a user
   */
  async unfollowUser(userId: string): Promise<void> {
    await apiClient.delete(`/social/follow/${userId}`);
  }

  /**
   * Check if following a user
   */
  async isFollowing(userId: string): Promise<{ is_following: boolean }> {
    const response = await apiClient.get(`/social/follow/${userId}/check`);
    return response.data;
  }

  /**
   * Get user's followers
   */
  async getFollowers(params: {
    user_id: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    followers: Follow[];
    total: number;
  }> {
    const response = await apiClient.get(`/social/followers/${params.user_id}`, {
      params: { page: params.page, page_size: params.page_size }
    });
    return response.data;
  }

  /**
   * Get users that user is following
   */
  async getFollowing(params: {
    user_id: string;
    page?: number;
    page_size?: number;
  }): Promise<{
    following: Follow[];
    total: number;
  }> {
    const response = await apiClient.get(`/social/following/${params.user_id}`, {
      params: { page: params.page, page_size: params.page_size }
    });
    return response.data;
  }

  /**
   * Get follower/following counts
   */
  async getFollowStats(userId: string): Promise<{
    followers_count: number;
    following_count: number;
  }> {
    const response = await apiClient.get(`/social/follow/${userId}/stats`);
    return response.data;
  }

  // ==========================================================================
  // SHARES
  // ==========================================================================

  /**
   * Track a share (for analytics)
   */
  async trackShare(data: {
    content_type: 'beat' | 'track' | 'mix';
    content_id: string;
    platform: 'facebook' | 'twitter' | 'whatsapp' | 'link' | 'embed';
  }): Promise<void> {
    await apiClient.post('/social/shares', data);
  }

  /**
   * Get share count
   */
  async getShareCount(params: {
    content_type: 'beat' | 'track' | 'mix';
    content_id: string;
  }): Promise<{ count: number }> {
    const response = await apiClient.get('/social/shares/count', { params });
    return response.data;
  }

  /**
   * Generate share URLs
   */
  getShareUrls(params: {
    content_type: 'beat' | 'track' | 'mix';
    content_id: string;
    title: string;
  }): {
    facebook: string;
    twitter: string;
    whatsapp: string;
    link: string;
  } {
    const baseUrl = typeof window !== 'undefined' ? window.location.origin : 'https://beatpush.ng';
    const url = `${baseUrl}/${params.content_type}s/${params.content_id}`;
    const text = `Check out "${params.title}" on BeatPush!`;

    return {
      facebook: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`,
      twitter: `https://twitter.com/intent/tweet?text=${encodeURIComponent(text)}&url=${encodeURIComponent(url)}`,
      whatsapp: `https://wa.me/?text=${encodeURIComponent(text + ' ' + url)}`,
      link: url,
    };
  }

  // ==========================================================================
  // FEED & POSTS (Mock implementation for now)
  // ==========================================================================

  /**
   * Get feed (following, discover, trending)
   */
  async getFeed(
    feedType: 'following' | 'discover' | 'trending' = 'following',
    page: number = 1,
    pageSize: number = 20
  ): Promise<{
    posts: any[];
    page: number;
    pageSize: number;
    hasMore: boolean;
  }> {
    // Mock implementation - replace with real API call
    // For now, return empty feed
    return {
      posts: [],
      page,
      pageSize,
      hasMore: false,
    };
  }

  /**
   * Get user posts
   */
  async getUserPosts(
    userId: string,
    page: number = 1,
    pageSize: number = 20
  ): Promise<{
    posts: any[];
    page: number;
    pageSize: number;
    hasMore: boolean;
  }> {
    // Mock implementation
    return {
      posts: [],
      page,
      pageSize,
      hasMore: false,
    };
  }

  /**
   * Get single post
   */
  async getPost(postId: string): Promise<any> {
    // Mock implementation
    return null;
  }

  /**
   * Create post
   */
  async createPost(data: any): Promise<any> {
    // Mock implementation
    const response = await apiClient.post('/social/posts', data);
    return response.data;
  }

  /**
   * Update post
   */
  async updatePost(postId: string, data: any): Promise<any> {
    const response = await apiClient.put(`/social/posts/${postId}`, data);
    return response.data;
  }

  /**
   * Delete post
   */
  async deletePost(postId: string): Promise<void> {
    await apiClient.delete(`/social/posts/${postId}`);
  }

  /**
   * Toggle like on post
   */
  async toggleLike(postId: string): Promise<void> {
    await apiClient.post(`/social/posts/${postId}/like`);
  }

  /**
   * Toggle bookmark on post
   */
  async toggleBookmark(postId: string): Promise<void> {
    await apiClient.post(`/social/posts/${postId}/bookmark`);
  }

  /**
   * Toggle follow user
   */
  async toggleFollow(userId: string): Promise<void> {
    const isFollowing = await this.isFollowing(userId);
    if (isFollowing.is_following) {
      await this.unfollowUser(userId);
    } else {
      await this.followUser(userId);
    }
  }

  /**
   * Create comment on post
   */
  async createComment(postId: string, data: any): Promise<any> {
    return await this.postComment({
      content_type: 'beat', // Adjust based on post type
      content_id: postId,
      content: data.content,
      parent_id: data.parent_id,
    });
  }

  /**
   * Get bookmarks
   */
  async getBookmarks(
    page: number = 1,
    pageSize: number = 20
  ): Promise<{
    posts: any[];
    page: number;
    pageSize: number;
    hasMore: boolean;
  }> {
    // Mock implementation
    return {
      posts: [],
      page,
      pageSize,
      hasMore: false,
    };
  }

  /**
   * Get follow suggestions
   */
  async getFollowSuggestions(
    type: 'all' | 'similar' | 'trending' | 'mutual' = 'all',
    limit: number = 10
  ): Promise<any[]> {
    // Mock implementation
    return [];
  }

  /**
   * Get trending creators
   */
  async getTrendingCreators(
    genre?: string,
    location?: string,
    limit: number = 20
  ): Promise<any[]> {
    // Mock implementation
    return [];
  }
}

export default new SocialService();
