/**
 * Custom hooks for managing conversations with React Query.
 * Wraps messagingService (snake_case API) for convenient component use.
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import messagingService from '@/services/messagingService';
import type { Conversation } from '@/services/messagingService';
import { useToast } from '@/hooks/useToast';

// ─── Query keys ─────────────────────────────────────────────────────────────

export const conversationKeys = {
  all: ['conversations'] as const,
  list: (params: object) => ['conversations', 'list', params] as const,
  single: (id: string) => ['conversations', 'single', id] as const,
};

// ─── Hooks ───────────────────────────────────────────────────────────────────

export function useConversations(params?: {
  page?: number;
  page_size?: number;
  unread_only?: boolean;
  search?: string;
}) {
  return useQuery({
    queryKey: conversationKeys.list(params ?? {}),
    queryFn: () => messagingService.listConversations(params),
    staleTime: 1000 * 60, // 1 minute
    refetchOnWindowFocus: true,
  });
}

export function useConversation(id: string | null) {
  return useQuery({
    queryKey: conversationKeys.single(id ?? ''),
    queryFn: () => messagingService.getConversation(id!),
    enabled: !!id,
    staleTime: 1000 * 30, // 30 seconds
  });
}

export function useCreateConversation() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  return useMutation({
    mutationFn: (recipientId: string) =>
      messagingService.createConversation(recipientId),
    onSuccess: (newConversation: Conversation) => {
      // Invalidate conversations list so it refetches
      queryClient.invalidateQueries({ queryKey: conversationKeys.all });

      // Seed the single-conversation cache immediately
      queryClient.setQueryData(
        conversationKeys.single(newConversation.id),
        newConversation
      );

      toast({
        title: 'Conversation started',
        description: 'You can now send messages',
        variant: 'success',
      });
    },
    onError: (error: unknown) => {
      const msg =
        error instanceof Error ? error.message : 'Please try again';
      toast({
        title: 'Failed to start conversation',
        description: msg,
        variant: 'error',
      });
    },
  });
}

export function useSearchConversations(query: string, page = 1, page_size = 20) {
  return useQuery({
    queryKey: conversationKeys.list({ search: query, page, page_size }),
    queryFn: () =>
      messagingService.listConversations({ search: query, page, page_size }),
    enabled: query.length > 0,
    staleTime: 1000 * 30,
  });
}
