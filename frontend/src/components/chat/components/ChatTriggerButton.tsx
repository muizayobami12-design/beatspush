/**
 * ChatTriggerButton - Floating action button to open chat
 * Can be placed globally or on specific pages
 */

'use client';

import React from 'react';
import { useChatContext } from './ChatProvider';
import { useChatStore } from '../store/chatStore';

interface ChatTriggerButtonProps {
  position?: 'bottom-right' | 'bottom-left' | 'top-right' | 'top-left';
  showBadge?: boolean;
}

export function ChatTriggerButton({
  position = 'bottom-right',
  showBadge = true,
}: ChatTriggerButtonProps) {
  const { openChat, isOpen } = useChatContext();
  const { connectionStatus, quota } = useChatStore();

  // Don't show if chat is already open
  if (isOpen) {
    return null;
  }

  // Position classes
  const positionClasses = {
    'bottom-right': 'bottom-6 right-6',
    'bottom-left': 'bottom-6 left-6',
    'top-right': 'top-6 right-6',
    'top-left': 'top-6 left-6',
  };

  // Show badge for quota warnings or new features
  const shouldShowBadge = showBadge && quota && quota.tier === 'free' && quota.remaining <= 5;

  return (
    <button
      onClick={openChat}
      className={`
        fixed ${positionClasses[position]}
        p-4 
        bg-gradient-to-r from-purple-600 to-blue-600
        text-white rounded-full
        shadow-2xl
        hover:scale-110
        active:scale-95
        transition-transform duration-200
        z-40
        group
      `}
      aria-label="Open AI Assistant"
      title="Open AI Assistant"
    >
      {/* Icon */}
      <svg
        className="w-6 h-6"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
        />
      </svg>

      {/* Badge */}
      {shouldShowBadge && (
        <span className="absolute -top-1 -right-1 flex items-center justify-center w-5 h-5 bg-red-500 text-white text-xs font-bold rounded-full animate-pulse">
          !
        </span>
      )}

      {/* Tooltip */}
      <span
        className="
          absolute right-full mr-3 top-1/2 -translate-y-1/2
          px-3 py-2 bg-gray-900 text-white text-sm rounded-lg
          opacity-0 group-hover:opacity-100
          pointer-events-none
          transition-opacity duration-200
          whitespace-nowrap
        "
      >
        <div className="flex flex-col gap-1">
          <span>AI Assistant {shouldShowBadge && '- Low quota'}</span>
          <span className="text-xs text-gray-400">Press ⌘K or Ctrl+K</span>
        </div>
        <span className="absolute left-full top-1/2 -translate-y-1/2 -ml-1">
          <span className="block w-2 h-2 bg-gray-900 rotate-45" />
        </span>
      </span>

      {/* Pulse ring animation */}
      <span className="absolute inset-0 rounded-full bg-purple-600 animate-ping opacity-20" />
    </button>
  );
}
