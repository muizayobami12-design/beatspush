'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, Upload, Music2, Image, CheckCircle2, AlertCircle, X } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { beatService } from '@/services/beatService';

const GENRES = [
  'Afrobeat',
  'Hip Hop',
  'Trap',
  'R&B',
  'Drill',
  'Amapiano',
  'Gospel',
  'Pop',
  'Dancehall',
  'Reggae',
  'Afro-Fusion',
  'Alte',
];

const KEYS = [
  'C major', 'C minor', 'C# major', 'C# minor',
  'D major', 'D minor', 'Eb major', 'Eb minor',
  'E major', 'E minor', 'F major', 'F minor',
  'F# major', 'F# minor', 'G major', 'G minor',
  'Ab major', 'Ab minor', 'A major', 'A minor',
  'Bb major', 'Bb minor', 'B major', 'B minor',
];

export default function BeatUploadPage() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const [formData, setFormData] = useState({
    title: '',
    description: '',
    genre: '',
    bpm: '',
    musicalKey: '',
    leasePrice: '',
    exclusivePrice: '',
    tags: '',
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
      alert('Please upload an audio file');
      return;
    }

    setIsUploading(true);

    try {
      // Upload audio file
      const audioUrl = await beatService.uploadAudioFile(files.audio);
      
      // Upload cover art if provided
      let coverUrl: string | undefined;
      if (files.cover) {
        coverUrl = await beatService.uploadCoverArt(files.cover);
      }

      // Create beat
      await beatService.createBeat({
        title: formData.title,
        description: formData.description || undefined,
        genre: formData.genre,
        bpm: parseInt(formData.bpm),
        musical_key: formData.musicalKey || undefined,
        lease_price: parseFloat(formData.leasePrice),
        exclusive_price: formData.exclusivePrice ? parseFloat(formData.exclusivePrice) : undefined,
        tags: formData.tags || undefined,
        tagged_audio_url: audioUrl,
        cover_art_url: coverUrl,
      });

      setUploadSuccess(true);
      
      setTimeout(() => {
        router.push('/beats');
      }, 2000);
    } catch (error) {
      console.error('Upload failed:', error);
      alert('Failed to upload beat. Please try again.');
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
          <h1 className="text-3xl font-bold mb-4">Beat Uploaded Successfully!</h1>
          <p className="text-muted-foreground mb-8">
            Your beat has been published to the marketplace and is now available for purchase.
          </p>
          <Button size="lg" onClick={() => router.push('/beats')}>
            View in Marketplace
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <Link href="/beats">
            <Button variant="ghost" size="sm" className="gap-2 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to Marketplace
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mb-2">Upload Beat</h1>
          <p className="text-muted-foreground">
            Share your beat with thousands of artists looking for quality production
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="max-w-3xl mx-auto">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* File Uploads */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">Files</h2>
              
              {/* Audio File */}
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">
                  Audio File <span className="text-destructive">*</span>
                </label>
                <div className="border-2 border-dashed rounded-lg p-6 hover:border-primary/50 transition-colors">
                  <input
                    type="file"
                    accept="audio/mp3,audio/wav,audio/mpeg"
                    onChange={(e) => handleFileChange('audio', e.target.files?.[0] || null)}
                    className="hidden"
                    id="audio-upload"
                    required
                  />
                  {files.audio ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="p-2 rounded-lg bg-primary/10">
                          <Music2 className="h-6 w-6 text-primary" />
                        </div>
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
                        <p className="font-medium mb-1">Click to upload audio file</p>
                        <p className="text-sm text-muted-foreground">
                          MP3 or WAV, up to 200MB
                        </p>
                      </div>
                    </label>
                  )}
                </div>
              </div>

              {/* Cover Art */}
              <div>
                <label className="block text-sm font-medium mb-2">
                  Cover Art <span className="text-muted-foreground text-xs">(Optional)</span>
                </label>
                <div className="border-2 border-dashed rounded-lg p-6 hover:border-primary/50 transition-colors">
                  <input
                    type="file"
                    accept="image/jpeg,image/png,image/webp"
                    onChange={(e) => handleFileChange('cover', e.target.files?.[0] || null)}
                    className="hidden"
                    id="cover-upload"
                  />
                  {files.cover ? (
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-16 h-16 rounded-lg overflow-hidden bg-muted">
                          <img
                            src={URL.createObjectURL(files.cover)}
                            alt="Cover preview"
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div>
                          <p className="font-medium">{files.cover.name}</p>
                          <p className="text-sm text-muted-foreground">
                            {(files.cover.size / 1024).toFixed(2)} KB
                          </p>
                        </div>
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
                        <p className="font-medium mb-1">Click to upload cover art</p>
                        <p className="text-sm text-muted-foreground">
                          JPG or PNG, recommended 1000x1000px
                        </p>
                      </div>
                    </label>
                  )}
                </div>
              </div>
            </div>

            {/* Beat Information */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">Beat Information</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Title <span className="text-destructive">*</span>
                  </label>
                  <Input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    placeholder="Afro Vibes"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Description</label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    placeholder="Describe your beat..."
                    rows={4}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      Genre <span className="text-destructive">*</span>
                    </label>
                    <select
                      required
                      value={formData.genre}
                      onChange={(e) => setFormData({ ...formData, genre: e.target.value })}
                      className="w-full px-3 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                    >
                      <option value="">Select genre...</option>
                      {GENRES.map((genre) => (
                        <option key={genre} value={genre}>
                          {genre}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium mb-2">
                      BPM <span className="text-destructive">*</span>
                    </label>
                    <Input
                      type="number"
                      required
                      min="60"
                      max="200"
                      value={formData.bpm}
                      onChange={(e) => setFormData({ ...formData, bpm: e.target.value })}
                      placeholder="120"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Musical Key</label>
                  <select
                    value={formData.musicalKey}
                    onChange={(e) => setFormData({ ...formData, musicalKey: e.target.value })}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring"
                  >
                    <option value="">Select key...</option>
                    {KEYS.map((key) => (
                      <option key={key} value={key}>
                        {key}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Tags</label>
                  <Input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData({ ...formData, tags: e.target.value })}
                    placeholder="danceable, party, upbeat (comma separated)"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Separate tags with commas
                  </p>
                </div>
              </div>
            </div>

            {/* Pricing */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">Pricing (Naira)</h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">
                    Lease Price (₦) <span className="text-destructive">*</span>
                  </label>
                  <Input
                    type="number"
                    required
                    min="1000"
                    step="100"
                    value={formData.leasePrice}
                    onChange={(e) => setFormData({ ...formData, leasePrice: e.target.value })}
                    placeholder="5000"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Recommended: ₦1,000 - ₦15,000
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">
                    Exclusive Price (₦)
                  </label>
                  <Input
                    type="number"
                    min="10000"
                    step="1000"
                    value={formData.exclusivePrice}
                    onChange={(e) => setFormData({ ...formData, exclusivePrice: e.target.value })}
                    placeholder="15000"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    Typically 3x lease price. Leave blank to disable exclusive sales.
                  </p>
                </div>
              </div>

              <div className="mt-6 p-4 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <div className="flex gap-3">
                  <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">
                      Pricing Guide
                    </p>
                    <ul className="text-sm text-muted-foreground space-y-1">
                      <li>• You'll receive 85% of each sale (15% platform fee)</li>
                      <li>• Competitive pricing helps attract more buyers</li>
                      <li>• Check similar beats for reference</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>

            {/* Submit Button */}
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
                {isUploading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="h-5 w-5 mr-2" />
                    Publish Beat
                  </>
                )}
              </Button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
