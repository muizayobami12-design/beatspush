'use client';

import { useState, useRef, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import Image from 'next/image';
import { Camera, Loader2, Sparkles, Lightbulb } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { useUpdateProfile, useUploadAvatar, useUploadCoverPhoto } from '@/hooks/useProfile';
import { useToast } from '@/hooks/useToast';
import type { Profile } from '@/types';
import { cn } from '@/lib/utils';

const profileSchema = z.object({
  fullName: z.string().min(2, 'Name must be at least 2 characters'),
  bio: z.string().max(500, 'Bio must be 500 characters or less').optional(),
  location: z.string().optional(),
  website: z.string().url('Must be a valid URL').optional().or(z.literal('')),
  socialLinks: z.object({
    twitter: z.string().optional(),
    instagram: z.string().optional(),
    facebook: z.string().optional(),
    youtube: z.string().optional(),
    spotify: z.string().optional(),
    soundcloud: z.string().optional(),
  }).optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

interface ProfileEditorProps {
  profile: Profile;
  onSuccess?: () => void;
  bioValue?: string;
  onBioChange?: (value: string) => void;
}

export function ProfileEditor({ profile, onSuccess, bioValue, onBioChange }: ProfileEditorProps) {
  const { toast } = useToast();
  const [avatarPreview, setAvatarPreview] = useState<string | null>(profile.avatar || null);
  const [coverPreview, setCoverPreview] = useState<string | null>(profile.coverPhoto || null);
  const avatarInputRef = useRef<HTMLInputElement>(null);
  const coverInputRef = useRef<HTMLInputElement>(null);

  const updateProfile = useUpdateProfile();
  const uploadAvatar = useUploadAvatar();
  const uploadCover = useUploadCoverPhoto();

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors, isDirty },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      fullName: profile.fullName,
      bio: bioValue || profile.bio || '',
      location: profile.location || '',
      website: profile.website || '',
      socialLinks: profile.socialLinks || {},
    },
  });

  const bioLength = watch('bio')?.length || 0;

  // Update bio field when bioValue prop changes (from AI chat)
  useEffect(() => {
    if (bioValue !== undefined && bioValue !== watch('bio')) {
      setValue('bio', bioValue, { shouldDirty: true, shouldValidate: true });
    }
  }, [bioValue, setValue, watch]);

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Avatar must be less than 2MB',
        variant: 'error',
      });
      return;
    }

    // Preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setAvatarPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload
    try {
      await uploadAvatar.mutateAsync(file);
      toast({
        title: 'Success',
        description: 'Avatar updated successfully',
        variant: 'success',
      });
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: 'Failed to upload avatar. Please try again.',
        variant: 'error',
      });
    }
  };

  const handleCoverChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file size (max 2MB)
    if (file.size > 2 * 1024 * 1024) {
      toast({
        title: 'File too large',
        description: 'Cover photo must be less than 2MB',
        variant: 'error',
      });
      return;
    }

    // Preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setCoverPreview(reader.result as string);
    };
    reader.readAsDataURL(file);

    // Upload
    try {
      await uploadCover.mutateAsync(file);
      toast({
        title: 'Success',
        description: 'Cover photo updated successfully',
        variant: 'success',
      });
    } catch (error) {
      toast({
        title: 'Upload failed',
        description: 'Failed to upload cover photo. Please try again.',
        variant: 'error',
      });
    }
  };

  const onSubmit = async (data: ProfileFormData) => {
    try {
      await updateProfile.mutateAsync(data);
      toast({
        title: 'Profile updated',
        description: 'Your profile has been updated successfully',
        variant: 'success',
      });
      onSuccess?.();
    } catch (error) {
      toast({
        title: 'Update failed',
        description: 'Failed to update profile. Please try again.',
        variant: 'error',
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
      {/* Cover Photo */}
      <div>
        <Label>Cover Photo</Label>
        <div className="mt-2 relative h-48 bg-gradient-to-br from-[#667eea] to-[#764ba2] rounded-lg overflow-hidden group">
          {coverPreview && (
            <Image
              src={coverPreview}
              alt="Cover photo"
              fill
              className="object-cover"
            />
          )}
          <button
            type="button"
            onClick={() => coverInputRef.current?.click()}
            className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
          >
            <Camera className="w-8 h-8 text-white" />
          </button>
          <input
            ref={coverInputRef}
            type="file"
            accept="image/*"
            className="hidden"
            onChange={handleCoverChange}
          />
        </div>
      </div>

      {/* Avatar */}
      <div>
        <Label>Profile Picture</Label>
        <div className="mt-2 flex items-center space-x-4">
          <div className="relative w-24 h-24 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden group">
            {avatarPreview ? (
              <Image
                src={avatarPreview}
                alt="Avatar"
                width={96}
                height={96}
                className="object-cover w-full h-full"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-white text-2xl font-bold">
                {profile?.fullName?.charAt(0)?.toUpperCase() || profile?.email?.charAt(0)?.toUpperCase() || 'U'}
              </div>
            )}
            <button
              type="button"
              onClick={() => avatarInputRef.current?.click()}
              className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center"
            >
              <Camera className="w-6 h-6 text-white" />
            </button>
            <input
              ref={avatarInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleAvatarChange}
            />
          </div>
          <div className="text-sm text-muted-foreground">
            <p>Recommended: Square image, at least 400x400px</p>
            <p>Max file size: 2MB</p>
          </div>
        </div>
      </div>

      {/* Basic Info */}
      <div className="space-y-4">
        <div>
          <Label htmlFor="fullName">Full Name *</Label>
          <Input
            id="fullName"
            {...register('fullName')}
          />
          {errors.fullName && (
            <p className="text-sm text-destructive mt-1">{errors.fullName.message}</p>
          )}
        </div>

        <div>
          <Label htmlFor="bio">Bio</Label>
          <Textarea
            id="bio"
            {...register('bio', {
              onChange: (e) => {
                if (onBioChange) {
                  onBioChange(e.target.value);
                }
              },
            })}
            rows={4}
            placeholder="Tell us about yourself..."
            className={cn(errors.bio && 'border-destructive')}
          />
          <div className="flex justify-between mt-1">
            <p className="text-sm text-muted-foreground">
              {errors.bio?.message}
            </p>
            <p className={cn(
              'text-sm',
              bioLength > 500 ? 'text-destructive' : 'text-muted-foreground'
            )}>
              {bioLength}/500
            </p>
          </div>

          {/* AI Bio Generation Buttons */}
          <AIBioButtons onBioUpdate={(bio) => {
            setValue('bio', bio, { shouldDirty: true, shouldValidate: true });
            onBioChange?.(bio);
          }} />
        </div>

        <div>
          <Label htmlFor="location">Location</Label>
          <Input
            id="location"
            {...register('location')}
            placeholder="e.g., Lagos, Nigeria"
          />
        </div>

        <div>
          <Label htmlFor="website">Website</Label>
          <Input
            id="website"
            {...register('website')}
            type="url"
            placeholder="https://example.com"
          />
          {errors.website && (
            <p className="text-sm text-destructive mt-1">{errors.website.message}</p>
          )}
        </div>
      </div>

      {/* Social Links */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Social Links</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <Label htmlFor="twitter">Twitter</Label>
            <Input
              id="twitter"
              {...register('socialLinks.twitter')}
              placeholder="@username"
            />
          </div>

          <div>
            <Label htmlFor="instagram">Instagram</Label>
            <Input
              id="instagram"
              {...register('socialLinks.instagram')}
              placeholder="@username"
            />
          </div>

          <div>
            <Label htmlFor="facebook">Facebook</Label>
            <Input
              id="facebook"
              {...register('socialLinks.facebook')}
              placeholder="username"
            />
          </div>

          <div>
            <Label htmlFor="youtube">YouTube</Label>
            <Input
              id="youtube"
              {...register('socialLinks.youtube')}
              placeholder="channel"
            />
          </div>

          <div>
            <Label htmlFor="spotify">Spotify</Label>
            <Input
              id="spotify"
              {...register('socialLinks.spotify')}
              placeholder="artist ID"
            />
          </div>

          <div>
            <Label htmlFor="soundcloud">SoundCloud</Label>
            <Input
              id="soundcloud"
              {...register('socialLinks.soundcloud')}
              placeholder="username"
            />
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-end space-x-3 pt-6 border-t">
        <Button
          type="submit"
          disabled={!isDirty || updateProfile.isPending}
        >
          {updateProfile.isPending && (
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
          )}
          Save Changes
        </Button>
      </div>
    </form>
  );
}

/**
 * AIBioButtons - AI-powered quick action buttons for bio generation
 * Allows users to generate bio variations with AI assistance
 */
function AIBioButtons({ onBioUpdate }: { onBioUpdate: (bio: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2 mt-3">
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => {
          // This button will be handled by useProfileChat hook in the profile page
          const event = new CustomEvent('ai:generate-bio', { detail: { action: 'write' } });
          document.dispatchEvent(event);
        }}
        className="text-xs"
      >
        <Sparkles className="w-3 h-3 mr-1" />
        Generate Bio
      </Button>
      <Button
        type="button"
        variant="outline"
        size="sm"
        onClick={() => {
          const event = new CustomEvent('ai:generate-bio', { detail: { action: 'improve' } });
          document.dispatchEvent(event);
        }}
        className="text-xs"
      >
        <Lightbulb className="w-3 h-3 mr-1" />
        Improve Bio
      </Button>
    </div>
  );
}
