/**
 * Constants and configuration for AI Chat Interface
 */

import type { QuickActionDefinition, PageContextDefinition, PageType, ChatErrorType } from '../types';
export { ChatErrorType } from '../types';

// ============================================================================
// WebSocket Configuration
// ============================================================================

export const WEBSOCKET_CONFIG = {
  RECONNECT_DELAYS: [1000, 2000, 4000, 8000, 16000], // Exponential backoff
  MAX_RECONNECT_ATTEMPTS: 5,
  MESSAGE_TIMEOUT_MS: 30000, // 30 seconds
  HEARTBEAT_INTERVAL_MS: 30000, // 30 seconds
} as const;

// ============================================================================
// Chat Interface Configuration
// ============================================================================

export const CHAT_CONFIG = {
  MAX_MESSAGE_LENGTH: 4000,
  MAX_MESSAGES_PER_SESSION: 50,
  SESSION_EXPIRY_HOURS: 1,
  MAX_STORAGE_SIZE_MB: 5,
  STREAMING_ANIMATION_DELAY_MS: 50,
  AUTO_SCROLL_DURATION_MS: 300,
  TYPING_INDICATOR_DELAY_MS: 200,
  SAVE_DEBOUNCE_MS: 1000,
  SCROLL_THROTTLE_MS: 100,
  TYPING_THROTTLE_MS: 500,
} as const;

// ============================================================================
// UI Configuration
// ============================================================================

export const UI_CONFIG = {
  DESKTOP_SIDEBAR_WIDTH: 400,
  MIN_SIDEBAR_WIDTH: 320,
  MOBILE_BREAKPOINT: 768,
  TABLET_BREAKPOINT: 1024,
  ANIMATION_DURATION_MS: 300,
  FADE_IN_DURATION_MS: 200,
  PULSE_DURATION_MS: 1500,
  COPY_SUCCESS_DURATION_MS: 2000,
  NOTIFICATION_DURATION_MS: 5000,
  SWIPE_CLOSE_THRESHOLD: 100,
  MIN_TOUCH_TARGET_SIZE: 44,
  BACKDROP_BLUR_PX: 12,
  BACKGROUND_OPACITY: 0.8,
  BORDER_RADIUS_CONTAINER: 16,
  BORDER_RADIUS_BUBBLE: 12,
} as const;

// ============================================================================
// Quick Actions Configuration
// ============================================================================

export const QUICK_ACTIONS: QuickActionDefinition[] = [
  // Beat Upload Actions
  {
    id: 'generate_title',
    label: 'Generate Title',
    icon: 'Sparkles',
    promptTemplate: 'Generate 5 creative beat titles for a {genre} beat with {mood} mood at {bpm} BPM',
    requiredContext: ['genre'],
    availableOn: ['beat_upload', 'beat_edit'],
    useWebSocket: false,
  },
  {
    id: 'write_description',
    label: 'Write Description',
    icon: 'FileText',
    promptTemplate: 'Write a compelling beat description for a {genre} beat with {mood} mood. Include key features and ideal use cases.',
    requiredContext: ['genre'],
    availableOn: ['beat_upload', 'beat_edit'],
    useWebSocket: false,
  },
  {
    id: 'create_tags',
    label: 'Suggest Tags',
    icon: 'Tag',
    promptTemplate: 'Suggest 10 relevant tags for a {genre} beat with {mood} mood at {bpm} BPM',
    requiredContext: ['genre'],
    availableOn: ['beat_upload', 'beat_edit'],
    useWebSocket: false,
  },
  {
    id: 'recommend_price',
    label: 'Recommend Price',
    icon: 'DollarSign',
    promptTemplate: 'Recommend pricing (basic lease, premium lease, exclusive rights) for a {genre} beat based on current market trends',
    requiredContext: ['genre'],
    availableOn: ['beat_upload', 'beat_edit'],
    useWebSocket: false,
  },
  
  // Campaign Actions
  {
    id: 'analyze_performance',
    label: 'Analyze Performance',
    icon: 'TrendingUp',
    promptTemplate: 'Analyze this campaign performance and provide insights: {metrics}',
    requiredContext: ['metrics'],
    availableOn: ['campaign_dashboard'],
    useWebSocket: true,
  },
  {
    id: 'suggest_optimizations',
    label: 'Suggest Optimizations',
    icon: 'Zap',
    promptTemplate: 'Based on campaign metrics {metrics}, suggest 3-5 optimization strategies to improve performance',
    requiredContext: ['metrics'],
    availableOn: ['campaign_dashboard'],
    useWebSocket: true,
  },
  {
    id: 'generate_ad_copy',
    label: 'Generate Ad Copy',
    icon: 'MessageSquare',
    promptTemplate: 'Generate ad copy variations for promoting {campaignName} targeting {targetAudience}',
    requiredContext: ['campaignName'],
    availableOn: ['campaign_dashboard'],
    useWebSocket: false,
  },
  
  // Analytics Actions
  {
    id: 'explain_trends',
    label: 'Explain Trends',
    icon: 'BarChart',
    promptTemplate: 'Explain the trends in this data: Revenue {revenue}, Plays {plays}, Engagement {engagement}',
    requiredContext: ['revenue', 'plays'],
    availableOn: ['analytics'],
    useWebSocket: true,
  },
  {
    id: 'compare_performance',
    label: 'Compare Performance',
    icon: 'GitCompare',
    promptTemplate: 'Compare current period performance to previous period and highlight key changes',
    requiredContext: [],
    availableOn: ['analytics'],
    useWebSocket: true,
  },
  {
    id: 'get_recommendations',
    label: 'Get Recommendations',
    icon: 'Lightbulb',
    promptTemplate: 'Based on analytics data, provide actionable recommendations to improve revenue and engagement',
    requiredContext: [],
    availableOn: ['analytics'],
    useWebSocket: true,
  },
  
  // Profile Actions
  {
    id: 'write_bio',
    label: 'Write Bio',
    icon: 'User',
    promptTemplate: `Write 3 compelling artist bio variations for a music producer:

**Context:**
- Name: {fullName}
- Genres: {genres}
- Location: {location}
- Beats Count: {beatsCount}
- Followers: {followersCount}
- Achievements: {achievements}

**Please provide:**
1. **Short Bio** (50-100 words) - Perfect for Twitter, Instagram bio
2. **Medium Bio** (150-250 words) - Ideal for website about section
3. **Long Bio** (300-500 words) - Great for press kits, detailed profiles

Make each variation professional, authentic, and engaging. Highlight achievements naturally.`,
    requiredContext: [],
    availableOn: ['profile_edit'],
    useWebSocket: false,
  },
  {
    id: 'craft_artist_statement',
    label: 'Artist Statement',
    icon: 'Quote',
    promptTemplate: `Craft a professional artist statement for a music producer:

**Context:**
- Name: {fullName}
- Genres: {genres}
- Location: {location}
- Achievements: {achievements}

**Create:**
1. Artistic vision and philosophy
2. Creative process and inspiration
3. Goals and aspirations
4. What makes their sound unique

Format as a cohesive 200-300 word statement. Be authentic and compelling.`,
    requiredContext: [],
    availableOn: ['profile_edit'],
    useWebSocket: false,
  },
  {
    id: 'suggest_improvements',
    label: 'Suggest Improvements',
    icon: 'Edit',
    promptTemplate: `Review this profile and suggest improvements to attract more followers and collaborators:

**Current Bio:**
{existingBio}

**Profile Info:**
- Genres: {genres}
- Location: {location}
- Beats: {beatsCount}
- Followers: {followersCount}
- Social Links: {socialLinks}

**Provide:**
1. Bio improvement suggestions (3-5 specific points)
2. Missing information to add
3. Tone and style recommendations
4. Call-to-action suggestions
5. Profile completeness score

Be specific and actionable!`,
    requiredContext: [],
    availableOn: ['profile_edit'],
    useWebSocket: true,
  },
  
  // Social Media Actions
  {
    id: 'generate_captions',
    label: 'Generate Caption',
    icon: 'Hash',
    promptTemplate: `Generate social media captions for my {contentType}:

**Content Details:**
- Title: {contentTitle}
- Description: {contentDescription}
- Genre: {beatGenre}

**Please provide 5 caption variations with different tones:**
1. **Hype** - Energetic and exciting
2. **Professional** - Polished and industry-focused
3. **Emotional** - Personal and heartfelt
4. **Fun** - Playful and entertaining
5. **Mysterious** - Intriguing and atmospheric

**Platform-specific formatting:**
- Instagram: Up to 2200 chars, with emojis ✨
- Twitter: Max 280 chars, concise and punchy
- TikTok: Max 150 chars, trending and catchy

**Also include:**
- Relevant hashtags (separate list)
- Best posting time suggestions
- Call-to-action ideas

Make them authentic and engaging!`,
    requiredContext: ['contentType'],
    availableOn: ['social_feed'],
    useWebSocket: false,
  },
  {
    id: 'suggest_hashtags',
    label: 'Suggest Hashtags',
    icon: 'Hash',
    promptTemplate: `Suggest relevant hashtags for my {contentType}:

**Content:**
- Title: {contentTitle}
- Genre: {beatGenre}
- Description: {contentDescription}

**Provide three categories:**
1. **Popular Hashtags** (5-10) - High reach, trending
2. **Niche Hashtags** (5-10) - Targeted audience, genre-specific
3. **Branded Hashtags** (3-5) - Unique to your brand

Format as ready-to-copy lists with brief explanations.`,
    requiredContext: ['contentType'],
    availableOn: ['social_feed'],
    useWebSocket: false,
  },
  
  // Messaging Actions
  {
    id: 'suggest_reply',
    label: 'Suggest Reply',
    icon: 'Reply',
    promptTemplate: 'Suggest a professional reply to this message: {messageContent}',
    requiredContext: ['messageContent'],
    availableOn: ['messaging'],
    useWebSocket: false,
  },
  {
    id: 'write_professional_message',
    label: 'Write Message',
    icon: 'Mail',
    promptTemplate: 'Write a professional message for {purpose}',
    requiredContext: ['purpose'],
    availableOn: ['messaging'],
    useWebSocket: false,
  },
];

// ============================================================================
// Page Context Extractors
// ============================================================================

export const CONTEXT_EXTRACTORS: Record<PageType, PageContextDefinition> = {
  beat_upload: {
    pageType: 'beat_upload',
    extractContext: (props: any) => ({
      genre: props?.selectedGenre || props?.genre,
      bpm: props?.bpmInput || props?.bpm,
      mood: props?.moodInput || props?.mood,
      fileName: props?.uploadedFile?.name,
      fileSize: props?.uploadedFile?.size,
      duration: props?.audioDuration,
    }),
    quickActions: ['generate_title', 'write_description', 'create_tags', 'recommend_price'],
    contextDisplay: 'Helping with: Beat Upload',
  },
  beat_edit: {
    pageType: 'beat_edit',
    extractContext: (props: any) => ({
      beatId: props?.beat?.id,
      title: props?.beat?.title,
      genre: props?.beat?.genre,
      bpm: props?.beat?.bpm,
      mood: props?.beat?.mood,
      description: props?.beat?.description,
      tags: props?.beat?.tags,
      plays: props?.beat?.plays,
      likes: props?.beat?.likes,
    }),
    quickActions: ['improve_description', 'create_tags', 'suggest_price_changes'],
    contextDisplay: 'Helping with: Beat Edit',
  },
  campaign_dashboard: {
    pageType: 'campaign_dashboard',
    extractContext: (props: any) => ({
      campaignId: props?.campaign?.id,
      campaignName: props?.campaign?.name,
      metrics: {
        reach: props?.metrics?.reach,
        engagement: props?.metrics?.engagement,
        conversions: props?.metrics?.conversions,
        spent: props?.metrics?.spent,
      },
      budget: props?.campaign?.budget,
      targetAudience: props?.campaign?.targetAudience,
      duration: props?.campaign?.duration,
    }),
    quickActions: ['analyze_performance', 'suggest_optimizations', 'generate_ad_copy'],
    contextDisplay: 'Helping with: Campaign Analysis',
  },
  analytics: {
    pageType: 'analytics',
    extractContext: (props: any) => ({
      timeRange: props?.timeRange,
      revenue: props?.metrics?.revenue,
      plays: props?.metrics?.plays,
      engagement: props?.metrics?.engagement,
      trends: props?.trends,
      topBeats: props?.topBeats,
      growth: props?.growth,
    }),
    quickActions: ['explain_trends', 'compare_performance', 'get_recommendations'],
    contextDisplay: 'Helping with: Analytics',
  },
  profile_edit: {
    pageType: 'profile_edit',
    extractContext: (props: any) => ({
      existingBio: props?.bio || props?.existingBio || props?.profile?.bio,
      fullName: props?.fullName || props?.profile?.fullName,
      genres: props?.genres || props?.profile?.genres,
      location: props?.location || props?.profile?.location,
      socialLinks: props?.socialLinks || props?.profile?.socialLinks,
      beatsCount: props?.beatsCount || props?.profile?.beatsCount,
      followersCount: props?.followersCount || props?.profile?.followersCount,
      achievements: props?.achievements || props?.profile?.achievements,
    }),
    quickActions: ['write_bio', 'craft_artist_statement', 'suggest_improvements'],
    contextDisplay: 'Helping with: Profile Edit',
  },
  social_feed: {
    pageType: 'social_feed',
    extractContext: (props: any) => ({
      contentType: props?.contentType || 'post',
      contentTitle: props?.contentTitle || props?.title,
      contentDescription: props?.contentDescription || props?.description,
      imageUrl: props?.imageUrl || props?.image,
      beatGenre: props?.beatGenre || props?.genre,
      targetPlatforms: props?.targetPlatforms || ['instagram', 'twitter', 'tiktok'],
      targetAudience: props?.targetAudience,
    }),
    quickActions: ['generate_captions', 'suggest_hashtags'],
    contextDisplay: 'Helping with: Social Media',
  },
  messaging: {
    pageType: 'messaging',
    extractContext: (props: any) => ({
      messageContent: props?.messageContent,
      conversationContext: props?.conversationContext,
      purpose: props?.purpose,
    }),
    quickActions: ['suggest_reply', 'write_professional_message'],
    contextDisplay: 'Helping with: Messaging',
  },
  general: {
    pageType: 'general',
    extractContext: () => ({}),
    quickActions: [],
    contextDisplay: 'AI Assistant',
  },
};

// ============================================================================
// Error Messages
// ============================================================================

import { ChatErrorType } from '../types';

export const ERROR_MESSAGES: Record<ChatErrorType, string> = {
  [ChatErrorType.CONNECTION_FAILED]: 
    'Connection lost. Retrying in {seconds}s...',
  [ChatErrorType.WEBSOCKET_CLOSED]: 
    'Connection closed. Click retry to reconnect.',
  [ChatErrorType.MESSAGE_SEND_FAILED]: 
    'Failed to send message. Please try again.',
  [ChatErrorType.STREAMING_INTERRUPTED]: 
    'Response interrupted. Click retry to continue.',
  [ChatErrorType.QUOTA_EXCEEDED]: 
    "You've used all 20 free AI requests today. Upgrade to Premium for unlimited access!",
  [ChatErrorType.AUTHENTICATION_FAILED]: 
    'Session expired. Please log in again.',
  [ChatErrorType.TIMEOUT]: 
    'AI is taking longer than usual. Please try again or rephrase your question.',
  [ChatErrorType.RATE_LIMIT]: 
    'Too many requests. Please wait {seconds} seconds.',
  [ChatErrorType.SERVER_ERROR]: 
    'Our AI service is temporarily unavailable. We\'re working on it!',
};

/**
 * Get a user-friendly error message for a given error type
 * Handles dynamic value replacement (e.g., countdown seconds)
 */
export function getErrorMessage(
  errorType: ChatErrorType,
  params?: { seconds?: number }
): string {
  const template = ERROR_MESSAGES[errorType];
  if (!params?.seconds) {
    return template;
  }
  return template.replace('{seconds}', String(params.seconds));
}

// ============================================================================
// Color Palette
// ============================================================================

export const COLORS = {
  // Primary
  purple: '#8B5CF6',
  blue: '#3B82F6',
  gradient: 'linear-gradient(135deg, #8B5CF6 0%, #3B82F6 100%)',
  
  // Semantic
  success: '#10B981',
  warning: '#F59E0B',
  error: '#EF4444',
  info: '#3B82F6',
  
  // Text
  textPrimary: '#1F2937',
  textSecondary: '#6B7280',
  textPlaceholder: '#9CA3AF',
  textInverted: '#FFFFFF',
  
  // Background
  bgGlass: 'rgba(255, 255, 255, 0.1)',
  bgUserBubble: '#8B5CF6',
  bgAiBubble: '#F3F4F6',
} as const;

// ============================================================================
// Storage Keys
// ============================================================================

export const STORAGE_KEYS = {
  CHAT_SESSION: 'beatpush_chat_session',
  CHAT_PREFERENCES: 'beatpush_chat_preferences',
} as const;

// ============================================================================
// API Endpoints
// ============================================================================

export const API_ENDPOINTS = {
  WS_CHAT: '/api/v1/ai/ws',
  REST_GENERATE: '/api/v1/ai/generate',
  REST_QUOTA: '/api/v1/ai/quota',
  REST_USER: '/api/v1/users/me',
} as const;
