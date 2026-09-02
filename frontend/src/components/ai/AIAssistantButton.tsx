/**
 * AI Assistant Button
 * Simple button to trigger AI actions
 */

'use client';

import React from 'react';
import { Sparkles, Loader2 } from 'lucide-react';

export interface AIAssistantButtonProps {
  onClick: () => void;
  loading?: boolean;
  disabled?: boolean;
  label?: string;
  variant?: 'primary' | 'secondary' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export function AIAssistantButton({
  onClick,
  loading = false,
  disabled = false,
  label = 'Generate with AI',
  variant = 'primary',
  size = 'md',
  className = '',
}: AIAssistantButtonProps) {
  const baseClasses = 'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200';
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white shadow-lg hover:shadow-xl',
    secondary: 'bg-purple-100 hover:bg-purple-200 text-purple-700 border border-purple-300',
    ghost: 'hover:bg-purple-50 text-purple-600',
  };
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  const disabledClasses = 'opacity-50 cursor-not-allowed';

  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        ${baseClasses}
        ${variantClasses[variant]}
        ${sizeClasses[size]}
        ${(disabled || loading) ? disabledClasses : ''}
        ${className}
      `}
    >
      {loading ? (
        <Loader2 className="w-4 h-4 animate-spin" />
      ) : (
        <Sparkles className="w-4 h-4" />
      )}
      <span>{loading ? 'Generating...' : label}</span>
    </button>
  );
}

export default AIAssistantButton;
