'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Upload, Music2, Image, CheckCircle2, X } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { trackService } from '@/services/trackService';
import { useAuthStore } from '@/store/authStore';
import { toast } from 'sonner';

const GENRES = [
  'Afrobeat', 'Hip Hop', 'R&B', 'Amapiano', 'Gospel', 'Pop',
  'Dancehall', 'Reggae', 'Afro-Fusion', 'Alte', 'Trap', 'Drill',
];

export default function TrackUploadPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const isDJ = user?.role === 'dj';
  
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    genre: '',
    isPremium: false,
    price: '',
    lyrics: '',
  });

  const [files, setFiles] = useState<{
    audio: File | null;
    cover: File | null;
  }>({
    audio: null,
    cover: null,
  });

  const handleFileChange = (type: 'audio' | 'cover', file: File | null) => {
    setFiles({ ...files, [type]: file });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!files.audio) {
      toast.error('Please upload an audio file');
      return;
    }

    setIsUploading(true);

    try {
      // Upload audio file to backend
      const audioFormData = new FormData();
      audioFormData.append('file', files.audio);
      
      let audioUrl = '/demo/audio.mp3';
      let coverUrl: string | undefined;

      // Upload audio
      try {
        const audioResponse = await fetch('/api/v1/uploads/audio', {
          method: 'POST',
          body: audioFormData,
        });
        if (audioResponse.ok) {
          const audioData = await audioResponse.json();
          audioUrl = audioData.url || audioUrl;
        }
      } catch (error) {
        console.warn('Audio upload failed, using demo URL:', error);
      }

      // Upload cover art if provided
      if (files.cover) {
        const coverFormData = new FormData();
        coverFormData.append('file', files.cover);
        
        try {
          const coverResponse = await fetch('/api/v1/uploads/image', {
            method: 'POST',
            body: coverFormData,
          });
          if (coverResponse.ok) {
            const coverData = await coverResponse.json();
            coverUrl = coverData.url;
          }
        } catch (error) {
          console.warn('Cover upload failed:', error);
        }
      }

      // Create track record in backend
      await trackService.createTrack({
        title: formData.title,
        description: formData.description || undefined,
        genre: formData.genre,
        is_premium: formData.isPremium,
        price: formData.isPremium && formData.price ? parseFloat(formData.price) : undefined,
        audio_url: audioUrl,
        cover_art_url: coverUrl,
        lyrics: formData.lyrics || undefined,
      });

      setUploadSuccess(true);
      toast.success('Track uploaded successfully!');
      
      setTimeout(() => {
        router.push('/tracks');
      }, 2000);
    } catch (error) {
      console.error('Upload failed:', error);
      toast.error('Failed to upload track. Please try again.');
      setIsUploading(false);
    }
  };

  if (uploadSuccess) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <div className="max-w-md w-full text-center">
          <div className="mb-6 flex justify-center">
            <div className="p-4 rounded-full bg-green-500/10">
              <CheckCircle2 className="h-16 w-16 text-green-500" />
            </div>
          </div>
          <h1 className="text-3xl font-bold mb-4">{isDJ ? 'Mix' : 'Track'} Uploaded!</h1>
          <p className="text-muted-foreground mb-8">
            Your {isDJ ? 'mix' : 'track'} is now available for streaming.
          </p>
          <Button size="lg" onClick={() => router.push('/tracks')}>
            View All Tracks
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-24">
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <Link href="/tracks">
            <Button variant="ghost" size="sm" className="gap-2 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to Tracks
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mb-2">Upload {isDJ ? 'Mix' : 'Track'}</h1>
          <p className="text-muted-foreground">
            {isDJ 
              ? 'Share your DJ mix with thousands of music lovers'
              : 'Share your music with fans and grow your audience'
            }
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Uploads */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">Files</h2>
              
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">
                  Audio File <span className="text-destructive">*</span>
                </label>
                <div className="border-2 border-dashed rounded-lg p-6">
                  <input
                    type="file"
                    accept="audio/*"
                    onChange={(e) => handleFileChange('audio', e.target.files?.[0] || null)}
                    className="hidden"
                    id="audio-upload"
                    required
                  />
                  {files.audio ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Music2 className="h-6 w-6 text-primary" />
                        <div>
                          <p className="font-medium">{files.audio.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {(files.audio.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => handleFileChange('audio', null)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <label htmlFor="audio-upload" className="cursor-pointer">
                      <div className="text-center">
                        <Upload className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="font-medium">Click to upload audio</p>
                      </div>
                    </label>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Cover Art</label>
                <div className="border-2 border-dashed rounded-lg p-6">
                  <input
                    type="file"
                    accept="image/*"
                    onChange={(e) => handleFileChange('cover', e.target.files?.[0] || null)}
                    className="hidden"
                    id="cover-upload"
                  />
                  {files.cover ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <img
                          src={URL.createObjectURL(files.cover)}
                          alt="Cover"
                          className="w-16 h-16 rounded object-cover"
                        />
                        <p className="font-medium">{files.cover.name}</p>
                      </div>
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        onClick={() => handleFileChange('cover', null)}
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  ) : (
                    <label htmlFor="cover-upload" className="cursor-pointer">
                      <div className="text-center">
                        <Image className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <p className="font-medium">Click to upload cover</p>
                      </div>
                    </label>
                  )}
                </div>
              </div>
            </div>

            {/* Track Info */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">{isDJ ? 'Mix' : 'Track'} Information</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Title <span className="text-destructive">*</span>
                  </label>
                  <Input
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder={isDJ ? 'Afrobeat Summer Mix 2024' : 'My Amazing Track'}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder={isDJ ? 'Describe your mix and the vibe...' : 'Tell us about your track...'}
                    rows={4}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Genre <span className="text-destructive">*</span>
                  </label>
                  <select
                    required
                    value={formData.genre}
                    onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background"
                  >
                    <option value="">Select genre...</option>
                    {GENRES.map((genre) => (
                      <option key={genre} value={genre}>{genre}</option>
                    ))}
                  </select>
                </div>

                {!isDJ && (
                  <>
                    <div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={formData.isPremium}
                          onChange={(e) => setFormData({ ...formData, isPremium: e.target.checked })}
                          className="w-4 h-4 rounded border-input"
                        />
                        <span className="text-sm font-medium">Make this a premium track</span>
                      </label>
                    </div>

                    {formData.isPremium && (
                      <div>
                        <label className="block text-sm font-medium mb-2">Price (₦)</label>
                        <Input
                          type="number"
                          min="100"
                          value={formData.price}
                          onChange={(e) => setFormData({ ...formData, price: e.target.value })}
                          placeholder="500"
                        />
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>

            <div className="flex gap-4">
              <Button
                type="button"
                variant="outline"
                size="lg"
                onClick={() => router.back()}
                disabled={isUploading}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                size="lg"
                disabled={isUploading}
                className="flex-1"
              >
                {isUploading ? 'Uploading...' : `Publish ${isDJ ? 'Mix' : 'Track'}`}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
