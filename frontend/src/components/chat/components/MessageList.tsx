/**
 * MessageList - Scrollable container for chat messages
 * Auto-scrolls to latest message, disables when user scrolls up
 * Virtual scrolling: renders only the visible window + buffer for performance
 */

'use client';

import React, { useRef, useEffect, useState, useMemo } from 'react';
import { MessageBubble } from './MessageBubble';
import { TypingIndicator } from './TypingIndicator';
import type { Message } from '../types';

/** Number of messages to render above the visible window (buffer) */
const VIRTUAL_BUFFER = 10;
/** Number of recent messages always rendered (the visible window) */
const VIRTUAL_WINDOW = 30;

interface MessageListProps {
  messages: Message[];
  streamingContent?: string;
  isStreaming?: boolean;
  onCopy?: (content: string) => void;
}

export function MessageList({
  messages,
  streamingContent,
  isStreaming = false,
  onCopy,
}: MessageListProps) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);
  const lastMessageRef = useRef<HTMLDivElement>(null);

  // Virtual scrolling: only render the last VIRTUAL_WINDOW + VIRTUAL_BUFFER messages
  // This keeps the DOM lightweight for long sessions
  const visibleMessages = useMemo(() => {
    if (messages.length <= VIRTUAL_WINDOW + VIRTUAL_BUFFER) {
      return messages; // Small enough to render all
    }
    // Only render the tail of the message list
    return messages.slice(-(VIRTUAL_WINDOW + VIRTUAL_BUFFER));
  }, [messages]);

  // Track whether messages were trimmed (for top indicator)
  const hasHiddenMessages = messages.length > VIRTUAL_WINDOW + VIRTUAL_BUFFER;

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (autoScroll && scrollContainerRef.current) {
      scrollContainerRef.current.scrollTo({
        top: scrollContainerRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages, streamingContent, autoScroll]);

  // Detect user scrolling up
  const handleScroll = () => {
    if (!scrollContainerRef.current) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollContainerRef.current;
    const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;

    setAutoScroll(isAtBottom);
  };

  // Empty state
  if (messages.length === 0 && !isStreaming) {
    return (
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="text-center text-gray-500 space-y-4">
          <div className="text-6xl">👋</div>
          <div>
            <p className="text-lg font-medium text-gray-700">Hi! How can I help you today?</p>
            <p className="text-sm mt-2">Ask me anything about your beats, campaigns, or analytics.</p>
          </div>
          <div className="flex flex-wrap gap-2 justify-center mt-4">
            <span className="px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-xs">
              Generate beat titles
            </span>
            <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs">
              Write descriptions
            </span>
            <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs">
              Analyze campaigns
            </span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div
      ref={scrollContainerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth"
      role="log"
      aria-live="polite"
      aria-atomic="false"
    >
      {/* Indicator when older messages are not rendered */}
      {hasHiddenMessages && (
        <div className="text-center text-xs text-gray-400 py-2">
          Showing last {VIRTUAL_WINDOW + VIRTUAL_BUFFER} messages
        </div>
      )}

      {visibleMessages.map((message, index) => (
        <div
          key={message.id}
          ref={index === visibleMessages.length - 1 ? lastMessageRef : null}
        >
          <MessageBubble
            message={message}
            isStreaming={false}
            onCopy={onCopy}
          />
        </div>
      ))}

      {/* Streaming message */}
      {isStreaming && streamingContent && (
        <MessageBubble
          message={{
            id: 'streaming',
            role: 'assistant',
            content: streamingContent,
            timestamp: new Date(),
          }}
          isStreaming={true}
        />
      )}

      {/* Typing indicator */}
      {isStreaming && !streamingContent && (
        <div className="flex justify-start">
          <TypingIndicator visible={true} />
        </div>
      )}

      {/* Scroll to bottom button */}
      {!autoScroll && (
        <button
          onClick={() => {
            setAutoScroll(true);
            scrollContainerRef.current?.scrollTo({
              top: scrollContainerRef.current.scrollHeight,
              behavior: 'smooth',
            });
          }}
          className="fixed bottom-24 right-8 p-3 bg-purple-600 text-white rounded-full shadow-lg hover:bg-purple-700 transition-colors"
          aria-label="Scroll to bottom"
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
              d="M19 14l-7 7m0 0l-7-7m7 7V3"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
