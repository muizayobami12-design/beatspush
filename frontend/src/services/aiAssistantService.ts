/**
 * AI Publishing Assistant Service
 * ChatGPT-like interface for music publishing
 */

import { apiClient } from '@/lib/api/client';

export interface AudioAnalysis {
  duration: number;
  duration_formatted: string;
  bitrate: number;
  quality: string;
  bpm: number;
  key: string;
  mood: string;
  analysis_available: boolean;
}

export interface PublishingDraft {
  title: string;
  description: string;
  tags: string[];
  price: number;
  genre: string;
  social_captions: {
    instagram: string;
    twitter: string;
    tiktok: string;
    whatsapp: string;
  };
  best_posting_time: string;
  audio_file: string;
}

export interface AnalyzeResponse {
  success: boolean;
  file_id: string;
  temp_path: string;
  filename: string;
  analysis: AudioAnalysis;
  detected_genre: string;
  draft: PublishingDraft;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export interface PublishResponse {
  success: boolean;
  message: string;
  beat_id: string;
  beat_url: string;
  title: string;
  price: number;
  social_captions: PublishingDraft['social_captions'];
}

export const aiAssistantService = {
  /**
   * Get AI assistant greeting
   */
  async getGreeting(): Promise<{ message: string; tips: string[] }> {
    const response = await apiClient.get('/ai-assistant/greeting');
    return response.data;
  },

  /**
   * Upload and analyze audio file
   */
  async analyzeAudio(
    file: File,
    genre?: string,
    onProgress?: (progress: number) => void
  ): Promise<AnalyzeResponse> {
    const formData = new FormData();
    formData.append('file', file);
    if (genre) {
      formData.append('genre', genre);
    }

    const response = await apiClient.post<AnalyzeResponse>(
      '/ai-assistant/analyze-audio',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total && onProgress) {
            const progress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            onProgress(progress);
          }
        },
      }
    );

    return response.data;
  },

  /**
   * Chat with AI (streaming responses)
   */
  async *chatStream(
    message: string,
    context: Record<string, any> = {}
  ): AsyncGenerator<string, void, undefined> {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/v1/ai-assistant/chat`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${localStorage.getItem('auth_token')}`,
        },
        body: JSON.stringify({ message, context }),
      }
    );

    if (!response.ok) {
      throw new Error('Failed to chat with AI');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        // Decode chunk
        const chunk = decoder.decode(value);

        // Parse SSE (Server-Sent Events)
        const lines = chunk.split('\n');
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.error) {
              throw new Error(data.error);
            }

            if (data.done) {
              return;
            }

            if (data.text) {
              yield data.text;
            }
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  },

  /**
   * Publish beat from AI-generated draft
   */
  async publishDraft(draft: PublishingDraft): Promise<PublishResponse> {
    const response = await apiClient.post<PublishResponse>(
      '/ai-assistant/publish-draft',
      draft
    );

    return response.data;
  },

  /**
   * Update draft (change title, price, etc.)
   */
  updateDraft(
    currentDraft: PublishingDraft,
    updates: Partial<PublishingDraft>
  ): PublishingDraft {
    return {
      ...currentDraft,
      ...updates,
    };
  },

  /**
   * Format price for display
   */
  formatPrice(price: number): string {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  },

  /**
   * Parse chat commands (e.g., "change price to 6000")
   */
  parseCommand(message: string): {
    type: string;
    value?: any;
  } | null {
    const lowerMessage = message.toLowerCase();

    // Price change
    const priceMatch = lowerMessage.match(/price.*?(\d+[,\d]*)/);
    if (priceMatch) {
      const price = parseInt(priceMatch[1].replace(/,/g, ''));
      return { type: 'change_price', value: price };
    }

    // Title change
    const titleMatch = lowerMessage.match(/title.*?["'](.+?)["']/);
    if (titleMatch) {
      return { type: 'change_title', value: titleMatch[1] };
    }

    // Genre change
    const genreMatch = lowerMessage.match(/genre.*?(afrobeat|trap|drill|dancehall|hip hop|r&b)/i);
    if (genreMatch) {
      return { type: 'change_genre', value: genreMatch[1] };
    }

    // Publish confirmation
    if (/\b(publish|yes|go|do it|sure|okay)\b/.test(lowerMessage)) {
      return { type: 'confirm_publish' };
    }

    return null;
  },
};

export default aiAssistantService;
