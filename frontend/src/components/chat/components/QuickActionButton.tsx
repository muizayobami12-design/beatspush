/**
 * QuickActionButton - Pre-configured button for common AI tasks
 * Auto-populates prompts with context
 */

'use client';

import React, { useState } from 'react';
import type { QuickActionButtonProps } from '../types';

export function QuickActionButton({
  label,
  icon,
  action,
  context,
  disabled = false,
  onClick,
}: QuickActionButtonProps) {
  const [isLoading, setIsLoading] = useState(false);

  const handleClick = async () => {
    if (disabled || isLoading) return;

    setIsLoading(true);
    try {
      onClick?.();
    } finally {
      // Reset loading after a short delay
      setTimeout(() => setIsLoading(false), 500);
    }
  };

  return (
    <button
      onClick={handleClick}
      disabled={disabled || isLoading}
      className={`
        relative flex items-center gap-2 
        min-w-[44px] min-h-[44px]
        px-4 py-2
        bg-purple-600/10 hover:bg-purple-600/20
        text-purple-700 font-medium
        rounded-lg border border-purple-600/20
        transition-all duration-150
        hover:scale-105 hover:shadow-md
        disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100
        whitespace-nowrap
        group
      `}
      aria-label={label}
    >
      {/* Icon */}
      <span className="text-lg group-hover:scale-110 transition-transform">
        {getIcon(icon)}
      </span>

      {/* Label */}
      <span className="text-sm">{label}</span>

      {/* Loading spinner */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-purple-600/10 rounded-lg">
          <svg
            className="animate-spin h-4 w-4 text-purple-700"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        </div>
      )}
    </button>
  );
}

// Icon mapping
function getIcon(iconName: string): string {
  const icons: Record<string, string> = {
    Sparkles: '✨',
    FileText: '📝',
    Tag: '🏷️',
    DollarSign: '💰',
    TrendingUp: '📈',
    Zap: '⚡',
    MessageSquare: '💬',
    BarChart: '📊',
    GitCompare: '🔄',
    Lightbulb: '💡',
    User: '👤',
    Quote: '💭',
    Edit: '✏️',
    Hash: '#️⃣',
    Reply: '↩️',
    Mail: '✉️',
  };

  return icons[iconName] || '🔹';
}
