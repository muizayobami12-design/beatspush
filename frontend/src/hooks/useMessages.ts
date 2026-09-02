/**
 * Custom hooks for managing messages with React Query.
 */

import { useMutation, useQueryClient, useInfiniteQuery, useQuery } from '@tanstack/react-query';
import messagingService from '@/services/messagingService';
import type { Message } from '@/services/messagingService';
import { useToast } from '@/hooks/useToast';

// ─── Query keys ──────────────────────────────────────────────────────────────

export const messageKeys = {
  all: ['messages'] as const,
  thread: (conversationId: string) =>
    ['messages', 'thread', conversationId] as const,
};

// ─── Hooks ───────────────────────────────────────────────────────────────────

/**
 * Infinite-scroll messages for a conversation thread.
 * Fetches oldest-first pages; prepend pages load older history.
 */
export function useMessages(conversationId: string | null, page_size = 50) {
  return useInfiniteQuery({
    queryKey: messageKeys.thread(conversationId ?? ''),
    queryFn: ({ pageParam = undefined }: { pageParam?: string }) =>
      messagingService.getMessages(conversationId!, {
        page_size,
        cursor: pageParam,
      }),
    enabled: !!conversationId,
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.next_cursor ?? undefined,
    staleTime: 1000 * 30,
    // Do NOT auto-refetch — WebSocket events drive live updates
    refetchInterval: false,
  });
}

/**
 * Mutation to send a new message.
 * On success it invalidates the thread cache so the new message appears.
 */
export function useSendMessage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (data: { conversation_id: string; content: string }) =>
      messagingService.sendMessage({ conversation_id: data.conversation_id, content: data.content }),
    onSuccess: (_newMessage: Message, variables) => {
      queryClient.invalidateQueries({
        queryKey: messageKeys.thread(variables.conversation_id),
      });
      // Also refresh conversation list so last_message preview updates
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
    onError: (error: unknown) => {
      const msg = error instanceof Error ? error.message : 'Please try again';
      toast({
        title: 'Failed to send message',
        description: msg,
        variant: 'error',
      });
    },
  });
}

/**
 * Mark all messages in a conversation as read.
 */
export function useMarkConversationRead() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (conversationId: string) =>
      messagingService.markConversationRead(conversationId),
    onSuccess: (_, conversationId) => {
      queryClient.invalidateQueries({ queryKey: ['conversations', 'single', conversationId] });
      queryClient.invalidateQueries({ queryKey: ['conversations'] });
    },
  });
}

/**
 * Mark a single message as read.
 */
export function useMarkMessageRead() {
  return useMutation({
    mutationFn: (messageId: string) =>
      messagingService.markMessageRead(messageId),
  });
}

/**
 * Soft-delete a message.
 */
export function useDeleteMessage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (messageId: string) => messagingService.deleteMessage(messageId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: messageKeys.all });
      toast({ title: 'Message deleted', variant: 'success' });
    },
    onError: (error: unknown) => {
      const msg = error instanceof Error ? error.message : 'Please try again';
      toast({ title: 'Failed to delete message', description: msg, variant: 'error' });
    },
  });
}

/**
 * Edit a message (within the 15-minute window).
 */
export function useEditMessage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: ({ messageId, content }: { messageId: string; content: string }) =>
      messagingService.editMessage(messageId, content),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: messageKeys.all });
    },
    onError: (error: unknown) => {
      const msg = error instanceof Error ? error.message : 'Please try again';
      toast({ title: 'Failed to edit message', description: msg, variant: 'error' });
    },
  });
}
