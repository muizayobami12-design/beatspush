'use client';

import React from 'react';
import Image from 'next/image';
import { FileText, Music, Video, Download, ExternalLink } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Attachment {
  id: string;
  file_type: 'image' | 'audio' | 'document' | 'voice_note';
  storage_url: string;
  original_filename: string;
  file_size: number;
  mime_type?: string;
  duration?: number;
  width?: number;
  height?: number;
  thumbnail_url?: string;
}

interface AttachmentPreviewProps {
  attachment: Attachment;
  className?: string;
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`;
}

function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = seconds % 60;
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * AttachmentPreview - Renders a message attachment based on its type.
 * Supports images, audio, videos, voice notes, and documents.
 */
export const AttachmentPreview = React.memo(function AttachmentPreview({
  attachment,
  className,
}: AttachmentPreviewProps) {
  const { file_type, storage_url, original_filename, file_size, duration, thumbnail_url } = attachment;

  if (file_type === 'image') {
    return (
      <div className={cn('rounded-lg overflow-hidden max-w-[280px]', className)}>
        <a href={storage_url} target="_blank" rel="noopener noreferrer">
          <Image
            src={thumbnail_url || storage_url}
            alt={original_filename}
            width={280}
            height={200}
            className="object-cover w-full hover:opacity-90 transition-opacity"
          />
        </a>
      </div>
    );
  }

  if (file_type === 'audio' || file_type === 'voice_note') {
    return (
      <div className={cn('rounded-lg bg-muted p-3 max-w-[280px]', className)}>
        <div className="flex items-center gap-2 mb-2">
          <div className="p-1.5 bg-primary/10 rounded-full">
            <Music className="w-4 h-4 text-primary" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{original_filename}</p>
            <p className="text-xs text-muted-foreground">
              {duration ? formatDuration(duration) : ''} · {formatFileSize(file_size)}
            </p>
          </div>
        </div>
        <audio
          src={storage_url}
          controls
          className="w-full h-8"
          aria-label={`Audio: ${original_filename}`}
        />
      </div>
    );
  }

  if (file_type === 'document') {
    return (
      <div className={cn('rounded-lg border bg-card p-3 max-w-[280px]', className)}>
        <div className="flex items-center gap-3">
          <div className="p-2 bg-muted rounded-lg flex-shrink-0">
            <FileText className="w-5 h-5 text-muted-foreground" />
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{original_filename}</p>
            <p className="text-xs text-muted-foreground">{formatFileSize(file_size)}</p>
          </div>
          <a
            href={storage_url}
            download={original_filename}
            className="p-1.5 hover:bg-muted rounded-lg transition-colors"
            aria-label="Download file"
          >
            <Download className="w-4 h-4 text-muted-foreground" />
          </a>
        </div>
      </div>
    );
  }

  // Fallback for unknown types
  return (
    <div className={cn('rounded-lg border bg-card p-3 max-w-[280px]', className)}>
      <div className="flex items-center gap-3">
        <FileText className="w-5 h-5 text-muted-foreground" />
        <div className="flex-1 min-w-0">
          <p className="text-sm truncate">{original_filename}</p>
          <p className="text-xs text-muted-foreground">{formatFileSize(file_size)}</p>
        </div>
        <a href={storage_url} target="_blank" rel="noopener noreferrer" aria-label="Open file">
          <ExternalLink className="w-4 h-4 text-muted-foreground" />
        </a>
      </div>
    </div>
  );
});

export default AttachmentPreview;
