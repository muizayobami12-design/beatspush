/**
 * Profile Page Integration
 * Provides AI chat context for profile edit page
 * Supports bio generation, artist statement creation, and iterative refinement
 */

'use client';

import React, { useEffect, useCallback } from 'react';
import { usePageContext } from '../hooks/usePageContext';
import { useChatContext } from '../components/ChatProvider';
import { useChatStore } from '../store/chatStore';

interface ProfileData {
  // Existing profile data
  bio?: string;
  fullName?: string;
  location?: string;
  genres?: string[];
  socialLinks?: {
    twitter?: string;
    instagram?: string;
    facebook?: string;
    youtube?: string;
    spotify?: string;
    soundcloud?: string;
  };
  // Additional context
  beatsCount?: number;
  followersCount?: number;
  achievements?: string[];
}

interface ProfileIntegrationProps extends ProfileData {
  children?: React.ReactNode;
  // Callback for "Use This Bio" functionality
  onBioUpdate?: (bio: string, variant: 'short' | 'medium' | 'long') => void;
  onArtistStatementUpdate?: (statement: string) => void;
}

export function ProfileIntegration({
  bio,
  fullName,
  location,
  genres,
  socialLinks,
  beatsCount,
  followersCount,
  achievements,
  children,
  onBioUpdate,
  onArtistStatementUpdate,
}: ProfileIntegrationProps) {
  const { updateContext } = usePageContext({
    props: {
      existingBio: bio,
      bio,
      fullName,
      location,
      genres,
      socialLinks,
      beatsCount,
      followersCount,
      achievements,
    },
    autoDetect: false,
  });

  useEffect(() => {
    updateContext({
      pageType: 'profile_edit',
      pageUrl: window.location.pathname,
      contextData: {
        existingBio: bio,
        bio,
        fullName,
        location,
        genres: Array.isArray(genres) ? genres.join(', ') : genres,
        socialLinks: socialLinks ? Object.entries(socialLinks)
          .filter(([_, value]) => value)
          .map(([key, value]) => `${key}: ${value}`)
          .join(', ') : undefined,
        beatsCount,
        followersCount,
        achievements: Array.isArray(achievements) ? achievements.join(', ') : achievements,
      },
    });
  }, [bio, fullName, location, genres, socialLinks, beatsCount, followersCount, achievements, updateContext]);

  // Store callbacks in chat store for use by MessageBubble "Use This" buttons
  useEffect(() => {
    if (onBioUpdate) {
      useChatStore.getState().setAutoFillCallback('bio', onBioUpdate);
    }
    if (onArtistStatementUpdate) {
      useChatStore.getState().setAutoFillCallback('artistStatement', onArtistStatementUpdate);
    }

    return () => {
      useChatStore.getState().clearAutoFillCallbacks();
    };
  }, [onBioUpdate, onArtistStatementUpdate]);

  return <>{children}</>;
}

/**
 * Hook for Profile page AI chat integration
 * Provides methods for bio generation, artist statement creation, and iterative refinement
 */
export function useProfileChat(callbacks?: {
  onBioUpdate?: (bio: string, variant: 'short' | 'medium' | 'long') => void;
  onArtistStatementUpdate?: (statement: string) => void;
}) {
  const { openChat } = useChatContext();
  const sendMessage = useChatStore((state) => state.sendMessage);

  // Register callbacks
  useEffect(() => {
    if (callbacks?.onBioUpdate) {
      useChatStore.getState().setAutoFillCallback('bio', callbacks.onBioUpdate);
    }
    if (callbacks?.onArtistStatementUpdate) {
      useChatStore.getState().setAutoFillCallback('artistStatement', callbacks.onArtistStatementUpdate);
    }

    return () => {
      useChatStore.getState().clearAutoFillCallbacks();
    };
  }, [callbacks]);
  
  return {
    /**
     * Generate bio variations (short, medium, long)
     * Opens chat with Write Bio quick action available
     */
    writeBio: useCallback(() => {
      openChat();
    }, [openChat]),

    /**
     * Craft a professional artist statement
     * Opens chat with Craft Artist Statement quick action available
     */
    craftArtistStatement: useCallback(() => {
      openChat();
    }, [openChat]),

    /**
     * Suggest improvements to existing bio
     * Opens chat with Suggest Improvements quick action available
     */
    suggestImprovements: useCallback(() => {
      openChat();
    }, [openChat]),

    /**
     * Request specific refinement (e.g., "Make it more professional", "Add humor")
     */
    refineBio: useCallback((instruction: string) => {
      openChat();
      // Send refinement instruction after a brief delay to allow chat to open
      setTimeout(() => {
        sendMessage(`Refine my bio: ${instruction}`);
      }, 500);
    }, [openChat, sendMessage]),

    /**
     * Open chat for general profile-related questions and iterative refinement
     * Users can provide refinement instructions like "Make it more professional", "Add humor", etc.
     */
    openChat,
  };
}

/**
 * Example Usage:
 * 
 * function ProfileEditPage() {
 *   const { user } = useAuthStore();
 *   const [bioValue, setBioValue] = useState(user.bio || '');
 *   
 *   const { writeBio, craftArtistStatement, suggestImprovements, refineBio } = useProfileChat({
 *     onBioUpdate: (bio, variant) => {
 *       setBioValue(bio);
 *       toast.success(`${variant} bio applied!`);
 *     },
 *     onArtistStatementUpdate: (statement) => {
 *       // Handle artist statement
 *       toast.success('Artist statement applied!');
 *     },
 *   });
 * 
 *   return (
 *     <ProfileIntegration
 *       bio={user.bio}
 *       fullName={user.fullName}
 *       location={user.location}
 *       genres={user.genres}
 *       socialLinks={user.socialLinks}
 *       beatsCount={user.beatsCount}
 *       followersCount={user.followersCount}
 *       achievements={user.achievements}
 *       onBioUpdate={(bio, variant) => setBioValue(bio)}
 *     >
 *       <div className="space-y-4">
 *         <Textarea
 *           value={bioValue}
 *           onChange={(e) => setBioValue(e.target.value)}
 *           placeholder="Write your bio..."
 *         />
 *         
 *         <div className="flex flex-wrap gap-2">
 *           <Button onClick={writeBio}>
 *             <Sparkles className="w-4 h-4 mr-2" />
 *             Ask AI to Write Bio
 *           </Button>
 *           <Button variant="outline" onClick={craftArtistStatement}>
 *             <Quote className="w-4 h-4 mr-2" />
 *             Ask AI for Artist Statement
 *           </Button>
 *           <Button variant="outline" onClick={suggestImprovements}>
 *             <Edit className="w-4 h-4 mr-2" />
 *             Ask AI for Improvements
 *           </Button>
 *         </div>
 *         
 *         {bioValue && (
 *           <div className="flex gap-2">
 *             <Button size="sm" variant="ghost" onClick={() => refineBio('Make it more professional')}>
 *               More Professional
 *             </Button>
 *             <Button size="sm" variant="ghost" onClick={() => refineBio('Add some humor')}>
 *               Add Humor
 *             </Button>
 *             <Button size="sm" variant="ghost" onClick={() => refineBio('Make it shorter')}>
 *               Shorter
 *             </Button>
 *           </div>
 *         )}
 *         
 *         <p className="text-sm text-muted-foreground">
 *           💡 The AI chat will open with context-aware quick actions.
 *           Click "Use This Bio" in the chat to auto-fill your preferred variation.
 *         </p>
 *       </div>
 *     </ProfileIntegration>
 *   );
 * }
 */
