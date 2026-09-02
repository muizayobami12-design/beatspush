/**
 * MessageBubble - Display individual chat messages
 */

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import type { MessageBubbleProps } from '../types';
import { CopyButton } from './CopyButton';
import { cn } from '@/lib/utils';

export const MessageBubble: React.FC<MessageBubbleProps> = React.memo(({
  message,
  isStreaming = false,
  onCopy,
}) => {
  const isUser = message.role === 'user';
  const isAssistant = message.role === 'assistant';

  return (
    <div
      className={cn(
        'flex w-full animate-in fade-in duration-200',
        isUser ? 'justify-end' : 'justify-start'
      )}
    >
      <div
        className={cn(
          'group relative max-w-[80%] rounded-2xl px-4 py-3 shadow-sm',
          isUser && 'bg-gradient-to-r from-purple-500 to-blue-500 text-white',
          isAssistant && 'bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20 border border-purple-200/50 dark:border-purple-700/50',
          isStreaming && 'animate-pulse'
        )}
      >
        {/* Copy button for AI messages */}
        {isAssistant && !isStreaming && (
          <div className="absolute -top-2 -right-2">
            <CopyButton content={message.content} onCopy={onCopy} />
          </div>
        )}

        {/* Message content */}
        <div className={cn(
          'prose prose-sm max-w-none',
          isUser && 'prose-invert',
          isAssistant && 'prose-purple dark:prose-invert'
        )}>
          {isAssistant ? (
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeSanitize]}
              components={{
                // Custom renderers for markdown elements
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                a: ({ href, children }) => (
                  <a
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-purple-600 dark:text-purple-400 hover:underline"
                  >
                    {children}
                  </a>
                ),
                code: ({ inline, children, ...props }: any) =>
                  inline ? (
                    <code
                      className="px-1.5 py-0.5 rounded bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 text-sm font-mono"
                      {...props}
                    >
                      {children}
                    </code>
                  ) : (
                    <code
                      className="block p-3 rounded-lg bg-gray-900 text-gray-100 text-sm font-mono overflow-x-auto"
                      {...props}
                    >
                      {children}
                    </code>
                  ),
                ul: ({ children }) => <ul className="list-disc list-inside mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="list-decimal list-inside mb-2">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                h1: ({ children }) => <h1 className="text-xl font-bold mb-2">{children}</h1>,
                h2: ({ children }) => <h2 className="text-lg font-bold mb-2">{children}</h2>,
                h3: ({ children }) => <h3 className="text-base font-bold mb-2">{children}</h3>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          ) : (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          )}
        </div>

        {/* Timestamp */}
        <div
          className={cn(
            'mt-1 text-xs opacity-70',
            isUser ? 'text-white' : 'text-gray-500 dark:text-gray-400'
          )}
        >
          {new Date(message.timestamp).toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit',
          })}
        </div>
      </div>
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';

export default MessageBubble;
