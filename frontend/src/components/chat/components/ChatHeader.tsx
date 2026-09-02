/**
 * ChatHeader - Header component for chat interface
 * Displays title, quota, context badge, and action buttons
 */

'use client';

import React from 'react';
import type { ChatHeaderProps } from '../types';

export function ChatHeader({
  onClose,
  onMinimize,
  quota,
  context,
}: ChatHeaderProps) {
  // Determine quota display
  const getQuotaDisplay = () => {
    if (!quota) return null;
    
    if (quota.tier === 'premium') {
      return (
        <div className="flex items-center gap-1 px-2 py-1 bg-purple-600/10 rounded-md">
          <span className="text-xs font-medium text-purple-700">Unlimited</span>
          <span className="text-sm">⚡</span>
        </div>
      );
    }

    // Free tier
    const remaining = quota.remaining ?? 0;
    const isLow = remaining <= 5;
    const isEmpty = remaining === 0;

    return (
      <div
        className={`
          flex items-center gap-1 px-2 py-1 rounded-md
          ${isEmpty ? 'bg-red-500/10' : isLow ? 'bg-amber-500/10' : 'bg-gray-100'}
        `}
        title={quota.resetAt ? `Resets at ${new Date(quota.resetAt).toLocaleString()}` : undefined}
      >
        <span
          className={`
            text-xs font-medium
            ${isEmpty ? 'text-red-700' : isLow ? 'text-amber-700' : 'text-gray-700'}
          `}
        >
          {remaining}/20
        </span>
      </div>
    );
  };

  return (
    <div className="flex items-center justify-between p-4 border-b border-white/20 bg-white/5">
      {/* Left side - Title and context */}
      <div className="flex items-center gap-3">
        {/* Back button - Mobile only (<768px) */}
        <button
          onClick={onClose}
          className="lg:hidden min-w-[44px] min-h-[44px] flex items-center justify-center p-2 -ml-2 rounded-lg hover:bg-white/10 transition-colors"
          aria-label="Go back"
        >
          <svg
            className="w-5 h-5 text-gray-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 19l-7-7 7-7"
            />
          </svg>
        </button>
        
        <div>
          <h2 className="text-lg font-semibold text-gray-900">
            AI Assistant
          </h2>
          {context && (
            <p className="text-xs text-gray-600 mt-0.5">
              {context.pageType === 'beat_upload' && '🎵 Beat Upload'}
              {context.pageType === 'beat_edit' && '✏️ Beat Edit'}
              {context.pageType === 'campaign_dashboard' && '📊 Campaign'}
              {context.pageType === 'analytics' && '📈 Analytics'}
              {context.pageType === 'profile_edit' && '👤 Profile'}
              {context.pageType === 'social_feed' && '📱 Social'}
              {context.pageType === 'messaging' && '💬 Messages'}
              {context.pageType === 'general' && '💡 General'}
            </p>
          )}
        </div>
      </div>

      {/* Right side - Quota and actions */}
      <div className="flex items-center gap-2">
        {/* Quota Display */}
        {getQuotaDisplay()}

        {/* Clear conversation button - Minimum 44x44px touch target */}
        <button
          onClick={() => {
            if (confirm('Clear conversation history?')) {
              // This will be connected to store action
              console.log('Clear conversation');
            }
          }}
          className="min-w-[44px] min-h-[44px] flex items-center justify-center p-2 rounded-lg hover:bg-white/10 transition-colors"
          aria-label="Clear conversation"
          title="Clear conversation"
        >
          <svg
            className="w-5 h-5 text-gray-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>

        {/* Minimize button (optional) - Minimum 44x44px touch target */}
        {onMinimize && (
          <button
            onClick={onMinimize}
            className="min-w-[44px] min-h-[44px] flex items-center justify-center p-2 rounded-lg hover:bg-white/10 transition-colors"
            aria-label="Minimize chat"
          >
            <svg
              className="w-5 h-5 text-gray-700"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M20 12H4"
              />
            </svg>
          </button>
        )}

        {/* Close button - Desktop only (≥1024px), Minimum 44x44px touch target */}
        <button
          onClick={onClose}
          className="hidden lg:flex min-w-[44px] min-h-[44px] items-center justify-center p-2 rounded-lg hover:bg-white/10 transition-colors"
          aria-label="Close chat"
        >
          <svg
            className="w-5 h-5 text-gray-700"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
