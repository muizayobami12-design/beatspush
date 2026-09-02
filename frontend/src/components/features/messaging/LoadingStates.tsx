'use client';

import React from 'react';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';

/**
 * ConversationListSkeleton — skeleton loader for conversation list.
 */
export function ConversationListSkeleton() {
  return (
    <div className="space-y-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="flex items-center gap-3 p-4">
          <Skeleton className="h-10 w-10 rounded-full flex-shrink-0" />
          <div className="flex-1 space-y-2">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-3 w-full" />
          </div>
        </div>
      ))}
    </div>
  );
}

/**
 * MessageThreadSkeleton — skeleton loader for message thread.
 */
export function MessageThreadSkeleton() {
  return (
    <div className="space-y-4 p-4">
      <div className="flex gap-3">
        <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
        <div className="flex-1 max-w-xs space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-12 w-full" />
        </div>
      </div>

      <div className="flex justify-end">
        <div className="max-w-xs space-y-2">
          <Skeleton className="h-12 w-full" />
          <Skeleton className="h-3 w-20 ml-auto" />
        </div>
      </div>

      <div className="flex gap-3">
        <Skeleton className="h-8 w-8 rounded-full flex-shrink-0" />
        <div className="flex-1 max-w-xs space-y-2">
          <Skeleton className="h-4 w-32" />
          <Skeleton className="h-12 w-full" />
        </div>
      </div>
    </div>
  );
}

/**
 * MessageInputSkeleton — skeleton loader for message input.
 */
export function MessageInputSkeleton() {
  return (
    <div className="flex gap-2 p-4">
      <Skeleton className="h-10 w-10 flex-shrink-0" />
      <Skeleton className="h-10 flex-1" />
      <Skeleton className="h-10 w-10 flex-shrink-0" />
    </div>
  );
}

/**
 * FileUploadProgressBar — progress indicator for file uploads.
 */
interface FileUploadProgressBarProps {
  fileName: string;
  progress: number; // 0-100
  status?: 'uploading' | 'processing' | 'complete' | 'error';
  error?: string;
  onCancel?: () => void;
}

export function FileUploadProgressBar({
  fileName,
  progress,
  status = 'uploading',
  error,
  onCancel,
}: FileUploadProgressBarProps) {
  return (
    <div className="space-y-2 p-3 rounded-lg bg-muted/50 border border-border">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium truncate">{fileName}</p>
        {status === 'uploading' && (
          <span className="text-xs text-muted-foreground">{progress}%</span>
        )}
        {status === 'complete' && (
          <span className="text-xs text-green-600">Done</span>
        )}
        {status === 'error' && (
          <span className="text-xs text-destructive">Failed</span>
        )}
      </div>

      <div className="w-full bg-muted h-2 rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full transition-all duration-200',
            status === 'error' ? 'bg-destructive' : 'bg-primary'
          )}
          style={{ width: `${Math.max(0, Math.min(100, progress))}%` }}
        />
      </div>

      {error && (
        <p className="text-xs text-destructive">{error}</p>
      )}

      {status === 'uploading' && onCancel && (
        <button
          onClick={onCancel}
          className="text-xs text-muted-foreground hover:text-foreground underline"
        >
          Cancel
        </button>
      )}
    </div>
  );
}

/**
 * EmptyStateMessage — display empty state for various messaging scenarios.
 */
interface EmptyStateProps {
  title: string;
  description?: string;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export function EmptyState({
  title,
  description,
  action,
  icon,
  className,
}: EmptyStateProps) {
  return (
    <div
      className={cn(
        'flex flex-col items-center justify-center py-12 px-4 text-center',
        className
      )}
    >
      {icon && <div className="mb-4 text-muted-foreground">{icon}</div>}
      <h3 className="text-lg font-semibold mb-2">{title}</h3>
      {description && (
        <p className="text-sm text-muted-foreground max-w-sm">{description}</p>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

/**
 * OfflineIndicator — show when connection is lost.
 */
export function OfflineIndicator() {
  return (
    <div className="flex items-center justify-center gap-2 p-3 bg-amber-50 border border-amber-200 rounded-md text-sm text-amber-800">
      <div className="h-2 w-2 rounded-full bg-amber-500" />
      <span>You&apos;re offline. Messages will sync when you reconnect.</span>
    </div>
  );
}

/**
 * RateLimitWarning — show when rate limit is approaching.
 */
interface RateLimitWarningProps {
  messagesRemaining: number;
  resetIn: number; // seconds
}

export function RateLimitWarning({
  messagesRemaining,
  resetIn,
}: RateLimitWarningProps) {
  return (
    <div className="flex items-center justify-center gap-2 p-3 bg-orange-50 border border-orange-200 rounded-md text-sm text-orange-800">
      <span>
        Slow down! {messagesRemaining} messages remaining. Resets in {resetIn}s.
      </span>
    </div>
  );
}

/**
 * LoadingSpinner — simple loading indicator.
 */
interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  message?: string;
  className?: string;
}

export function LoadingSpinner({
  size = 'md',
  message,
  className,
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-6 w-6',
    lg: 'h-8 w-8',
  };

  return (
    <div
      className={cn('flex flex-col items-center justify-center gap-2', className)}
    >
      <div className={cn('animate-spin text-muted-foreground', sizeClasses[size])}>
        <svg
          className="w-full h-full"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"
          />
        </svg>
      </div>
      {message && <p className="text-sm text-muted-foreground">{message}</p>}
    </div>
  );
}

const loadingStateExports = {
  ConversationListSkeleton,
  MessageThreadSkeleton,
  MessageInputSkeleton,
  FileUploadProgressBar,
  EmptyState,
  OfflineIndicator,
  RateLimitWarning,
  LoadingSpinner,
};

export default loadingStateExports;
