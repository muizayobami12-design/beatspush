/**
 * FileUploader Component
 * Generic file uploader with drag-and-drop, progress tracking, and preview
 */

'use client';

import React, { useState, useRef, useCallback } from 'react';
import { Upload, X, File, AlertCircle, CheckCircle } from 'lucide-react';
import { UploadProgress, formatFileSize } from '@/services/uploadService';

export interface FileUploaderProps {
  accept: string;
  maxSizeMB: number;
  onFileSelect: (file: File) => void;
  onUpload: (file: File, onProgress: (progress: UploadProgress) => void) => Promise<any>;
  onSuccess?: (result: any) => void;
  onError?: (error: Error) => void;
  preview?: 'image' | 'audio' | 'none';
  label?: string;
  description?: string;
  className?: string;
}

export const FileUploader: React.FC<FileUploaderProps> = ({
  accept,
  maxSizeMB,
  onFileSelect,
  onUpload,
  onSuccess,
  onError,
  preview = 'none',
  label = 'Upload File',
  description,
  className = '',
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Handle file selection
  const handleFileSelect = useCallback((selectedFile: File) => {
    setError(null);
    setSuccess(false);
    
    // Validate file size
    const fileSizeMB = selectedFile.size / (1024 * 1024);
    if (fileSizeMB > maxSizeMB) {
      setError(`File too large. Maximum size: ${maxSizeMB}MB (your file: ${fileSizeMB.toFixed(2)}MB)`);
      return;
    }

    setFile(selectedFile);
    onFileSelect(selectedFile);

    // Create preview
    if (preview === 'image' && selectedFile.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreviewUrl(e.target?.result as string);
      };
      reader.readAsDataURL(selectedFile);
    } else if (preview === 'audio' && selectedFile.type.startsWith('audio/')) {
      const url = URL.createObjectURL(selectedFile);
      setPreviewUrl(url);
    }
  }, [maxSizeMB, preview, onFileSelect]);

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  // Handle drag events
  const handleDragEnter = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  // Handle upload
  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setError(null);
    setSuccess(false);
    setProgress(null);

    try {
      const result = await onUpload(file, (prog) => {
        setProgress(prog);
      });
      
      setSuccess(true);
      if (onSuccess) {
        onSuccess(result);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.message || 'Upload failed';
      setError(errorMessage);
      if (onError) {
        onError(new Error(errorMessage));
      }
    } finally {
      setUploading(false);
    }
  };

  // Handle remove
  const handleRemove = () => {
    setFile(null);
    setPreviewUrl(null);
    setProgress(null);
    setError(null);
    setSuccess(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle click to open file dialog
  const handleClick = () => {
    fileInputRef.current?.click();
  };

  return (
    <div className={`w-full ${className}`}>
      {/* Upload Area */}
      {!file && (
        <div
          onClick={handleClick}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
          className={`
            border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
            transition-colors duration-200
            ${isDragging 
              ? 'border-blue-500 bg-blue-50' 
              : 'border-gray-300 hover:border-gray-400 bg-gray-50'
            }
          `}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept={accept}
            onChange={handleInputChange}
            className="hidden"
          />
          
          <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
          
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            {label}
          </h3>
          
          {description && (
            <p className="text-sm text-gray-500 mb-4">
              {description}
            </p>
          )}
          
          <p className="text-sm text-gray-600">
            Drag and drop or click to browse
          </p>
          
          <p className="text-xs text-gray-500 mt-2">
            Maximum file size: {maxSizeMB}MB
          </p>
        </div>
      )}

      {/* File Preview */}
      {file && (
        <div className="border rounded-lg p-4 bg-white">
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-3 flex-1">
              <File className="w-10 h-10 text-gray-400 flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {file.name}
                </p>
                <p className="text-xs text-gray-500">
                  {formatFileSize(file.size)} • {file.type}
                </p>
              </div>
            </div>
            
            {!uploading && !success && (
              <button
                onClick={handleRemove}
                className="p-1 hover:bg-gray-100 rounded"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            )}
          </div>

          {/* Image Preview */}
          {preview === 'image' && previewUrl && (
            <div className="mb-4">
              <img
                src={previewUrl}
                alt="Preview"
                className="w-full h-48 object-cover rounded"
              />
            </div>
          )}

          {/* Audio Preview */}
          {preview === 'audio' && previewUrl && (
            <div className="mb-4">
              <audio controls className="w-full">
                <source src={previewUrl} type={file.type} />
                Your browser does not support audio playback.
              </audio>
            </div>
          )}

          {/* Progress Bar */}
          {uploading && progress && (
            <div className="mb-4">
              <div className="flex justify-between text-xs text-gray-600 mb-1">
                <span>Uploading...</span>
                <span>{progress.percentage}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress.percentage}%` }}
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded flex items-start space-x-2">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Success Message */}
          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 rounded flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-green-500" />
              <p className="text-sm text-green-700">Upload successful!</p>
            </div>
          )}

          {/* Upload Button */}
          {!uploading && !success && (
            <button
              onClick={handleUpload}
              disabled={!!error}
              className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
            >
              Upload
            </button>
          )}

          {/* Upload Another Button */}
          {success && (
            <button
              onClick={handleRemove}
              className="w-full py-2 px-4 bg-gray-600 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Upload Another
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default FileUploader;
