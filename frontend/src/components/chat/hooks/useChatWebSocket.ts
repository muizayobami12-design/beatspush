/**
 * useChatWebSocket - Custom hook for WebSocket integration with Chat Store
 * Connects WebSocket client to Zustand chat store with automatic retry logic
 */

import { useEffect, useRef, useCallback } from 'react';
import { ChatWebSocketClient } from '../utils/ChatWebSocketClient';
import { useChatStore } from '../store/chatStore';
import type { ChatMessagePayload, PageContext } from '../types';
import { ChatErrorType } from '../types';

interface UseChatWebSocketOptions {
  token: string;
  enabled?: boolean;
  context?: PageContext;
}

const MAX_AUTO_RETRIES = 2;

export function useChatWebSocket({ token, enabled = true, context }: UseChatWebSocketOptions) {
  const clientRef = useRef<ChatWebSocketClient | null>(null);
  const contextRef = useRef<PageContext | undefined>(context);
  const retryTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  
  const {
    isOpen,
    messages,
    retryCount,
    lastFailedMessage,
    appendStreamingChunk,
    finalizeStreamingMessage,
    setError,
    setConnectionStatus,
    incrementRetryCount,
    resetRetryCount,
  } = useChatStore();

  // Update context ref when it changes
  useEffect(() => {
    contextRef.current = context;
  }, [context]);

  // Auto-retry logic for failed requests
  const handleAutoRetry = useCallback((errorType: ChatErrorType) => {
    // Only auto-retry certain error types
    const retryableErrors: ChatErrorType[] = [
      ChatErrorType.CONNECTION_FAILED,
      ChatErrorType.STREAMING_INTERRUPTED,
      ChatErrorType.MESSAGE_SEND_FAILED,
      ChatErrorType.TIMEOUT,
    ];

    if (!retryableErrors.includes(errorType)) {
      return;
    }

    if (retryCount < MAX_AUTO_RETRIES && lastFailedMessage) {
      // Increment retry count
      incrementRetryCount();

      // Wait 2 seconds before retrying
      retryTimeoutRef.current = setTimeout(() => {
        console.log(`[useChatWebSocket] Auto-retry attempt ${retryCount + 1}/${MAX_AUTO_RETRIES}`);
        
        // Clear error before retry
        setError(null);
        
        // Resend the last failed message
        if (clientRef.current && clientRef.current.isConnected()) {
          const conversationId = messages[0]?.conversationId;
          const payload: ChatMessagePayload = {
            type: 'chat_message',
            content: lastFailedMessage,
            context: contextRef.current || {
              pageType: 'general',
              pageUrl: window.location.pathname,
              contextData: {},
            },
            conversationId,
          };
          
          try {
            clientRef.current.send(payload);
          } catch (error) {
            console.error('[useChatWebSocket] Retry failed:', error);
            // Set error after retry failure
            setError({
              type: ChatErrorType.MESSAGE_SEND_FAILED,
              message: 'Failed to send message after retry',
              retryable: true,
              action: 'retry',
            });
          }
        }
      }, 2000);
    } else if (retryCount >= MAX_AUTO_RETRIES) {
      // Max retries reached, show error with manual retry button
      console.log('[useChatWebSocket] Max auto-retries reached');
      setError({
        type: errorType,
        message: 'Failed after multiple attempts. Please try again.',
        retryable: true,
        action: 'retry',
      });
    }
  }, [retryCount, lastFailedMessage, messages, incrementRetryCount, setError]);

  // Cleanup retry timeout
  useEffect(() => {
    return () => {
      if (retryTimeoutRef.current) {
        clearTimeout(retryTimeoutRef.current);
      }
    };
  }, []);

  // Initialize WebSocket client
  useEffect(() => {
    if (!enabled || !isOpen) {
      return;
    }

    // Create WebSocket client
    const client = new ChatWebSocketClient(
      {
        url: process.env.NEXT_PUBLIC_WS_URL || '',
        token,
      },
      {
        onOpen: () => {
          console.log('[useChatWebSocket] Connected');
          setConnectionStatus('connected');
          setError(null);
          resetRetryCount(); // Reset retry count on successful connection
        },
        onMessage: (chunk) => {
          if (chunk.type === 'chunk' && chunk.content) {
            // Append streaming content
            appendStreamingChunk(chunk.content);
            resetRetryCount(); // Reset on successful chunk (message is working)
          } else if (chunk.type === 'done') {
            // Finalize the streaming message
            finalizeStreamingMessage();
            resetRetryCount(); // Reset on successful completion
            
            // Update quota if provided
            if (chunk.metadata?.quotaRemaining !== undefined) {
              useChatStore.getState().updateQuota({
                tier: 'free', // Will be updated by actual quota check
                remaining: chunk.metadata.quotaRemaining,
                resetAt: null,
                allowed: chunk.metadata.quotaRemaining > 0,
              });
            }
          } else if (chunk.type === 'error') {
            // Display partial response if available before showing error
            const currentContent = useChatStore.getState().streamingContent;
            if (currentContent) {
              // Save partial response
              finalizeStreamingMessage();
            }
            
            // Handle error response from server
            const errorMessage = chunk.error || 'Streaming interrupted';
            
            // Determine error type based on error message
            let errorType = ChatErrorType.STREAMING_INTERRUPTED;
            if (errorMessage.includes('quota') || errorMessage.includes('limit exceeded')) {
              errorType = ChatErrorType.QUOTA_EXCEEDED;
            } else if (errorMessage.includes('rate limit')) {
              errorType = ChatErrorType.RATE_LIMIT;
            } else if (errorMessage.includes('authentication') || errorMessage.includes('unauthorized')) {
              errorType = ChatErrorType.AUTHENTICATION_FAILED;
            }
            
            setError({
              type: errorType,
              message: errorMessage,
              retryable: errorType !== ChatErrorType.QUOTA_EXCEEDED && errorType !== ChatErrorType.AUTHENTICATION_FAILED,
              action: errorType === ChatErrorType.QUOTA_EXCEEDED ? 'upgrade' : 
                      errorType === ChatErrorType.AUTHENTICATION_FAILED ? 'login' : 
                      errorType === ChatErrorType.RATE_LIMIT ? 'wait' : 'retry',
            });
            
            // Only trigger auto-retry for certain errors
            if (errorType === ChatErrorType.STREAMING_INTERRUPTED) {
              handleAutoRetry(errorType);
            }
          }
        },
        onError: (error) => {
          console.error('[useChatWebSocket] Error:', error);
          setConnectionStatus('disconnected');
          
          const errorType = ChatErrorType.CONNECTION_FAILED;
          setError({
            type: errorType,
            message: error.message,
            retryable: true,
            action: 'retry',
          });
          
          // Trigger auto-retry
          handleAutoRetry(errorType);
        },
        onClose: () => {
          console.log('[useChatWebSocket] Disconnected');
          setConnectionStatus('disconnected');
        },
      }
    );

    clientRef.current = client;

    // Connect
    setConnectionStatus('connecting');
    client.connect().catch((error) => {
      console.error('[useChatWebSocket] Failed to connect:', error);
      setConnectionStatus('disconnected');
      
      const errorType = ChatErrorType.CONNECTION_FAILED;
      setError({
        type: errorType,
        message: 'Failed to establish connection',
        retryable: true,
        action: 'retry',
      });
      
      // Trigger auto-retry
      handleAutoRetry(errorType);
    });

    // Cleanup on unmount
    return () => {
      client.disconnect();
      clientRef.current = null;
    };
  }, [enabled, isOpen, token, appendStreamingChunk, finalizeStreamingMessage, setError, setConnectionStatus]);

  // Send message function with timeout and error handling
  const sendMessage = useCallback((content: string) => {
    if (!clientRef.current || !clientRef.current.isConnected()) {
      const errorType = ChatErrorType.MESSAGE_SEND_FAILED;
      setError({
        type: errorType,
        message: 'Not connected to chat server',
        retryable: true,
        action: 'retry',
      });
      
      // Trigger auto-retry
      handleAutoRetry(errorType);
      return;
    }

    const conversationId = messages[0]?.conversationId;

    const payload: ChatMessagePayload = {
      type: 'chat_message',
      content,
      context: contextRef.current || {
        pageType: 'general',
        pageUrl: window.location.pathname,
        contextData: {},
      },
      conversationId,
    };

    try {
      clientRef.current.send(payload);
      
      // Update store with user message
      useChatStore.getState().sendMessage(content);
      
      // Set timeout for response (30 seconds)
      const timeoutId = setTimeout(() => {
        // Check if we're still streaming
        const state = useChatStore.getState();
        if (state.isStreaming) {
          // Display partial response if available
          if (state.streamingContent) {
            state.finalizeStreamingMessage();
          }
          
          // No response or partial response received in 30 seconds
          const errorType = ChatErrorType.TIMEOUT;
          setError({
            type: errorType,
            message: 'AI is taking longer than usual. Please try again.',
            retryable: true,
            action: 'retry',
          });
          
          // Trigger auto-retry
          handleAutoRetry(errorType);
        }
      }, 30000); // 30 second timeout
      
      // Store timeout ID for cleanup (you might want to add this to state if needed)
      // For now, we'll let it clean up naturally
      
    } catch (error) {
      console.error('[useChatWebSocket] Failed to send message:', error);
      
      const errorType = ChatErrorType.MESSAGE_SEND_FAILED;
      setError({
        type: errorType,
        message: 'Failed to send message',
        retryable: true,
        action: 'retry',
      });
      
      // Trigger auto-retry
      handleAutoRetry(errorType);
    }
  }, [messages, setError, handleAutoRetry]);

  // Manual retry function
  const retryMessage = useCallback(() => {
    if (lastFailedMessage) {
      resetRetryCount();
      setError(null);
      sendMessage(lastFailedMessage);
    }
  }, [lastFailedMessage, resetRetryCount, setError, sendMessage]);

  return {
    sendMessage,
    retryMessage,
    isConnected: clientRef.current?.isConnected() ?? false,
  };
}
