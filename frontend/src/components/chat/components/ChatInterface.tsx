/**
 * ChatInterface - Root component for AI Chat Interface
 * Gemini-style conversational AI sidebar with glassmorphism design
 */

'use client';

import React, { useEffect, useCallback, useState, useRef } from 'react';
import { createPortal } from 'react-dom';
import { useChatStore } from '../store/chatStore';
import { useChatWebSocket } from '../hooks/useChatWebSocket';
import { useAuthStore } from '@/store/authStore';
import { ChatHeader } from './ChatHeader';
import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { QuickActionBar } from './QuickActionBar';
import { QuotaResetNotification } from './QuotaResetNotification';
import { ErrorMessage } from './ErrorMessage';
import { UpgradePrompt } from './UpgradePrompt';
import type { ChatInterfaceProps, QuickActionType } from '../types';
import { ChatErrorType } from '../types';
import { UI_CONFIG, QUICK_ACTIONS } from '../constants';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export function ChatInterface({ isOpen, onClose, initialContext }: ChatInterfaceProps) {
  const router = useRouter();
  
  const {
    messages,
    streamingContent,
    isStreaming,
    connectionStatus,
    error,
    quota,
    clearConversation,
    setError,
  } = useChatStore();

  // Track previous quota to detect resets
  const previousQuotaRef = useRef<{ remaining: number | null; tier: string } | null>(null);
  const [showQuotaResetNotification, setShowQuotaResetNotification] = useState(false);
  const [showUpgradePrompt, setShowUpgradePrompt] = useState(false);
  
  // Swipe gesture state
  const touchStartY = useRef<number>(0);
  const touchCurrentY = useRef<number>(0);
  const [swipeOffset, setSwipeOffset] = useState<number>(0);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  
  // Virtual keyboard handling state
  const [keyboardHeight, setKeyboardHeight] = useState<number>(0);

  // Get auth token from auth store
  const { token } = useAuthStore();
  const authToken = token || (typeof window !== 'undefined' ? localStorage.getItem('token') || '' : '');

  // Initialize WebSocket connection
  const { sendMessage, retryMessage, isConnected } = useChatWebSocket({
    token: authToken,
    enabled: isOpen,
    context: initialContext,
  });

  // Detect quota reset (from 0 to positive value for free tier)
  useEffect(() => {
    if (!quota) {
      return;
    }

    const previous = previousQuotaRef.current;

    // Check if quota was reset
    // Quota reset occurs when:
    // 1. Previous quota was 0 (or null initially)
    // 2. Current quota is > 0
    // 3. User is on free tier
    if (
      quota.tier === 'free' &&
      quota.remaining !== null &&
      quota.remaining > 0 &&
      previous &&
      previous.remaining === 0 &&
      previous.tier === 'free'
    ) {
      // Quota was reset! Show notification
      setShowQuotaResetNotification(true);
    }

    // Update previous quota reference
    previousQuotaRef.current = {
      remaining: quota.remaining,
      tier: quota.tier,
    };
  }, [quota]);

  // Show upgrade prompt when quota exceeded
  useEffect(() => {
    if (error?.type === ChatErrorType.QUOTA_EXCEEDED) {
      setShowUpgradePrompt(true);
    }
  }, [error]);

  // Handle retry action
  const handleRetry = useCallback(() => {
    setError(null);
    retryMessage();
  }, [retryMessage, setError]);

  // Handle upgrade action
  const handleUpgrade = useCallback(() => {
    setShowUpgradePrompt(false);
    router.push('/subscription');
  }, [router]);

  // Handle login redirect
  const handleLogin = useCallback(() => {
    // Save current conversation state
    useChatStore.getState().saveToSession();
    // Redirect to login
    router.push('/login');
  }, [router]);

  // Handle quick action click
  const handleQuickAction = useCallback((actionId: QuickActionType) => {
    const action = QUICK_ACTIONS.find((a) => a.id === actionId);
    if (!action) return;

    let prompt = action.promptTemplate;
    
    // Replace context placeholders with actual data from initialContext
    if (initialContext?.contextData) {
      Object.entries(initialContext.contextData).forEach(([key, value]) => {
        const formattedValue = typeof value === 'object' 
          ? JSON.stringify(value) 
          : String(value);
        prompt = prompt.replace(`{${key}}`, formattedValue);
      });
    }

    // Send the prompt
    if (isConnected && prompt) {
      sendMessage(prompt);
    }
  }, [initialContext, isConnected, sendMessage]);

  // Handle message send
  const handleSend = useCallback((content: string) => {
    if (isConnected) {
      sendMessage(content);
    }
  }, [isConnected, sendMessage]);

  // Handle copy
  const handleCopy = useCallback((content: string) => {
    navigator.clipboard.writeText(content).then(() => {
      toast.success('Copied to clipboard');
    }).catch(() => {
      toast.error('Failed to copy to clipboard');
    });
  }, []);

  // Handle swipe-down gesture to close on mobile
  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    // Only track swipe if user starts from the top portion of the chat
    const touch = e.touches[0];
    touchStartY.current = touch.clientY;
    touchCurrentY.current = touch.clientY;
    setSwipeOffset(0);
  }, []);

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    const touch = e.touches[0];
    touchCurrentY.current = touch.clientY;
    
    // Calculate swipe distance (only allow downward swipes)
    const deltaY = touchCurrentY.current - touchStartY.current;
    
    if (deltaY > 0) {
      // Update visual offset for drag feedback
      setSwipeOffset(deltaY);
      
      // Prevent default scrolling when swiping down
      if (deltaY > 10) {
        e.preventDefault();
      }
    }
  }, []);

  const handleTouchEnd = useCallback(() => {
    const deltaY = touchCurrentY.current - touchStartY.current;
    
    // If swipe distance exceeds threshold (100px), close the chat
    if (deltaY > 100) {
      onClose();
    }
    
    // Reset swipe state
    setSwipeOffset(0);
    touchStartY.current = 0;
    touchCurrentY.current = 0;
  }, [onClose]);

  // Handle Ctrl/Cmd+K to open/close chat globally
  useEffect(() => {
    const handleGlobalKeyboard = (e: KeyboardEvent) => {
      // Check for Ctrl+K or Cmd+K
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        if (isOpen) {
          onClose();
        } else {
          // Don't open if not already handling the event
        }
      }
    };

    document.addEventListener('keydown', handleGlobalKeyboard);
    return () => document.removeEventListener('keydown', handleGlobalKeyboard);
  }, [isOpen, onClose]);

  // Handle escape key to close and prevent body scroll
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleEscape);
      
      // Prevent body scroll when chat is open
      // Save current body style to restore later
      const originalStyle = window.getComputedStyle(document.body).overflow;
      const originalPosition = window.getComputedStyle(document.body).position;
      
      // Prevent scrolling on the body
      document.body.style.overflow = 'hidden';
      
      // On mobile, also prevent touch-move on body to ensure scroll is fully disabled
      const preventTouchMove = (e: TouchEvent) => {
        // Allow touch events within the chat container
        if (chatContainerRef.current?.contains(e.target as Node)) {
          return;
        }
        e.preventDefault();
      };
      
      document.body.addEventListener('touchmove', preventTouchMove, { passive: false });

      return () => {
        document.removeEventListener('keydown', handleEscape);
        document.body.removeEventListener('touchmove', preventTouchMove);
        
        // Restore original body styles
        document.body.style.overflow = originalStyle;
      };
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  // Virtual keyboard and focus management
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    // Focus message input when chat opens
    const focusInput = () => {
      const input = document.querySelector('[aria-label="Message input field"] input') as HTMLInputElement;
      if (input) {
        input.focus();
      }
    };

    // Defer focus to next tick to ensure DOM is ready
    const timer = setTimeout(focusInput, 100);

    return () => clearTimeout(timer);
  }, [isOpen]);

  // Handle virtual keyboard on mobile devices
  useEffect(() => {
    if (!isOpen) {
      return;
    }

    // Check if visualViewport is supported (modern mobile browsers)
    if (typeof window === 'undefined' || !window.visualViewport) {
      return;
    }

    const handleViewportResize = () => {
      if (!window.visualViewport) {
        return;
      }

      // Calculate the difference between the window height and the visual viewport height
      // This gives us the approximate keyboard height
      const windowHeight = window.innerHeight;
      const viewportHeight = window.visualViewport.height;
      const calculatedKeyboardHeight = windowHeight - viewportHeight;

      // Only adjust if keyboard is actually open (significant height difference)
      // Use a threshold to avoid small viewport changes
      if (calculatedKeyboardHeight > 150) {
        setKeyboardHeight(calculatedKeyboardHeight);
      } else {
        setKeyboardHeight(0);
      }
    };

    // Listen to visualViewport resize events
    window.visualViewport.addEventListener('resize', handleViewportResize);
    window.visualViewport.addEventListener('scroll', handleViewportResize);

    // Initial check
    handleViewportResize();

    return () => {
      if (window.visualViewport) {
        window.visualViewport.removeEventListener('resize', handleViewportResize);
        window.visualViewport.removeEventListener('scroll', handleViewportResize);
      }
      // Reset keyboard height on cleanup
      setKeyboardHeight(0);
    };
  }, [isOpen]);

  // Don't render if not open
  if (!isOpen) {
    return null;
  }

  const interfaceContent = (
    <div
      className="fixed inset-0 z-50 flex items-center justify-end"
      role="dialog"
      aria-modal="true"
      aria-labelledby="chat-interface-title"
      aria-describedby="chat-interface-description"
    >
      {/* Backdrop - visible on all breakpoints, clickable on desktop to close */}
      <div
        className="absolute inset-0 bg-black/20 backdrop-blur-sm lg:cursor-pointer"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Chat Container with responsive breakpoints:
          - Mobile (<768px): Full-screen overlay (w-full h-full)
          - Tablet (768-1024px): Full-screen overlay (w-full h-full)
          - Desktop (≥1024px): 400px sidebar from right
      */}
      <div
        ref={chatContainerRef}
        onTouchStart={handleTouchStart}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        className={`
          relative flex flex-col
          w-full h-full
          lg:w-[400px] lg:min-w-[320px] lg:max-w-[90vw] lg:h-full
          bg-white/10 backdrop-blur-xl
          border-white/20
          lg:border-l
          shadow-2xl
          animate-slide-in-right
          transition-transform
          focus:outline-none
        `}
        style={{
          background: 'rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(12px)',
          WebkitBackdropFilter: 'blur(12px)',
          transform: `translateY(${swipeOffset}px)`,
          paddingBottom: keyboardHeight > 0 ? `${keyboardHeight}px` : '0px',
        }}
      >
        {/* Hidden title and description for accessibility */}
        <h2 id="chat-interface-title" className="sr-only">AI Assistant Chat</h2>
        <p id="chat-interface-description" className="sr-only">
          Interactive AI chat interface. Press Escape to close. Press Enter to send messages. Use Tab to navigate between elements.
        </p>

        {/* Header */}
        <ChatHeader
          onClose={onClose}
          quota={quota}
          context={initialContext}
        />

        {/* Connection Status */}
        {connectionStatus === 'connecting' && !error && (
          <div 
            className="px-4 py-2 bg-blue-500/10 text-blue-700 text-sm"
            role="status"
            aria-live="polite"
            aria-label="Connecting to AI Assistant"
          >
            Connecting to AI...
          </div>
        )}
        {connectionStatus === 'disconnected' && !error && (
          <div 
            className="px-4 py-2 bg-amber-500/10 text-amber-700 text-sm"
            role="status"
            aria-live="polite"
            aria-label="Disconnected from AI Assistant"
          >
            Disconnected. Trying to reconnect...
          </div>
        )}

        {/* Error Message */}
        {error && (
          <ErrorMessage
            error={error}
            onRetry={handleRetry}
            onUpgrade={() => setShowUpgradePrompt(true)}
            onLogin={handleLogin}
          />
        )}

        {/* Quota Reset Notification */}
        <QuotaResetNotification
          visible={showQuotaResetNotification}
          onDismiss={() => setShowQuotaResetNotification(false)}
          resetAmount={quota?.remaining ?? 20}
        />

        {/* Messages */}
        <MessageList
          messages={messages}
          streamingContent={streamingContent}
          isStreaming={isStreaming}
          onCopy={handleCopy}
          aria-label="Chat message history"
        />

        {/* Quick Actions */}
        <QuickActionBar
          context={initialContext}
          onActionClick={handleQuickAction}
          disabled={!isConnected || isStreaming}
          aria-label="Quick action suggestions"
        />

        {/* Input */}
        <MessageInput
          onSend={handleSend}
          disabled={!isConnected || isStreaming}
          aria-label="Message input field"
        />
      </div>

      {/* Upgrade Prompt Modal */}
      {showUpgradePrompt && (
        <UpgradePrompt
          isOpen={showUpgradePrompt}
          onClose={() => setShowUpgradePrompt(false)}
          onUpgrade={handleUpgrade}
        />
      )}
      
      {/* Skip link for keyboard navigation */}
      <a href="#main-content" className="sr-only focus:not-sr-only">
        Skip to main content
      </a>
    </div>
  );

  // Render via portal to body
  if (typeof window === 'undefined') {
    return null;
  }

  return createPortal(interfaceContent, document.body);
}
