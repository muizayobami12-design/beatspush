/**
 * QuotaDisplay - Component for displaying AI quota status
 * Shows remaining requests for free users, unlimited badge for premium
 */

'use client';

import React from 'react';
import type { QuotaDisplayProps } from '../types';

export function QuotaDisplay({ quota, onUpgradeClick }: QuotaDisplayProps) {
  if (!quota) {
    return null;
  }

  // Premium user
  if (quota.tier === 'premium') {
    return (
      <div
        className="flex items-center gap-1.5 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg shadow-sm"
        title="Premium plan - Unlimited AI requests"
      >
        <span className="text-sm font-semibold text-white">Unlimited</span>
        <span className="text-base">⚡</span>
      </div>
    );
  }

  // Free user
  const remaining = quota.remaining ?? 0;
  const total = 20;
  const percentage = (remaining / total) * 100;
  
  // Determine status
  const isEmpty = remaining === 0;
  const isLow = remaining > 0 && remaining <= 5;
  const isNormal = remaining > 5;

  // Colors based on status
  const bgColor = isEmpty
    ? 'bg-red-500/10'
    : isLow
    ? 'bg-amber-500/10'
    : 'bg-gray-100';

  const textColor = isEmpty
    ? 'text-red-700'
    : isLow
    ? 'text-amber-700'
    : 'text-gray-700';

  const borderColor = isEmpty
    ? 'border-red-300'
    : isLow
    ? 'border-amber-300'
    : 'border-gray-300';

  // Format reset time
  const resetTime = quota.resetAt
    ? new Date(quota.resetAt).toLocaleString('en-US', {
        hour: 'numeric',
        minute: 'numeric',
        hour12: true,
      })
    : null;

  return (
    <div className="relative group">
      {/* Quota Display */}
      <div
        className={`
          flex items-center gap-2 px-3 py-1.5 rounded-lg border
          ${bgColor} ${borderColor}
          cursor-pointer transition-all
          hover:shadow-md
        `}
        onClick={isEmpty ? onUpgradeClick : undefined}
      >
        {/* Progress bar (small visual indicator) */}
        <div className="w-8 h-1.5 bg-gray-200 rounded-full overflow-hidden">
          <div
            className={`
              h-full transition-all duration-300 rounded-full
              ${isEmpty ? 'bg-red-500' : isLow ? 'bg-amber-500' : 'bg-purple-600'}
            `}
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Count */}
        <span className={`text-sm font-medium ${textColor}`}>
          {remaining}/{total}
        </span>

        {/* Warning icon for low/empty */}
        {(isEmpty || isLow) && (
          <span className="text-base">
            {isEmpty ? '🚫' : '⚠️'}
          </span>
        )}
      </div>

      {/* Tooltip */}
      <div
        className="
          absolute bottom-full left-1/2 -translate-x-1/2 mb-2
          px-3 py-2 bg-gray-900 text-white text-xs rounded-lg
          opacity-0 group-hover:opacity-100
          pointer-events-none
          transition-opacity duration-200
          whitespace-nowrap
          z-10
        "
      >
        <div className="space-y-1">
          <div className="font-medium">
            {isEmpty ? 'Daily limit reached' : `${remaining} requests remaining`}
          </div>
          {resetTime && (
            <div className="text-gray-300">
              Resets at {resetTime}
            </div>
          )}
          {isEmpty && (
            <div className="text-purple-300 mt-1">
              Click to upgrade
            </div>
          )}
        </div>
        {/* Arrow */}
        <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1">
          <div className="w-2 h-2 bg-gray-900 rotate-45" />
        </div>
      </div>

      {/* Upgrade prompt for empty quota */}
      {isEmpty && (
        <button
          onClick={onUpgradeClick}
          className="
            absolute -bottom-8 left-0 right-0
            px-2 py-1 text-xs
            bg-gradient-to-r from-purple-600 to-blue-600
            text-white rounded-md
            opacity-0 group-hover:opacity-100
            transition-opacity duration-200
            hover:shadow-lg
          "
        >
          Upgrade for unlimited
        </button>
      )}
    </div>
  );
}
