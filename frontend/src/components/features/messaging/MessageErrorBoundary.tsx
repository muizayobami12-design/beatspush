'use client';

import React, { ReactNode, ReactElement, ErrorInfo } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Props {
  children: ReactNode;
  fallback?: (error: Error, retry: () => void) => ReactElement;
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * MessageErrorBoundary — catches errors in messaging components.
 * Shows user-friendly error message with retry button.
 * Logs errors to monitoring service (Sentry integration point).
 * Requirements: 27.1, 27.3
 */
export class MessageErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log to console in development
    console.error('Messaging Error:', error, errorInfo);

    // Log to monitoring service (Sentry, etc.)
    // Example: Sentry.captureException(error, { contexts: { react: errorInfo } });
    if (typeof window !== 'undefined' && window.__SENTRY__) {
      try {
        window.__SENTRY__.captureException(error, {
          contexts: {
            react: {
              componentStack: errorInfo.componentStack,
            },
          },
        });
      } catch (e) {
        console.error('Failed to log to Sentry:', e);
      }
    }

    // Call custom error handler if provided
    this.props.onError?.(error, errorInfo);
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError && this.state.error) {
      if (this.props.fallback) {
        return this.props.fallback(this.state.error, this.handleRetry);
      }

      return (
        <div className="flex flex-col items-center justify-center p-8 text-center min-h-[400px]">
          <div className="mb-4 p-3 rounded-lg bg-destructive/10">
            <AlertCircle className="h-8 w-8 text-destructive mx-auto" />
          </div>
          <h2 className="text-lg font-semibold mb-2">Something went wrong</h2>
          <p className="text-sm text-muted-foreground mb-4 max-w-md">
            {this.state.error.message ||
              'An unexpected error occurred while loading your messages. Please try again.'}
          </p>
          <Button
            onClick={this.handleRetry}
            className="gap-2"
          >
            <RefreshCw className="h-4 w-4" />
            Try again
          </Button>
          <p className="text-xs text-muted-foreground mt-4">
            Error ID: {this.state.error.message?.substring(0, 20) || 'unknown'}
          </p>
        </div>
      );
    }

    return this.props.children;
  }
}

export default MessageErrorBoundary;
