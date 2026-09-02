/**
 * React Query hooks for user operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  loginUser,
  registerUser,
  logoutUser,
  refreshToken,
  getCurrentUser,
  getUserProfile,
  updateUserProfile,
  uploadAvatar,
  uploadCover,
  searchUsers,
  getUserFollowers,
  getUserFollowing,
  followUser,
  unfollowUser,
  checkFollowStatus,
  blockUser,
  unblockUser,
  getBlockedUsers,
  getUserStats,
  changePassword,
  requestPasswordReset,
  resetPassword,
  verifyEmail,
  resendVerificationEmail,
  AuthCredentials,
  RegistrationData,
  UpdateProfileData,
  UserProfile,
  UsersResponse,
  UserStats,
  FollowStatus,
} from '@/services/userService';
import { QUERY_KEYS, PAGINATION } from '@/lib/constants';

/**
 * Fetch current user
 */
export function useCurrentUser(enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.USER, 'current'],
    queryFn: () => getCurrentUser(),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Fetch user profile by ID or username
 */
export function useUserProfile(userIdOrUsername: string, enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.PROFILE, userIdOrUsername],
    queryFn: () => getUserProfile(userIdOrUsername),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
}

/**
 * Search users
 */
export function useSearchUsers(
  query: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: [QUERY_KEYS.USER, 'search', query, page],
    queryFn: () => searchUsers(query, page, page_size),
    enabled: enabled && query.length > 0,
    staleTime: 3 * 60 * 1000, // 3 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch user followers
 */
export function useUserFollowers(
  userId: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: [QUERY_KEYS.USER, userId, 'followers', page],
    queryFn: () => getUserFollowers(userId, page, page_size),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
}

/**
 * Fetch user following list
 */
export function useUserFollowing(
  userId: string,
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: [QUERY_KEYS.USER, userId, 'following', page],
    queryFn: () => getUserFollowing(userId, page, page_size),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
}

/**
 * Check follow status
 */
export function useFollowStatus(userId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.USER, userId, 'follow-status'],
    queryFn: () => checkFollowStatus(userId),
    enabled,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch user statistics
 */
export function useUserStats(userId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.USER, userId, 'stats'],
    queryFn: () => getUserStats(userId),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Fetch blocked users
 */
export function useBlockedUsers(
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: [QUERY_KEYS.USER, 'me', 'blocked', page],
    queryFn: () => getBlockedUsers(page, page_size),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
}

/**
 * Login mutation
 */
export function useLogin() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: AuthCredentials) => loginUser(credentials),
    onSuccess: (data) => {
      // Invalidate user query to refetch current user
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'current'] });
    },
  });
}

/**
 * Register mutation
 */
export function useRegister() {
  return useMutation({
    mutationFn: (data: RegistrationData) => registerUser(data),
  });
}

/**
 * Logout mutation
 */
export function useLogout() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => logoutUser(),
    onSuccess: () => {
      // Clear all user-related queries
      queryClient.clear();
    },
  });
}

/**
 * Refresh token mutation
 */
export function useRefreshToken() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (refreshToken: string) => refreshToken(refreshToken),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'current'] });
    },
  });
}

/**
 * Update profile mutation
 */
export function useUpdateProfile() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: UpdateProfileData) => updateUserProfile(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'current'] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PROFILE] });
    },
  });
}

/**
 * Upload avatar mutation
 */
export function useUploadAvatar() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadAvatar(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'current'] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PROFILE] });
    },
  });
}

/**
 * Upload cover mutation
 */
export function useUploadCover() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (file: File) => uploadCover(file),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'current'] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.PROFILE] });
    },
  });
}

/**
 * Follow user mutation
 */
export function useFollowUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => followUser(userId),
    onSuccess: () => {
      // Invalidate followers/following queries
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER] });
    },
  });
}

/**
 * Unfollow user mutation
 */
export function useUnfollowUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => unfollowUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER] });
    },
  });
}

/**
 * Block user mutation
 */
export function useBlockUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => blockUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'me', 'blocked'] });
    },
  });
}

/**
 * Unblock user mutation
 */
export function useUnblockUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => unblockUser(userId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'me', 'blocked'] });
    },
  });
}

/**
 * Change password mutation
 */
export function useChangePassword() {
  return useMutation({
    mutationFn: ({
      oldPassword,
      newPassword,
    }: {
      oldPassword: string;
      newPassword: string;
    }) => changePassword(oldPassword, newPassword),
  });
}

/**
 * Request password reset mutation
 */
export function useRequestPasswordReset() {
  return useMutation({
    mutationFn: (email: string) => requestPasswordReset(email),
  });
}

/**
 * Reset password mutation
 */
export function useResetPassword() {
  return useMutation({
    mutationFn: ({ token, newPassword }: { token: string; newPassword: string }) =>
      resetPassword(token, newPassword),
  });
}

/**
 * Verify email mutation
 */
export function useVerifyEmail() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (token: string) => verifyEmail(token),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.USER, 'current'] });
    },
  });
}

/**
 * Resend verification email mutation
 */
export function useResendVerificationEmail() {
  return useMutation({
    mutationFn: () => resendVerificationEmail(),
  });
}

export default {
  useCurrentUser,
  useUserProfile,
  useSearchUsers,
  useUserFollowers,
  useUserFollowing,
  useFollowStatus,
  useUserStats,
  useBlockedUsers,
  useLogin,
  useRegister,
  useLogout,
  useRefreshToken,
  useUpdateProfile,
  useUploadAvatar,
  useUploadCover,
  useFollowUser,
  useUnfollowUser,
  useBlockUser,
  useUnblockUser,
  useChangePassword,
  useRequestPasswordReset,
  useResetPassword,
  useVerifyEmail,
  useResendVerificationEmail,
};
