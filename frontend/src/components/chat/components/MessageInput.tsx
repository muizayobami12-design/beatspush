/**
 * MessageInput - Text input component for chat messages
 * Auto-resizing textarea with character limit and keyboard shortcuts
 */

'use client';

import React, { useState, useRef, useEffect } from 'react';
import type { MessageInputProps } from '../types';
import { CHAT_CONFIG } from '../constants';

export function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Ask me anything...',
  maxLength = CHAT_CONFIG.MAX_MESSAGE_LENGTH,
}: MessageInputProps) {
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      // Max 5 lines (roughly 120px)
      textareaRef.current.style.height = `${Math.min(scrollHeight, 120)}px`;
    }
  }, [value]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = value.trim();
    
    if (trimmed && !disabled) {
      onSend(trimmed);
      setValue('');
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const characterCount = value.length;
  const isOverLimit = characterCount > maxLength;
  const showCount = characterCount > maxLength * 0.8; // Show at 80%

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t border-white/20">
      <div className="flex gap-2">
        {/* Textarea */}
        <div className="flex-1 relative">
          <textarea
            ref={textareaRef}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            maxLength={maxLength}
            className={`
              w-full px-3 py-2 
              bg-white/50 border border-white/20 rounded-lg
              focus:outline-none focus:ring-2 focus:ring-purple-600
              resize-none
              disabled:opacity-50 disabled:cursor-not-allowed
              ${isOverLimit ? 'border-red-500 focus:ring-red-500' : ''}
            `}
            rows={1}
            aria-label="Message input"
          />
          
          {/* Character count */}
          {showCount && (
            <div
              className={`
                absolute bottom-1 right-2 text-xs
                ${isOverLimit ? 'text-red-600 font-medium' : 'text-gray-500'}
              `}
            >
              {characterCount}/{maxLength}
            </div>
          )}
        </div>

        {/* Send button - Minimum 44x44px touch target */}
        <button
          type="submit"
          disabled={disabled || !value.trim() || isOverLimit}
          className="
            min-w-[44px] min-h-[44px]
            px-4 py-2 
            bg-gradient-to-r from-purple-600 to-blue-600 
            text-white rounded-lg 
            hover:opacity-90 
            disabled:opacity-50 disabled:cursor-not-allowed
            transition-opacity
            flex items-center justify-center
          "
          aria-label="Send message"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"
            />
          </svg>
        </button>
      </div>

      {/* Keyboard shortcuts hint */}
      <div className="mt-2 text-xs text-gray-500 flex items-center justify-between">
        <span>
          <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs">Enter</kbd>
          {' '}to send, {' '}
          <kbd className="px-1.5 py-0.5 bg-gray-100 border border-gray-300 rounded text-xs">Shift+Enter</kbd>
          {' '}for new line
        </span>
        {disabled && (
          <span className="text-amber-600">⚠️ Connecting...</span>
        )}
      </div>
    </form>
  );
}
