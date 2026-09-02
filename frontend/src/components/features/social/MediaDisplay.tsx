'use client';

import React from 'react';
import Image from 'next/image';
import { Play } from 'lucide-react';
import { cn } from '@/lib/utils';

interface MediaDisplayProps {
  mediaUrl: string;
  mediaType?: 'image' | 'video';
  alt?: string;
  className?: string;
}

/**
 * MediaDisplay - Renders post media (image or video) in a PostCard.
 * Handles both images and videos with appropriate controls.
 */
export const MediaDisplay = React.memo(function MediaDisplay({
  mediaUrl,
  mediaType,
  alt = 'Post media',
  className,
}: MediaDisplayProps) {
  // Auto-detect type from URL if not provided
  const detectedType = mediaType || (
    mediaUrl.match(/\.(mp4|webm|ogg|mov)(\?|$)/i) ? 'video' : 'image'
  );

  if (detectedType === 'video') {
    return (
      <div className={cn('relative rounded-lg overflow-hidden bg-black', className)}>
        <video
          src={mediaUrl}
          controls
          className="w-full max-h-96 object-contain"
          preload="metadata"
          aria-label={alt}
        >
          <track kind="captions" />
        </video>
      </div>
    );
  }

  return (
    <div className={cn('relative rounded-lg overflow-hidden', className)}>
      <a href={mediaUrl} target="_blank" rel="noopener noreferrer">
        <Image
          src={mediaUrl}
          alt={alt}
          width={600}
          height={400}
          className="w-full object-cover max-h-96 hover:opacity-95 transition-opacity"
          unoptimized
        />
      </a>
    </div>
  );
});

export default MediaDisplay;
