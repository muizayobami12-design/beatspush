/**
 * Beat Upload Page Integration
 * Provides AI chat context for beat upload page
 */

'use client';

import React, { useEffect } from 'react';
import { usePageContext } from '../hooks/usePageContext';
import { useChatContext } from '../components/ChatProvider';

interface BeatUploadIntegrationProps {
  // Beat upload form data
  genre?: string;
  bpm?: number;
  mood?: string;
  fileName?: string;
  fileSize?: number;
  duration?: number;
  // Optional: Pass children to wrap
  children?: React.ReactNode;
}

export function BeatUploadIntegration({
  genre,
  bpm,
  mood,
  fileName,
  fileSize,
  duration,
  children,
}: BeatUploadIntegrationProps) {
  const { updateContext } = usePageContext({
    props: {
      selectedGenre: genre,
      bpmInput: bpm,
      moodInput: mood,
      uploadedFile: fileName ? {
        name: fileName,
        size: fileSize,
      } : undefined,
      audioDuration: duration,
    },
    autoDetect: false,
  });

  // Update context when props change
  useEffect(() => {
    updateContext({
      pageType: 'beat_upload',
      pageUrl: window.location.pathname,
      contextData: {
        genre,
        bpm,
        mood,
        fileName,
        fileSize,
        duration,
      },
    });
  }, [genre, bpm, mood, fileName, fileSize, duration, updateContext]);

  return <>{children}</>;
}

/**
 * Hook for Beat Upload page integration
 */
export function useBeatUploadChat() {
  const { openChat } = useChatContext();
  
  return {
    askAIForTitle: () => openChat(),
    askAIForDescription: () => openChat(),
    askAIForTags: () => openChat(),
    askAIForPricing: () => openChat(),
    openChat,
  };
}

/**
 * Example Usage:
 * 
 * function BeatUploadPage() {
 *   const [genre, setGenre] = useState('');
 *   const [bpm, setBpm] = useState(120);
 *   const { askAIForTitle } = useBeatUploadChat();
 * 
 *   return (
 *     <BeatUploadIntegration genre={genre} bpm={bpm}>
 *       <div>
 *         <input value={genre} onChange={(e) => setGenre(e.target.value)} />
 *         <button onClick={askAIForTitle}>Ask AI for Title</button>
 *       </div>
 *     </BeatUploadIntegration>
 *   );
 * }
 */
