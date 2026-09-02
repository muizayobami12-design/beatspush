/**
 * TypingIndicator - Animated dots showing AI is typing
 */

import React from 'react';
import type { TypingIndicatorProps } from '../types';

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ visible }) => {
  if (!visible) return null;

  return (
    <div className="flex items-center gap-1 px-4 py-2">
      <div className="flex items-center gap-1 px-3 py-2 rounded-xl bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20">
        <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" style={{ animationDelay: '0s' }} />
        <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" style={{ animationDelay: '0.2s' }} />
        <div className="w-2 h-2 rounded-full bg-purple-500 animate-pulse" style={{ animationDelay: '0.4s' }} />
      </div>
    </div>
  );
};

export default TypingIndicator;
