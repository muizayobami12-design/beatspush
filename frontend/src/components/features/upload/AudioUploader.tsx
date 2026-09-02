/**
 * AudioUploader Component
 * Specialized uploader for audio files with audio-specific features
 */

'use client';

import React from 'react';
import { FileUploader } from './FileUploader';
import { uploadAudio, AudioUploadResult } from '@/services/uploadService';
import { Music } from 'lucide-react';

export interface AudioUploaderProps {
  onSuccess?: (result: AudioUploadResult) => void;
  onError?: (error: Error) => void;
  title?: string;
  trackId?: string;
  className?: string;
}

export const AudioUploader: React.FC<AudioUploaderProps> = ({
  onSuccess,
  onError,
  title,
  trackId,
  className,
}) => {
  return (
    <FileUploader
      accept="audio/mpeg,audio/wav,audio/flac,audio/mp4,audio/ogg"
      maxSizeMB={100}
      onFileSelect={(file) => {
        console.log('Audio file selected:', file.name);
      }}
      onUpload={(file, onProgress) => 
        uploadAudio(file, { title, track_id: trackId, onProgress })
      }
      onSuccess={onSuccess}
      onError={onError}
      preview="audio"
      label="Upload Audio Track"
      description="MP3, WAV, FLAC, M4A, or OGG • Max 100MB"
      className={className}
    />
  );
};

export default AudioUploader;
