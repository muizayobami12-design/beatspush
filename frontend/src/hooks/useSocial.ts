/**
 * Custom hooks for social feed with React Query
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  useInfiniteQuery,
} from '@tanstack/react-query';
import socialService from '@/services/socialService';
import { useToast } from '@/hooks/useToast';

// Placeholder types for feed functionality (not yet implemented in socialService)
type CreatePostData = any;
type UpdatePostData = any;
type CreateCommentData = any;

// ==================== FEED HOOKS ====================

export function useFeed(
  feedType: 'following' | 'discover' | 'trending' = 'following',
  pageSize = 20
) {
  return useInfiniteQuery({
    queryKey: ['feed', feedType],
    queryFn: ({ pageParam = 1 }) =>
      socialService.getFeed(feedType, pageParam, pageSize),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.hasMore) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    staleTime: 1000 * 60, // 1 minute
    refetchOnWindowFocus: true,
  });
}

export function useUserPosts(userId: string | null, pageSize = 20) {
  return useInfiniteQuery({
    queryKey: ['userPosts', userId],
    queryFn: ({ pageParam = 1 }) =>
      socialService.getUserPosts(userId!, pageParam, pageSize),
    enabled: !!userId,
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.hasMore) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function usePost(postId: string | null) {
  return useQuery({
    queryKey: ['post', postId],
    queryFn: () => socialService.getPost(postId!),
    enabled: !!postId,
    staleTime: 1000 * 30, // 30 seconds
  });
}

// ==================== POST MUTATIONS ====================

export function useCreatePost() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: CreatePostData) => socialService.createPost(data),
    onSuccess: () => {
      // Invalidate all feeds
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['userPosts'] });

      toast({
        title: 'Post created',
        description: 'Your post has been shared',
        variant: 'success',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to create post',
        description: error.message || 'Please try again',
        variant: 'error',
      });
    },
  });
}

export function useUpdatePost() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      postId,
      data,
    }: {
      postId: string;
      data: UpdatePostData;
    }) => socialService.updatePost(postId, data),
    onSuccess: (_, variables) => {
      // Invalidate specific post and feeds
      queryClient.invalidateQueries({ queryKey: ['post', variables.postId] });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['userPosts'] });

      toast({
        title: 'Post updated',
        variant: 'success',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to update post',
        description: error.message || 'Please try again',
        variant: 'error',
      });
    },
  });
}

export function useDeletePost() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (postId: string) => socialService.deletePost(postId),
    onSuccess: () => {
      // Invalidate feeds
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['userPosts'] });

      toast({
        title: 'Post deleted',
        variant: 'success',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to delete post',
        description: error.message || 'Please try again',
        variant: 'error',
      });
    },
  });
}

// ==================== LIKE MUTATION ====================

export function useToggleLike() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (postId: string) => socialService.toggleLike(postId),
    onMutate: async (postId) => {
      // Cancel outgoing refetches
      await queryClient.cancelQueries({ queryKey: ['feed'] });
      await queryClient.cancelQueries({ queryKey: ['post', postId] });

      // Snapshot previous value
      const previousFeeds = queryClient.getQueriesData({ queryKey: ['feed'] });
      const previousPost = queryClient.getQueryData(['post', postId]);

      // Optimistically update
      queryClient.setQueriesData({ queryKey: ['feed'] }, (old: any) => {
        if (!old) return old;

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            posts: page.posts.map((post: any) =>
              post.id === postId
                ? {
                    ...post,
                    isLiked: !post.isLiked,
                    likeCount: post.isLiked
                      ? post.likeCount - 1
                      : post.likeCount + 1,
                  }
                : post
            ),
          })),
        };
      });

      return { previousFeeds, previousPost };
    },
    onError: (_err, _postId, context) => {
      // Rollback on error
      if (context?.previousFeeds) {
        context.previousFeeds.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: (_, __, postId) => {
      // Refetch after mutation
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['post', postId] });
    },
  });
}

// ==================== COMMENT MUTATIONS ====================

export function useCreateComment() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({
      postId,
      data,
    }: {
      postId: string;
      data: CreateCommentData;
    }) => socialService.createComment(postId, data),
    onSuccess: (_, variables) => {
      // Invalidate post to refetch with new comment
      queryClient.invalidateQueries({ queryKey: ['post', variables.postId] });

      // Update comment count in feeds
      queryClient.invalidateQueries({ queryKey: ['feed'] });

      toast({
        title: 'Comment added',
        variant: 'success',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to add comment',
        description: error.message || 'Please try again',
        variant: 'error',
      });
    },
  });
}

export function useDeleteComment() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (commentId: string) => socialService.deleteComment(commentId),
    onSuccess: () => {
      // Invalidate all posts to update comment counts
      queryClient.invalidateQueries({ queryKey: ['post'] });
      queryClient.invalidateQueries({ queryKey: ['feed'] });

      toast({
        title: 'Comment deleted',
        variant: 'success',
      });
    },
    onError: (error: any) => {
      toast({
        title: 'Failed to delete comment',
        description: error.message || 'Please try again',
        variant: 'error',
      });
    },
  });
}

// ==================== FOLLOW MUTATION ====================

export function useToggleFollow() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (userId: string) => socialService.toggleFollow(userId),
    onSuccess: (_, userId) => {
      // Invalidate follow-related queries
      queryClient.invalidateQueries({ queryKey: ['followers', userId] });
      queryClient.invalidateQueries({ queryKey: ['following'] });
      queryClient.invalidateQueries({ queryKey: ['followStats', userId] });
      queryClient.invalidateQueries({ queryKey: ['feed'] });
    },
  });
}

// ==================== BOOKMARK MUTATION ====================

export function useToggleBookmark() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (postId: string) => socialService.toggleBookmark(postId),
    onMutate: async (postId) => {
      // Optimistically update bookmark status in feeds
      await queryClient.cancelQueries({ queryKey: ['feed'] });

      const previousFeeds = queryClient.getQueriesData({ queryKey: ['feed'] });

      queryClient.setQueriesData({ queryKey: ['feed'] }, (old: any) => {
        if (!old) return old;

        return {
          ...old,
          pages: old.pages.map((page: any) => ({
            ...page,
            posts: page.posts.map((post: any) =>
              post.id === postId
                ? { ...post, isBookmarked: !post.isBookmarked }
                : post
            ),
          })),
        };
      });

      return { previousFeeds };
    },
    onError: (_err, _postId, context) => {
      // Rollback on error
      if (context?.previousFeeds) {
        context.previousFeeds.forEach(([queryKey, data]) => {
          queryClient.setQueryData(queryKey, data);
        });
      }
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ['feed'] });
      queryClient.invalidateQueries({ queryKey: ['bookmarks'] });
    },
  });
}

// ==================== OTHER QUERIES ====================

export function useBookmarks(pageSize = 20) {
  return useInfiniteQuery({
    queryKey: ['bookmarks'],
    queryFn: ({ pageParam = 1 }) =>
      socialService.getBookmarks(pageParam, pageSize),
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.hasMore) {
        return lastPage.page + 1;
      }
      return undefined;
    },
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useFollowSuggestions(
  type: 'all' | 'similar' | 'trending' | 'mutual' = 'all',
  limit = 10
) {
  return useQuery({
    queryKey: ['followSuggestions', type, limit],
    queryFn: () => socialService.getFollowSuggestions(type, limit),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useTrendingCreators(
  genre?: string,
  location?: string,
  limit = 20
) {
  return useQuery({
    queryKey: ['trendingCreators', genre, location, limit],
    queryFn: () => socialService.getTrendingCreators(genre, location, limit),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
}
