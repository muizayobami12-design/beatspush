'use client';

import { useState } from 'react';
import Image from 'next/image';
import { MapPin, Link as LinkIcon, Users, Music, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useFollowUser } from '@/hooks/useProfile';
import type { Profile } from '@/types';
import { cn } from '@/lib/utils';

interface ProfileHeaderProps {
  profile: Profile;
  isOwnProfile?: boolean;
  onEditClick?: () => void;
}

export function ProfileHeader({ profile, isOwnProfile, onEditClick }: ProfileHeaderProps) {
  const { follow, unfollow, isFollowing, isUnfollowing } = useFollowUser(profile.username);
  const [isFollowingState, setIsFollowingState] = useState(profile.isFollowing || false);

  const handleFollowToggle = () => {
    if (isFollowingState) {
      unfollow();
      setIsFollowingState(false);
    } else {
      follow();
      setIsFollowingState(true);
    }
  };

  const roleBadgeColors = {
    artist: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
    producer: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    dj: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    fan: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200',
    admin: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
  };

  return (
    <div className="w-full">
      {/* Cover Photo */}
      <div className="relative h-48 md:h-64 bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden">
        {profile.coverPhotoUrl ? (
          <Image
            src={profile.coverPhotoUrl}
            alt="Cover photo"
            fill
            className="object-cover"
            priority
          />
        ) : null}
      </div>

      {/* Profile Info */}
      <div className="relative px-4 md:px-6 pb-6">
        {/* Avatar */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between -mt-12 md:-mt-16">
          <div className="flex items-end space-x-4">
            <div className="relative">
              <div className="w-24 h-24 md:w-32 md:h-32 rounded-full border-4 border-background bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden">
                {profile.avatarUrl ? (
                  <Image
                    src={profile.avatarUrl}
                    alt={profile.fullName}
                    width={128}
                    height={128}
                    className="object-cover w-full h-full"
                    priority
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-white text-3xl md:text-4xl font-bold">
                    {profile?.fullName?.charAt(0)?.toUpperCase() || profile?.email?.charAt(0)?.toUpperCase() || 'U'}
                  </div>
                )}
              </div>
            </div>

            <div className="pb-2">
              <h1 className="text-2xl md:text-3xl font-bold">{profile.fullName}</h1>
              <p className="text-muted-foreground">@{profile.username}</p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="mt-4 md:mt-0 md:pb-2">
            {isOwnProfile ? (
              <Button onClick={onEditClick} variant="outline">
                Edit Profile
              </Button>
            ) : (
              <Button
                onClick={handleFollowToggle}
                disabled={isFollowing || isUnfollowing}
                variant={isFollowingState ? 'outline' : 'default'}
              >
                {isFollowingState ? 'Following' : 'Follow'}
              </Button>
            )}
          </div>
        </div>

        {/* Role Badge */}
        <div className="mt-4">
          <span
            className={cn(
              'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
              roleBadgeColors[profile.role as keyof typeof roleBadgeColors]
            )}
          >
            {profile?.role?.charAt(0)?.toUpperCase() + (profile?.role?.slice(1) || '') || 'User'}
          </span>
        </div>

        {/* Bio */}
        {profile.bio && (
          <p className="mt-4 text-foreground max-w-2xl">{profile.bio}</p>
        )}

        {/* Stats & Info */}
        <div className="mt-6 flex flex-wrap gap-6">
          <div className="flex items-center space-x-2 text-sm">
            <Users className="w-4 h-4 text-muted-foreground" />
            <span>
              <strong className="font-semibold">{profile.followersCount || 0}</strong>{' '}
              <span className="text-muted-foreground">Followers</span>
            </span>
          </div>
          
          <div className="flex items-center space-x-2 text-sm">
            <Users className="w-4 h-4 text-muted-foreground" />
            <span>
              <strong className="font-semibold">{profile.followingCount || 0}</strong>{' '}
              <span className="text-muted-foreground">Following</span>
            </span>
          </div>

          {profile.role !== 'fan' && (
            <div className="flex items-center space-x-2 text-sm">
              <Music className="w-4 h-4 text-muted-foreground" />
              <span>
                <strong className="font-semibold">{profile.beatsCount || 0}</strong>{' '}
                <span className="text-muted-foreground">Beats</span>
              </span>
            </div>
          )}

          {profile.location && (
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <MapPin className="w-4 h-4" />
              <span>{profile.location}</span>
            </div>
          )}

          {profile.createdAt && (
            <div className="flex items-center space-x-2 text-sm text-muted-foreground">
              <Calendar className="w-4 h-4" />
              <span>
                Joined {new Date(profile.createdAt).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })}
              </span>
            </div>
          )}
        </div>

        {/* Social Links */}
        {profile.socialLinks && Object.keys(profile.socialLinks).length > 0 && (
          <div className="mt-4 flex items-center space-x-3">
            {profile.website && (
              <a
                href={profile.website}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-primary transition-colors"
                aria-label="Website"
              >
                <LinkIcon className="w-5 h-5" />
              </a>
            )}
            {/* Add more social links as needed */}
          </div>
        )}
      </div>
    </div>
  );
}
