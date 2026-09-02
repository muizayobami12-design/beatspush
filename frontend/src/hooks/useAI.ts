/**
 * useAI Hook
 * React hook for AI operations
 */

import { useState, useEffect, useCallback } from 'react';
import aiService, { AIRequestType, QuotaStatus, QuotaExceededError } from '@/services/aiService';

export interface UseAIOptions {
  autoLoadQuota?: boolean;
}

export function useAI(options: UseAIOptions = {}) {
  const { autoLoadQuota = true } = options;

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [quota, setQuota] = useState<QuotaStatus | null>(null);

  // Load quota status
  const loadQuota = useCallback(async () => {
    try {
      const status = await aiService.getQuotaStatus();
      setQuota(status);
    } catch (err) {
      console.error('Failed to load quota:', err);
    }
  }, []);

  // Auto-load quota on mount
  useEffect(() => {
    if (autoLoadQuota) {
      loadQuota().catch(err => {
        console.error('Failed to auto-load quota:', err);
        // Don't crash the page if quota fails to load
      });
    }
  }, [autoLoadQuota, loadQuota]);

  // Generic generate function
  const generate = useCallback(async (
    requestType: AIRequestType,
    params: Record<string, any>,
    bypassCache: boolean = false
  ) => {
    setLoading(true);
    setError(null);

    try {
      const result = await aiService.generate(requestType, params, bypassCache);
      
      // Update quota if provided (convert QuotaInfo to QuotaStatus)
      if (result.quota) {
        setQuota({
          ...result.quota,
          allowed: true, // If we got a response, it was allowed
        });
      }

      return result;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'AI generation failed';
      setError(errorMessage);
      
      if (err instanceof QuotaExceededError) {
        await loadQuota();  // Refresh quota status
      }
      
      throw err;
    } finally {
      setLoading(false);
    }
  }, [loadQuota]);

  // Specific generator methods
  const generateTitles = useCallback(async (params: Parameters<typeof aiService.generateTitles>[0]) => {
    const result = await generate('title', params);
    return result.content.titles || [];
  }, [generate]);

  const generateDescription = useCallback(async (params: Parameters<typeof aiService.generateDescription>[0]) => {
    const result = await generate('description', params);
    return result.content.description || '';
  }, [generate]);

  const generateCaptions = useCallback(async (params: Parameters<typeof aiService.generateCaptions>[0]) => {
    const result = await generate('caption', params);
    return result.content.captions || [];
  }, [generate]);

  const generateHashtags = useCallback(async (params: Parameters<typeof aiService.generateHashtags>[0]) => {
    const result = await generate('hashtags', params);
    return {
      genre: result.content.genre || [],
      trending: result.content.trending || [],
      location: result.content.location || [],
      campaign: result.content.campaign || [],
    };
  }, [generate]);

  return {
    // State
    loading,
    error,
    quota,

    // Actions
    generate,
    loadQuota,

    // Convenience methods
    generateTitles,
    generateDescription,
    generateCaptions,
    generateHashtags,

    // Quota helpers
    isQuotaExceeded: quota?.remaining === 0 && quota.tier === 'free',
    isPremium: quota?.tier === 'premium',
    remaining: quota?.remaining,
  };
}

export default useAI;
