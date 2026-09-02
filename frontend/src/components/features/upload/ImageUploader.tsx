/**
 * ImageUploader Component
 * Specialized uploader for images with image-specific features
 */

'use client';

import React from 'react';
import { FileUploader } from './FileUploader';
import { uploadImage, ImageUploadResult } from '@/services/uploadService';

export interface ImageUploaderProps {
  imageType?: 'avatar' | 'cover' | 'beat_cover' | 'general';
  onSuccess?: (result: ImageUploadResult) => void;
  onError?: (error: Error) => void;
  label?: string;
  description?: string;
  className?: string;
}

export const ImageUploader: React.FC<ImageUploaderProps> = ({
  imageType = 'general',
  onSuccess,
  onError,
  label,
  description,
  className,
}) => {
  // Default labels based on image type
  const defaultLabels = {
    avatar: 'Upload Avatar',
    cover: 'Upload Cover Photo',
    beat_cover: 'Upload Beat Cover',
    general: 'Upload Image',
  };

  const defaultDescriptions = {
    avatar: 'Will be resized to 400x400 • JPEG, PNG, or WebP • Max 10MB',
    cover: 'Will be resized to 1200x400 • JPEG, PNG, or WebP • Max 10MB',
    beat_cover: 'Will be resized to 800x800 • JPEG, PNG, or WebP • Max 10MB',
    general: 'JPEG, PNG, WebP, or GIF • Max 10MB',
  };

  return (
    <FileUploader
      accept="image/jpeg,image/png,image/gif,image/webp"
      maxSizeMB={10}
      onFileSelect={(file) => {
        console.log('Image file selected:', file.name);
      }}
      onUpload={(file, onProgress) => 
        uploadImage(file, imageType, onProgress)
      }
      onSuccess={onSuccess}
      onError={onError}
      preview="image"
      label={label || defaultLabels[imageType]}
      description={description || defaultDescriptions[imageType]}
      className={className}
    />
  );
};

export default ImageUploader;
