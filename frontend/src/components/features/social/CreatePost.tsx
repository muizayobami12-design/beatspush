'use client';

import { useState, useRef } from 'react';
import Image from 'next/image';
import { Image as ImageIcon, Music, Calendar, BarChart3, Loader2, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useCreatePost } from '@/hooks/useSocial';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

interface CreatePostProps {
  onPostCreated?: () => void;
}

export function CreatePost({ onPostCreated }: CreatePostProps) {
  const { user } = useAuthStore();
  const createPost = useCreatePost();
  const [content, setContent] = useState('');
  const [postType, setPostType] = useState<'status' | 'track_share' | 'event' | 'milestone'>('status');
  const [mediaFile, setMediaFile] = useState<File | null>(null);
  const [mediaPreview, setMediaPreview] = useState<string | null>(null);
  const [mediaType, setMediaType] = useState<'image' | 'video' | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const maxLength = 1000;
  const remainingChars = maxLength - content.length;

  const handleMediaSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const isImage = file.type.startsWith('image/');
    const isVideo = file.type.startsWith('video/');

    if (!isImage && !isVideo) {
      alert('Only images and videos are supported');
      return;
    }

    const maxSize = isVideo ? 100 * 1024 * 1024 : 10 * 1024 * 1024;
    if (file.size > maxSize) {
      alert(`File too large. Max ${isVideo ? '100MB' : '10MB'}`);
      return;
    }

    setMediaFile(file);
    setMediaType(isImage ? 'image' : 'video');
    setMediaPreview(URL.createObjectURL(file));
  };

  const handleRemoveMedia = () => {
    setMediaFile(null);
    setMediaPreview(null);
    setMediaType(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;

    try {
      let mediaUrl: string | undefined;

      // Upload media if selected
      if (mediaFile) {
        setUploading(true);
        const formData = new FormData();
        formData.append('file', mediaFile);

        const response = await fetch('/api/v1/social/posts/upload', {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) throw new Error('Upload failed');
        const data = await response.json();
        mediaUrl = data.media_url;
        setUploading(false);
      }

      await createPost.mutateAsync({
        postType,
        content: content.trim(),
        visibility: 'public',
        media_url: mediaUrl,
      });

      setContent('');
      setPostType('status');
      handleRemoveMedia();
      onPostCreated?.();
    } catch (error) {
      setUploading(false);
      console.error('Failed to create post:', error);
    }
  };

  if (!user) return null;

  return (
    <div className="bg-card border rounded-lg p-4">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* User Avatar and Input */}
        <div className="flex items-start space-x-3">
          {/* Avatar */}
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden flex-shrink-0">
            {user.avatar ? (
              <Image
                src={user.avatar}
                alt={user.fullName}
                width={40}
                height={40}
                className="object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-white font-semibold text-sm">
                {user?.fullName?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
              </div>
            )}
          </div>

          {/* Textarea */}
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="What's on your mind?"
            className="flex-1 resize-none border-none focus:outline-none focus:ring-0 bg-transparent text-foreground placeholder:text-muted-foreground min-h-[80px]"
            maxLength={maxLength}
            disabled={createPost.isPending}
          />
        </div>

        {/* Media Preview */}
        {mediaPreview && (
          <div className="relative rounded-lg overflow-hidden border">
            {mediaType === 'image' ? (
              <Image src={mediaPreview} alt="Preview" width={400} height={300} className="w-full object-cover max-h-64" />
            ) : (
              <video src={mediaPreview} className="w-full max-h-64" controls />
            )}
            <button
              type="button"
              onClick={handleRemoveMedia}
              className="absolute top-2 right-2 p-1 bg-black/50 rounded-full text-white hover:bg-black/70"
              aria-label="Remove media"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Post Type Selector */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-2">
          <button
            type="button"
            onClick={() => setPostType('status')}
            className={cn(
              'flex items-center space-x-2 px-3 py-1.5 rounded-full border text-sm transition-colors',
              postType === 'status'
                ? 'bg-primary text-primary-foreground border-primary'
                : 'hover:bg-accent'
            )}
          >
            <span>Status</span>
          </button>

          <button
            type="button"
            onClick={() => setPostType('track_share')}
            className={cn(
              'flex items-center space-x-2 px-3 py-1.5 rounded-full border text-sm transition-colors',
              postType === 'track_share'
                ? 'bg-primary text-primary-foreground border-primary'
                : 'hover:bg-accent'
            )}
          >
            <Music className="w-4 h-4" />
            <span>Share Track</span>
          </button>

          <button
            type="button"
            onClick={() => setPostType('event')}
            className={cn(
              'flex items-center space-x-2 px-3 py-1.5 rounded-full border text-sm transition-colors',
              postType === 'event'
                ? 'bg-primary text-primary-foreground border-primary'
                : 'hover:bg-accent'
            )}
          >
            <Calendar className="w-4 h-4" />
            <span>Event</span>
          </button>

          <button
            type="button"
            onClick={() => setPostType('milestone')}
            className={cn(
              'flex items-center space-x-2 px-3 py-1.5 rounded-full border text-sm transition-colors',
              postType === 'milestone'
                ? 'bg-primary text-primary-foreground border-primary'
                : 'hover:bg-accent'
            )}
          >
            <BarChart3 className="w-4 h-4" />
            <span>Milestone</span>
          </button>
        </div>

        {/* Bottom Bar */}
        <div className="flex items-center justify-between pt-2 border-t">
          {/* Media Buttons */}
          <div className="flex items-center space-x-1">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*,video/*"
              className="hidden"
              onChange={handleMediaSelect}
            />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              title="Add image or video"
              onClick={() => fileInputRef.current?.click()}
              disabled={createPost.isPending || uploading}
            >
              <ImageIcon className="w-5 h-5 text-muted-foreground" />
            </Button>
          </div>

          {/* Character Counter and Post Button */}
          <div className="flex items-center space-x-3">
            <span
              className={cn(
                'text-sm',
                remainingChars < 50
                  ? 'text-amber-500'
                  : remainingChars < 0
                  ? 'text-destructive'
                  : 'text-muted-foreground'
              )}
            >
              {remainingChars}
            </span>

            <Button
              type="submit"
              disabled={!content.trim() || remainingChars < 0 || createPost.isPending || uploading}
            >
              {uploading ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Uploading...</>
              ) : createPost.isPending ? (
                <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Posting...</>
              ) : (
                'Post'
              )}
            </Button>
          </div>
        </div>
      </form>
    </div>
  );
}
