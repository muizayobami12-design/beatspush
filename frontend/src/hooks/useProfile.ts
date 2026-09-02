import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { profileService, type UpdateProfileData } from '@/services/profileService';
import type { Profile } from '@/types';

/**
 * Hook to fetch a user profile by username
 */
export function useProfile(username: string) {
  return useQuery({
    queryKey: ['profile', username],
    queryFn: () => profileService.getProfile(username),
    enabled: !!username,
  });
}

/**
 * Hook to update the current user's profile with optimistic updates
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProfileData) => profileService.updateProfile(data),
    onMutate: async (newData) => {
      // Cancel any outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['profile', 'me'] });

      // Snapshot the previous value
      const previousProfile = queryClient.getQueryData(['profile', 'me']);

      // Optimistically update
      queryClient.setQueryData(['profile', 'me'], (old: Profile | undefined) => {
        if (!old) return old;
        return { ...old, ...newData };
      });

      return { previousProfile };
    },
    onError: (_error, _newData, context) => {
      // Rollback on error
      if (context?.previousProfile) {
        queryClient.setQueryData(['profile', 'me'], context.previousProfile);
      }
    },
    onSettled: () => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['profile', 'me'] });
    },
  });
}

/**
 * Hook to upload avatar
 */
export function useUploadAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => profileService.uploadAvatar(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });
}

/**
 * Hook to upload cover photo
 */
export function useUploadCoverPhoto() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => profileService.uploadCoverPhoto(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile'] });
    },
  });
}

/**
 * Hook to follow/unfollow a user
 */
export function useFollowUser(username: string) {
  const queryClient = useQueryClient();

  const followMutation = useMutation({
    mutationFn: () => profileService.followUser(username),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', username] });
    },
  });

  const unfollowMutation = useMutation({
    mutationFn: () => profileService.unfollowUser(username),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['profile', username] });
    },
  });

  return {
    follow: followMutation.mutate,
    unfollow: unfollowMutation.mutate,
    isFollowing: followMutation.isPending,
    isUnfollowing: unfollowMutation.isPending,
  };
}

/**
 * Hook to fetch followers
 */
export function useFollowers(username: string, page = 1, limit = 20) {
  return useQuery({
    queryKey: ['followers', username, page, limit],
    queryFn: () => profileService.getFollowers(username, page, limit),
    enabled: !!username,
  });
}

/**
 * Hook to fetch following
 */
export function useFollowing(username: string, page = 1, limit = 20) {
  return useQuery({
    queryKey: ['following', username, page, limit],
    queryFn: () => profileService.getFollowing(username, page, limit),
    enabled: !!username,
  });
}
