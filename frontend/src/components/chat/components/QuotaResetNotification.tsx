/**
 * QuotaResetNotification - Success banner for quota reset
 * Displays for 5 seconds with auto-dismiss and smooth fade-out animation
 * 
 * **Validates: Requirement 10.7**
 */

'use client';

import React, { useEffect, useState } from 'react';
import { CheckCircle2, X } from 'lucide-react';

export interface QuotaResetNotificationProps {
  visible: boolean;
  onDismiss: () => void;
  resetAmount?: number;
}

/**
 * QuotaResetNotification Component
 * 
 * Success banner that appears when user's AI quota resets (daily reset).
 * - Appears when quota changes from 0 to reset value
 * - Styled with Tailwind success colors (green)
 * - Auto-dismisses after 5 seconds
 * - Smooth fade-out animation
 */
export function QuotaResetNotification({
  visible,
  onDismiss,
  resetAmount = 20,
}: QuotaResetNotificationProps) {
  const [isExiting, setIsExiting] = useState(false);

  useEffect(() => {
    if (!visible) {
      setIsExiting(false);
      return;
    }

    // Auto-dismiss after 5 seconds
    const dismissTimer = setTimeout(() => {
      setIsExiting(true);
      
      // Wait for fade-out animation to complete before calling onDismiss
      setTimeout(() => {
        onDismiss();
      }, 300); // Match animation duration
    }, 5000);

    return () => {
      clearTimeout(dismissTimer);
    };
  }, [visible, onDismiss]);

  if (!visible) {
    return null;
  }

  const handleManualDismiss = () => {
    setIsExiting(true);
    setTimeout(() => {
      onDismiss();
    }, 300);
  };

  return (
    <div
      className={`
        px-4 py-3 
        bg-green-50 border border-green-200
        text-green-800
        flex items-center justify-between gap-3
        transition-all duration-300 ease-in-out
        ${isExiting ? 'opacity-0 translate-y-[-10px]' : 'opacity-100 translate-y-0'}
      `}
      role="status"
      aria-live="polite"
    >
      {/* Icon and Message */}
      <div className="flex items-center gap-3 flex-1">
        <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0" />
        <div className="flex-1">
          <p className="text-sm font-medium">
            Your AI quota has been reset!
          </p>
          <p className="text-xs text-green-700 mt-0.5">
            You now have {resetAmount} AI requests available.
          </p>
        </div>
      </div>

      {/* Manual Dismiss Button */}
      <button
        onClick={handleManualDismiss}
        className="
          p-1 
          hover:bg-green-100 
          rounded 
          transition-colors
          focus:outline-none 
          focus:ring-2 
          focus:ring-green-500 
          focus:ring-offset-1
        "
        aria-label="Dismiss notification"
      >
        <X className="w-4 h-4 text-green-600" />
      </button>
    </div>
  );
}
