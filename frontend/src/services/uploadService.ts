/**
 * Upload Service
 * Handles file uploads (audio, images) with progress tracking
 */

import { apiClient } from './apiClient';

export interface UploadProgress {
  loaded: number;
  total: number;
  percentage: number;
}

export interface AudioUploadResult {
  success: boolean;
  file_id: string;
  public_url: string;
  metadata: {
    duration?: number;
    bitrate?: number;
    sample_rate?: number;
    file_size?: string;
    original_filename?: string;
    title?: string;
  };
}

export interface ImageUploadResult {
  success: boolean;
  public_url: string;
  image_type: string;
  dimensions: string;
  format: string;
}

export interface UploadStats {
  uploads_remaining: number;
  max_uploads_per_hour: number;
  window_seconds: number;
}

export interface StorageHealth {
  status: string;
  storage_type: 'r2' | 'local';
  r2_configured: boolean;
}

/**
 * Validate file before upload
 */
export const validateFile = (
  file: File,
  allowedTypes: string[],
  maxSizeMB: number
): { valid: boolean; error?: string } => {
  // Check file type
  const fileType = file.type;
  const isValidType = allowedTypes.some(type => {
    if (type.endsWith('/*')) {
      return fileType.startsWith(type.replace('/*', ''));
    }
    return fileType === type;
  });

  if (!isValidType) {
    return {
      valid: false,
      error: `Invalid file type. Allowed: ${allowedTypes.join(', ')}`
    };
  }

  // Check file size
  const fileSizeMB = file.size / (1024 * 1024);
  if (fileSizeMB > maxSizeMB) {
    return {
      valid: false,
      error: `File too large. Maximum size: ${maxSizeMB}MB (your file: ${fileSizeMB.toFixed(2)}MB)`
    };
  }

  return { valid: true };
};

/**
 * Upload audio file
 */
export const uploadAudio = async (
  file: File,
  options?: {
    title?: string;
    track_id?: string;
    onProgress?: (progress: UploadProgress) => void;
  }
): Promise<AudioUploadResult> => {
  // Validate file
  const validation = validateFile(
    file,
    ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/mp4', 'audio/ogg'],
    100 // 100MB max
  );

  if (!validation.valid) {
    throw new Error(validation.error);
  }

  // Create form data
  const formData = new FormData();
  formData.append('file', file);
  
  if (options?.title) {
    formData.append('title', options.title);
  }
  
  if (options?.track_id) {
    formData.append('track_id', options.track_id);
  }

  // Upload with progress tracking
  const response = await apiClient.post<AudioUploadResult>(
    '/uploads/audio',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (options?.onProgress && progressEvent.total) {
          const percentage = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          options.onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      },
    }
  );

  return response.data;
};

/**
 * Upload image file
 */
export const uploadImage = async (
  file: File,
  imageType: 'avatar' | 'cover' | 'beat_cover' | 'general' = 'general',
  onProgress?: (progress: UploadProgress) => void
): Promise<ImageUploadResult> => {
  // Validate file
  const validation = validateFile(
    file,
    ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
    10 // 10MB max
  );

  if (!validation.valid) {
    throw new Error(validation.error);
  }

  // Create form data
  const formData = new FormData();
  formData.append('file', file);
  formData.append('image_type', imageType);

  // Upload with progress tracking
  const response = await apiClient.post<ImageUploadResult>(
    '/uploads/image',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentage = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          );
          onProgress({
            loaded: progressEvent.loaded,
            total: progressEvent.total,
            percentage,
          });
        }
      },
    }
  );

  return response.data;
};

/**
 * Upload avatar image (400x400)
 */
export const uploadAvatar = async (
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<ImageUploadResult> => {
  return uploadImage(file, 'avatar', onProgress);
};

/**
 * Upload cover photo (1200x400)
 */
export const uploadCoverPhoto = async (
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<ImageUploadResult> => {
  return uploadImage(file, 'cover', onProgress);
};

/**
 * Upload beat cover art (800x800)
 */
export const uploadBeatCover = async (
  file: File,
  onProgress?: (progress: UploadProgress) => void
): Promise<ImageUploadResult> => {
  return uploadImage(file, 'beat_cover', onProgress);
};

/**
 * Delete file
 */
export const deleteFile = async (fileUrl: string): Promise<{ success: boolean; message: string }> => {
  // Encode the URL for the path parameter
  const encodedUrl = encodeURIComponent(fileUrl);
  
  const response = await apiClient.delete<{ success: boolean; message: string }>(
    `/uploads/${encodedUrl}`
  );

  return response.data;
};

/**
 * Get upload statistics
 */
export const getUploadStats = async (): Promise<UploadStats> => {
  const response = await apiClient.get<UploadStats>('/uploads/stats');
  return response.data;
};

/**
 * Check storage health
 */
export const getStorageHealth = async (): Promise<StorageHealth> => {
  const response = await apiClient.get<StorageHealth>('/uploads/health');
  return response.data;
};

/**
 * Format file size for display
 */
export const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
};

/**
 * Format duration for display (seconds to MM:SS)
 */
export const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = Math.floor(seconds % 60);
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
};

/**
 * Get file extension
 */
export const getFileExtension = (filename: string): string => {
  return filename.slice(filename.lastIndexOf('.') + 1).toLowerCase();
};

/**
 * Check if file is audio
 */
export const isAudioFile = (file: File): boolean => {
  return file.type.startsWith('audio/');
};

/**
 * Check if file is image
 */
export const isImageFile = (file: File): boolean => {
  return file.type.startsWith('image/');
};

/**
 * Create preview URL for image
 */
export const createImagePreview = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      if (e.target?.result) {
        resolve(e.target.result as string);
      } else {
        reject(new Error('Failed to create preview'));
      }
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
};

/**
 * Get audio duration
 */
export const getAudioDuration = (file: File): Promise<number> => {
  return new Promise((resolve, reject) => {
    const audio = new Audio();
    const url = URL.createObjectURL(file);
    
    audio.addEventListener('loadedmetadata', () => {
      URL.revokeObjectURL(url);
      resolve(audio.duration);
    });
    
    audio.addEventListener('error', () => {
      URL.revokeObjectURL(url);
      reject(new Error('Failed to load audio'));
    });
    
    audio.src = url;
  });
};

export default {
  uploadAudio,
  uploadImage,
  uploadAvatar,
  uploadCoverPhoto,
  uploadBeatCover,
  deleteFile,
  getUploadStats,
  getStorageHealth,
  validateFile,
  formatFileSize,
  formatDuration,
  getFileExtension,
  isAudioFile,
  isImageFile,
  createImagePreview,
  getAudioDuration,
};
