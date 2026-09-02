/**
 * AI Service Client
 * Frontend service for interacting with BeatPush AI API
 */

import { getAuthToken } from './auth';
import { SecureAIService } from './sanitizationService';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// ============================================================================
// Types
// ============================================================================

export type AIRequestType =
  | 'title'
  | 'description'
  | 'caption'
  | 'hashtags'
  | 'press_release'
  | 'campaign_suggestions'
  | 'genre_tags'
  | 'audience_insights';

export interface AIGenerateRequest {
  request_type: AIRequestType;
  params: Record<string, any>;
  bypass_cache?: boolean;
}

export interface ResponseMetadata {
  provider: string;
  model: string;
  response_time_ms: number;
  cached: boolean;
}

export interface QuotaInfo {
  tier: 'free' | 'premium';
  remaining: number | null;  // null for premium
  reset_at: string | null;   // ISO timestamp, null for premium
}

export interface AIGenerateResponse {
  success: boolean;
  content: Record<string, any>;
  metadata: ResponseMetadata;
  quota?: QuotaInfo;
}

export interface QuotaStatus {
  tier: 'free' | 'premium';
  remaining: number | null;
  reset_at: string | null;
  allowed: boolean;
}

// ============================================================================
// AI Service Class
// ============================================================================

class AIService {
  private baseURL: string;

  constructor() {
    this.baseURL = `${API_BASE_URL}/api/v1/ai`;
  }

  /**
   * Generate AI content
   */
  async generate(
    requestType: AIRequestType,
    params: Record<string, any>,
    bypassCache: boolean = false
  ): Promise<AIGenerateResponse> {
    const token = getAuthToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${this.baseURL}/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({
        request_type: requestType,
        params,
        bypass_cache: bypassCache,
      }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'AI generation failed' }));
      
      if (response.status === 429) {
        throw new QuotaExceededError(error.detail);
      }
      
      throw new Error(error.detail || 'AI generation failed');
    }

    return response.json();
  }

  /**
   * Get current quota status
   */
  async getQuotaStatus(): Promise<QuotaStatus> {
    const token = getAuthToken();
    if (!token) {
      throw new Error('Not authenticated');
    }

    const response = await fetch(`${this.baseURL}/quota`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get quota status');
    }

    return response.json();
  }

  // ============================================================================
  // Convenience Methods for Specific Content Types
  // ============================================================================

  /**
   * Generate beat titles (sanitized for security)
   */
  async generateTitles(params: {
    genre: string;
    mood?: string;
    bpm?: number;
    instruments?: string[];
  }): Promise<string[]> {
    const result = await this.generate('title', params);
    const titles = result.content.titles || [];
    // Sanitize all titles to prevent XSS attacks
    return SecureAIService.sanitizeArray(titles, 'generateTitles');
  }

  /**
   * Generate beat description (sanitized for security)
   */
  async generateDescription(params: {
    title: string;
    genre: string;
    mood?: string;
    bpm?: number;
  }): Promise<string> {
    const result = await this.generate('description', params);
    const description = result.content.description || '';
    // Sanitize description (allow basic formatting)
    return SecureAIService.sanitizeDescription(description, 'generateDescription');
  }

  /**
   * Generate social media captions
   */
  async generateCaptions(params: {
    track_title: string;
    artist_name: string;
    genre?: string;
    platform?: 'instagram' | 'twitter' | 'tiktok' | 'facebook';
  }): Promise<Array<{ tone: string; caption: string }>> {
    const result = await this.generate('caption', params);
    return result.content.captions || [];
  }

  /**
   * Generate hashtags
   */
  async generateHashtags(params: {
    track_title: string;
    artist_name: string;
    genre?: string;
    location?: string;
  }): Promise<{
    genre: string[];
    trending: string[];
    location: string[];
    campaign: string[];
  }> {
    const result = await this.generate('hashtags', params);
    return {
      genre: result.content.genre || [],
      trending: result.content.trending || [],
      location: result.content.location || [],
      campaign: result.content.campaign || [],
    };
  }

  /**
   * Generate press release
   */
  async generatePressRelease(params: {
    track_title: string;
    artist_name: string;
    genre?: string;
    artist_bio?: string;
    track_description?: string;
    release_date?: string;
  }): Promise<string> {
    const result = await this.generate('press_release', params);
    return result.content.press_release || '';
  }

  /**
   * Get campaign optimization suggestions
   */
  async getCampaignSuggestions(params: {
    campaign_metrics: Record<string, any>;
    target_audience?: string;
    budget?: number;
  }): Promise<string[]> {
    const result = await this.generate('campaign_suggestions', params);
    return result.content.suggestions || [];
  }

  /**
   * Get genre and mood tags
   */
  async getGenreTags(params: {
    title: string;
    description?: string;
    bpm?: number;
    key?: string;
  }): Promise<{
    genres: string[];
    moods: string[];
  }> {
    const result = await this.generate('genre_tags', params);
    return {
      genres: result.content.genres || [],
      moods: result.content.moods || [],
    };
  }

  /**
   * Get audience insights
   */
  async getAudienceInsights(params: {
    genre: string;
    style?: string;
  }): Promise<string> {
    const result = await this.generate('audience_insights', params);
    return result.content.insights || '';
  }
}

// ============================================================================
// Custom Errors
// ============================================================================

export class QuotaExceededError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'QuotaExceededError';
  }
}

// ============================================================================
// Export singleton instance
// ============================================================================

export const aiService = new AIService();
export default aiService;
