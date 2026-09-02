/**
 * Quota Display Component
 * Shows AI request quota for free tier users
 */

'use client';

import React from 'react';
import { Zap, Crown, AlertTriangle } from 'lucide-react';
import { QuotaStatus } from '@/services/aiService';

export interface QuotaDisplayProps {
  quota: QuotaStatus | null;
  showUpgradeButton?: boolean;
  onUpgrade?: () => void;
  className?: string;
}

export function QuotaDisplay({
  quota,
  showUpgradeButton = true,
  onUpgrade,
  className = '',
}: QuotaDisplayProps) {
  if (!quota) {
    return null;
  }

  // Premium users
  if (quota.tier === 'premium') {
    return (
      <div className={`flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 rounded-lg ${className}`}>
        <Crown className="w-5 h-5 text-yellow-600" />
        <span className="text-sm font-medium text-yellow-900">
          Premium - Unlimited AI
        </span>
      </div>
    );
  }

  // Free tier users
  const remaining = quota.remaining || 0;
  const isLow = remaining <= 5;
  const isExceeded = remaining === 0;

  return (
    <div className={`space-y-2 ${className}`}>
      {/* Quota bar */}
      <div className="flex items-center justify-between gap-3 px-4 py-2 bg-white border border-gray-200 rounded-lg">
        <div className="flex items-center gap-2">
          <Zap className={`w-4 h-4 ${isLow ? 'text-orange-500' : 'text-purple-500'}`} />
          <span className="text-sm font-medium text-gray-700">
            AI Requests
          </span>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={`text-lg font-bold ${isLow ? 'text-orange-600' : 'text-purple-600'}`}>
            {remaining}
          </span>
          <span className="text-sm text-gray-500">/ 20</span>
        </div>
      </div>

      {/* Progress bar */}
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={`h-full transition-all duration-300 ${
            isExceeded ? 'bg-red-500' :
            isLow ? 'bg-orange-500' :
            'bg-gradient-to-r from-purple-500 to-blue-500'
          }`}
          style={{ width: `${(remaining / 20) * 100}%` }}
        />
      </div>

      {/* Warning message */}
      {isLow && !isExceeded && (
        <div className="flex items-start gap-2 p-3 bg-orange-50 border border-orange-200 rounded-lg">
          <AlertTriangle className="w-4 h-4 text-orange-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1">
            <p className="text-sm font-medium text-orange-900">
              {remaining} request{remaining !== 1 ? 's' : ''} remaining today
            </p>
            <p className="text-xs text-orange-700 mt-1">
              Resets at midnight UTC
            </p>
          </div>
        </div>
      )}

      {/* Quota exceeded */}
      {isExceeded && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start gap-2 mb-3">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h4 className="text-sm font-semibold text-red-900">
                Daily limit reached
              </h4>
              <p className="text-xs text-red-700 mt-1">
                Your free tier AI requests will reset at midnight UTC
              </p>
            </div>
          </div>

          {showUpgradeButton && (
            <button
              onClick={onUpgrade}
              className="w-full px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white text-sm font-medium rounded-lg transition-all duration-200 shadow-md hover:shadow-lg flex items-center justify-center gap-2"
            >
              <Crown className="w-4 h-4" />
              Upgrade to Premium
            </button>
          )}
        </div>
      )}

      {/* Upgrade prompt for low quota */}
      {isLow && !isExceeded && showUpgradeButton && (
        <button
          onClick={onUpgrade}
          className="w-full px-4 py-2 bg-white hover:bg-gray-50 text-purple-600 text-sm font-medium border border-purple-200 rounded-lg transition-all duration-200 flex items-center justify-center gap-2"
        >
          <Crown className="w-4 h-4" />
          Upgrade for Unlimited AI
        </button>
      )}
    </div>
  );
}

export default QuotaDisplay;
