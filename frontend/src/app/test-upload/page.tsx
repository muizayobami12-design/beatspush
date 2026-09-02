/**
 * Upload Test Page
 * Test the upload functionality with backend endpoints
 */

'use client';

import React, { useState, useEffect } from 'react';
import { AudioUploader } from '@/components/features/upload/AudioUploader';
import { ImageUploader } from '@/components/features/upload/ImageUploader';
import { 
  AudioUploadResult, 
  ImageUploadResult, 
  getUploadStats, 
  getStorageHealth,
  formatDuration
} from '@/services/uploadService';
import { CheckCircle, AlertCircle, HardDrive, Upload as UploadIcon } from 'lucide-react';

export default function TestUploadPage() {
  const [audioResult, setAudioResult] = useState<AudioUploadResult | null>(null);
  const [imageResult, setImageResult] = useState<ImageUploadResult | null>(null);
  const [uploadStats, setUploadStats] = useState<any>(null);
  const [storageHealth, setStorageHealth] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Load stats and health on mount
  useEffect(() => {
    loadStats();
    loadHealth();
  }, []);

  const loadStats = async () => {
    try {
      const stats = await getUploadStats();
      setUploadStats(stats);
    } catch (err: any) {
      console.error('Failed to load stats:', err);
    }
  };

  const loadHealth = async () => {
    try {
      const health = await getStorageHealth();
      setStorageHealth(health);
    } catch (err: any) {
      console.error('Failed to load health:', err);
      setError('Not authenticated. Please login first.');
    }
  };

  const handleAudioSuccess = (result: AudioUploadResult) => {
    setAudioResult(result);
    loadStats(); // Refresh stats
    console.log('Audio upload successful:', result);
  };

  const handleImageSuccess = (result: ImageUploadResult) => {
    setImageResult(result);
    loadStats(); // Refresh stats
    console.log('Image upload successful:', result);
  };

  const handleError = (err: Error) => {
    setError(err.message);
    console.error('Upload error:', err);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Upload Test Page
          </h1>
          <p className="text-gray-600">
            Test audio and image uploads with the backend API
          </p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-red-800">Error</p>
              <p className="text-sm text-red-700">{error}</p>
              <p className="text-xs text-red-600 mt-1">
                Make sure backend is running and you're logged in
              </p>
            </div>
          </div>
        )}

        {/* Storage Health Status */}
        {storageHealth && (
          <div className="mb-6 p-4 bg-white border rounded-lg">
            <div className="flex items-center space-x-3 mb-3">
              <HardDrive className="w-5 h-5 text-blue-500" />
              <h2 className="text-lg font-semibold text-gray-900">Storage Status</h2>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase">Status</p>
                <p className="text-sm font-medium text-gray-900">{storageHealth.status}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase">Storage Type</p>
                <p className="text-sm font-medium text-gray-900">
                  {storageHealth.storage_type === 'r2' ? 'Cloudflare R2' : 'Local Storage'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase">R2 Configured</p>
                <p className="text-sm font-medium text-gray-900">
                  {storageHealth.r2_configured ? 'Yes' : 'No (using local fallback)'}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Upload Stats */}
        {uploadStats && (
          <div className="mb-6 p-4 bg-white border rounded-lg">
            <div className="flex items-center space-x-3 mb-3">
              <UploadIcon className="w-5 h-5 text-green-500" />
              <h2 className="text-lg font-semibold text-gray-900">Upload Limits</h2>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <p className="text-xs text-gray-500 uppercase">Uploads Remaining</p>
                <p className="text-2xl font-bold text-gray-900">{uploadStats.uploads_remaining}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase">Max Per Hour</p>
                <p className="text-2xl font-bold text-gray-900">{uploadStats.max_uploads_per_hour}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase">Window</p>
                <p className="text-2xl font-bold text-gray-900">
                  {Math.round(uploadStats.window_seconds / 60)} min
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Upload Sections */}
        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Audio Upload */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Audio Upload Test
            </h2>
            <AudioUploader
              onSuccess={handleAudioSuccess}
              onError={handleError}
              title="Test Audio Track"
            />
            
            {/* Audio Result */}
            {audioResult && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2 mb-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <h3 className="font-medium text-green-900">Upload Successful!</h3>
                </div>
                <div className="space-y-2 text-sm">
                  <div>
                    <span className="text-gray-600">File ID:</span>
                    <span className="ml-2 font-mono text-gray-900">{audioResult.file_id}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">URL:</span>
                    <a 
                      href={audioResult.public_url} 
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-2 text-blue-600 hover:underline break-all"
                    >
                      {audioResult.public_url}
                    </a>
                  </div>
                  {audioResult.metadata.duration && (
                    <div>
                      <span className="text-gray-600">Duration:</span>
                      <span className="ml-2 text-gray-900">
                        {formatDuration(audioResult.metadata.duration)}
                      </span>
                    </div>
                  )}
                  {audioResult.metadata.bitrate && (
                    <div>
                      <span className="text-gray-600">Bitrate:</span>
                      <span className="ml-2 text-gray-900">
                        {audioResult.metadata.bitrate} kbps
                      </span>
                    </div>
                  )}
                  {audioResult.metadata.sample_rate && (
                    <div>
                      <span className="text-gray-600">Sample Rate:</span>
                      <span className="ml-2 text-gray-900">
                        {audioResult.metadata.sample_rate} Hz
                      </span>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Image Upload */}
          <div>
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              Image Upload Test
            </h2>
            <ImageUploader
              imageType="beat_cover"
              onSuccess={handleImageSuccess}
              onError={handleError}
            />
            
            {/* Image Result */}
            {imageResult && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center space-x-2 mb-3">
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <h3 className="font-medium text-green-900">Upload Successful!</h3>
                </div>
                <div className="space-y-2 text-sm mb-3">
                  <div>
                    <span className="text-gray-600">URL:</span>
                    <a 
                      href={imageResult.public_url} 
                      target="_blank"
                      rel="noopener noreferrer"
                      className="ml-2 text-blue-600 hover:underline break-all"
                    >
                      {imageResult.public_url}
                    </a>
                  </div>
                  <div>
                    <span className="text-gray-600">Dimensions:</span>
                    <span className="ml-2 text-gray-900">{imageResult.dimensions}</span>
                  </div>
                  <div>
                    <span className="text-gray-600">Format:</span>
                    <span className="ml-2 text-gray-900 uppercase">{imageResult.format}</span>
                  </div>
                </div>
                {/* Show uploaded image */}
                <img 
                  src={imageResult.public_url} 
                  alt="Uploaded" 
                  className="w-full rounded border"
                />
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-3">
            Testing Instructions
          </h3>
          <ol className="space-y-2 text-sm text-blue-800">
            <li>1. Make sure the backend is running on port 9000</li>
            <li>2. Login to get authentication token</li>
            <li>3. Upload test files using the forms above</li>
            <li>4. Check the console for detailed logs</li>
            <li>5. Verify files are saved to <code className="px-1 bg-blue-100 rounded">backend/uploads/</code></li>
          </ol>
          
          <div className="mt-4 p-3 bg-blue-100 rounded">
            <p className="text-xs text-blue-700 font-medium mb-1">Backend Status Check:</p>
            <code className="text-xs text-blue-900">
              curl http://localhost:9000/api/v1/uploads/health
            </code>
          </div>
        </div>
      </div>
    </div>
  );
}
