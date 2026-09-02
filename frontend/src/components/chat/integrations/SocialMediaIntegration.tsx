/**
 * SocialMediaIntegration - AI integration for social media content generation
 * Provides platform-specific caption and hashtag generation
 * Supports 5 tone variations and auto-fill functionality
 */

'use client';

import React, { useEffect, useCallback } from 'react';
import { useChatContext } from '../components/ChatProvider';
import { usePageContext } from '../hooks/usePageContext';
import { useChatStore } from '../store/chatStore';
import type { PageContext } from '../types';

export interface SocialMediaIntegrationProps {
  contentType?: 'beat' | 'post' | 'achievement' | 'announcement';
  contentTitle?: string;
  contentDescription?: string;
  imageUrl?: string;
  beatGenre?: string;
  targetPlatforms?: Array<'instagram' | 'twitter' | 'tiktok' | 'facebook'>;
  targetAudience?: string;
  children?: React.ReactNode;
  // Callbacks for "Use This Caption" functionality
  onCaptionUpdate?: (caption: string, platform: string, tone: string) => void;
  onHashtagsUpdate?: (hashtags: string[]) => void;
}

/**
 * SocialMediaIntegration Component
 * Wraps social media pages/modals to provide AI context
 */
export function SocialMediaIntegration({
  contentType = 'post',
  contentTitle,
  contentDescription,
  imageUrl,
  beatGenre,
  targetPlatforms = ['instagram', 'twitter', 'tiktok'],
  targetAudience,
  children,
  onCaptionUpdate,
  onHashtagsUpdate,
}: SocialMediaIntegrationProps) {
  const { updateContext } = usePageContext({
    props: {
      contentType,
      contentTitle,
      contentDescription,
      imageUrl,
      beatGenre,
      targetPlatforms,
      targetAudience,
    },
    autoDetect: false,
  });

  useEffect(() => {
    updateContext({
      pageType: 'social_feed',
      pageUrl: window.location.pathname,
      contextData: {
        contentType,
        contentTitle,
        contentDescription,
        imageUrl,
        beatGenre,
        targetPlatforms: targetPlatforms.join(', '),
        targetAudience,
      },
    });
  }, [contentType, contentTitle, contentDescription, imageUrl, beatGenre, targetPlatforms, targetAudience, updateContext]);

  // Store callbacks in chat store for use by MessageBubble "Use This" buttons
  useEffect(() => {
    if (onCaptionUpdate) {
      useChatStore.getState().setAutoFillCallback('caption', onCaptionUpdate);
    }
    if (onHashtagsUpdate) {
      useChatStore.getState().setAutoFillCallback('hashtags', onHashtagsUpdate);
    }

    return () => {
      useChatStore.getState().clearAutoFillCallbacks();
    };
  }, [onCaptionUpdate, onHashtagsUpdate]);

  return <>{children}</>;
}

/**
 * Extract social media context from page
 */
export function extractSocialMediaContext(props: SocialMediaIntegrationProps): PageContext {
  return {
    pageType: 'social_feed',
    pageUrl: typeof window !== 'undefined' ? window.location.href : '',
    contextData: {
      contentType: props.contentType || 'post',
      contentTitle: props.contentTitle || '',
      contentDescription: props.contentDescription || '',
      imageUrl: props.imageUrl || '',
      beatGenre: props.beatGenre || '',
      targetPlatforms: props.targetPlatforms ? props.targetPlatforms.join(', ') : 'instagram, twitter, tiktok',
      targetAudience: props.targetAudience || '',
    },
  };
}

/**
 * Hook to use social media AI features
 * Provides methods for generating captions, hashtags, and more
 */
export function useSocialMediaAI(
  props: SocialMediaIntegrationProps,
  callbacks?: {
    onCaptionUpdate?: (caption: string, platform: string, tone: string) => void;
    onHashtagsUpdate?: (hashtags: string[]) => void;
  }
) {
  const { openChat } = useChatContext();
  const sendMessage = useChatStore((state) => state.sendMessage);

  // Register callbacks
  useEffect(() => {
    if (callbacks?.onCaptionUpdate) {
      useChatStore.getState().setAutoFillCallback('caption', callbacks.onCaptionUpdate);
    }
    if (callbacks?.onHashtagsUpdate) {
      useChatStore.getState().setAutoFillCallback('hashtags', callbacks.onHashtagsUpdate);
    }

    return () => {
      useChatStore.getState().clearAutoFillCallbacks();
    };
  }, [callbacks]);

  /**
   * Generate captions for specific platform or all platforms
   * Generates 5 variations with different tones
   */
  const generateCaption = useCallback(
    (platform: 'instagram' | 'twitter' | 'tiktok' | 'all' = 'all') => {
      openChat();
      
      // Auto-send message after brief delay
      setTimeout(() => {
        const platformText = platform === 'all' 
          ? 'Instagram, Twitter, and TikTok' 
          : platform.charAt(0).toUpperCase() + platform.slice(1);

        const prompt = `Generate ${platformText} captions for my ${props.contentType || 'content'}:

**Content Details:**
- Title: ${props.contentTitle || 'N/A'}
- Description: ${props.contentDescription || 'N/A'}
- Genre: ${props.beatGenre || 'N/A'}

Please provide 5 caption variations with different tones:
1. **Hype** - Energetic and exciting
2. **Professional** - Polished and industry-focused
3. **Emotional** - Personal and heartfelt
4. **Fun** - Playful and entertaining
5. **Mysterious** - Intriguing and atmospheric

Include platform-specific formatting and relevant hashtags!`;

        sendMessage(prompt);
      }, 500);
    },
    [props, openChat, sendMessage]
  );

  /**
   * Generate hashtag suggestions
   * Provides popular, niche, and branded hashtags
   */
  const suggestHashtags = useCallback(() => {
    openChat();

    setTimeout(() => {
      const prompt = `Suggest relevant hashtags for my ${props.contentType || 'content'}:

**Content:**
- Title: ${props.contentTitle || 'N/A'}
- Genre: ${props.beatGenre || 'N/A'}
- Description: ${props.contentDescription || 'N/A'}

Provide:
1. **Popular Hashtags** (5-10) - High reach, trending
2. **Niche Hashtags** (5-10) - Targeted audience, genre-specific
3. **Branded Hashtags** (3-5) - Unique to my brand

Format as ready-to-copy lists!`;

      sendMessage(prompt);
    }, 500);
  }, [props, openChat, sendMessage]);

  /**
   * Write an announcement post
   */
  const writeAnnouncement = useCallback(() => {
    openChat();

    setTimeout(() => {
      const prompt = `Write an engaging announcement for: ${props.contentTitle || 'my content'}

Details: ${props.contentDescription || 'N/A'}

Create:
1. Attention-grabbing headline
2. 3 body text variations (short, medium, long)
3. Call-to-action suggestions
4. Best posting times recommendation

Make it exciting and share-worthy!`;

      sendMessage(prompt);
    }, 500);
  }, [props, openChat, sendMessage]);

  /**
   * Get engagement tips for social media
   */
  const getEngagementTips = useCallback(() => {
    openChat();

    setTimeout(() => {
      const prompt = `Give me engagement tips for promoting my ${props.contentType || 'content'} on social media:

Content: ${props.contentTitle || 'my content'}
Genre: ${props.beatGenre || 'N/A'}

Provide:
1. Best posting times for each platform
2. Engagement strategies (questions, polls, CTAs)
3. Cross-promotion ideas
4. Story/Reel ideas
5. Community interaction tactics

Make them actionable and specific!`;

      sendMessage(prompt);
    }, 500);
  }, [props, openChat, sendMessage]);

  /**
   * Generate caption with specific tone
   */
  const generateCaptionWithTone = useCallback(
    (tone: 'hype' | 'professional' | 'emotional' | 'fun' | 'mysterious', platform: string = 'all') => {
      openChat();

      setTimeout(() => {
        const prompt = `Generate a ${tone} ${platform} caption for my ${props.contentType}:

Title: ${props.contentTitle}
Description: ${props.contentDescription}

Make it ${tone} and engaging!`;

        sendMessage(prompt);
      }, 500);
    },
    [props, openChat, sendMessage]
  );

  return {
    generateCaption,
    suggestHashtags,
    writeAnnouncement,
    getEngagementTips,
    generateCaptionWithTone,
    openChat,
  };
}

/**
 * Example Usage Component
 */
export const SocialMediaExample: React.FC<SocialMediaIntegrationProps> = (props) => {
  const { generateCaption, suggestHashtags, getEngagementTips } = useSocialMediaAI(props);

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold">AI-Powered Social Media Tools</h3>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        {/* Platform-specific caption generation */}
        <button
          onClick={() => generateCaption('instagram')}
          className="p-4 rounded-lg border border-purple-200 hover:border-purple-400 hover:bg-purple-50 transition-all"
        >
          <div className="flex items-center gap-2">
            <span className="text-2xl">📸</span>
            <div className="text-left">
              <div className="font-medium">Instagram Caption</div>
              <div className="text-sm text-gray-600">Generate engaging IG captions</div>
            </div>
          </div>
        </button>

        <button
          onClick={() => generateCaption('twitter')}
          className="p-4 rounded-lg border border-blue-200 hover:border-blue-400 hover:bg-blue-50 transition-all"
        >
          <div className="flex items-center gap-2">
            <span className="text-2xl">🐦</span>
            <div className="text-left">
              <div className="font-medium">Twitter Post</div>
              <div className="text-sm text-gray-600">Craft punchy tweets</div>
            </div>
          </div>
        </button>

        <button
          onClick={() => generateCaption('tiktok')}
          className="p-4 rounded-lg border border-pink-200 hover:border-pink-400 hover:bg-pink-50 transition-all"
        >
          <div className="flex items-center gap-2">
            <span className="text-2xl">🎵</span>
            <div className="text-left">
              <div className="font-medium">TikTok Caption</div>
              <div className="text-sm text-gray-600">Create viral TikTok text</div>
            </div>
          </div>
        </button>

        <button
          onClick={suggestHashtags}
          className="p-4 rounded-lg border border-green-200 hover:border-green-400 hover:bg-green-50 transition-all"
        >
          <div className="flex items-center gap-2">
            <span className="text-2xl">#️⃣</span>
            <div className="text-left">
              <div className="font-medium">Hashtag Ideas</div>
              <div className="text-sm text-gray-600">Get trending hashtags</div>
            </div>
          </div>
        </button>
      </div>

      <button
        onClick={getEngagementTips}
        className="w-full p-3 rounded-lg border border-indigo-200 hover:border-indigo-400 hover:bg-indigo-50 transition-all text-sm font-medium"
      >
        💡 Get Engagement Tips & Strategy
      </button>

      <p className="text-sm text-gray-500 mt-4">
        💡 Tip: The AI will generate 5 caption variations with different tones. Click "Use This Caption" to auto-fill!
      </p>
    </div>
  );
};

/**
 * Example Usage in a Component:
 * 
 * function ShareBeatModal({ beat }) {
 *   const [caption, setCaption] = useState('');
 *   const [hashtags, setHashtags] = useState<string[]>([]);
 *   
 *   const { generateCaption, suggestHashtags } = useSocialMediaAI(
 *     {
 *       contentType: 'beat',
 *       contentTitle: beat.title,
 *       contentDescription: beat.description,
 *       beatGenre: beat.genre,
 *       targetPlatforms: ['instagram', 'twitter', 'tiktok'],
 *     },
 *     {
 *       onCaptionUpdate: (caption, platform, tone) => {
 *         setCaption(caption);
 *         toast.success(`${tone} caption for ${platform} applied!`);
 *       },
 *       onHashtagsUpdate: (hashtags) => {
 *         setHashtags(hashtags);
 *         toast.success('Hashtags applied!');
 *       },
 *     }
 *   );
 *   
 *   return (
 *     <SocialMediaIntegration
 *       contentType="beat"
 *       contentTitle={beat.title}
 *       contentDescription={beat.description}
 *       beatGenre={beat.genre}
 *       onCaptionUpdate={(caption) => setCaption(caption)}
 *       onHashtagsUpdate={(hashtags) => setHashtags(hashtags)}
 *     >
 *       <div className="space-y-4">
 *         <Textarea
 *           value={caption}
 *           onChange={(e) => setCaption(e.target.value)}
 *           placeholder="Write your caption..."
 *         />
 *         
 *         <div className="flex gap-2">
 *           <Button onClick={() => generateCaption('instagram')}>
 *             📸 Instagram Caption
 *           </Button>
 *           <Button onClick={() => generateCaption('twitter')}>
 *             🐦 Twitter Post
 *           </Button>
 *           <Button onClick={() => generateCaption('tiktok')}>
 *             🎵 TikTok Caption
 *           </Button>
 *         </div>
 *         
 *         <Button variant="outline" onClick={suggestHashtags}>
 *           #️⃣ Get Hashtags
 *         </Button>
 *         
 *         {hashtags.length > 0 && (
 *           <div className="flex flex-wrap gap-2">
 *             {hashtags.map((tag) => (
 *               <span key={tag} className="px-2 py-1 bg-blue-100 rounded text-sm">
 *                 {tag}
 *               </span>
 *             ))}
 *           </div>
 *         )}
 *       </div>
 *     </SocialMediaIntegration>
 *   );
 * }
 */

export default SocialMediaExample;
