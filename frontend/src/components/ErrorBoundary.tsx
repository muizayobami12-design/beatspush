/**
 * Error Boundary Component
 * Catches rendering errors and displays fallback UI
 */

'use client';

import React, { ReactNode } from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
  onReset?: () => void;
}

interface State {
  hasError: boolean;
  error?: Error;
}

/**
 * Error Boundary component
 */
export class ErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log error details
    console.error('[ErrorBoundary] Caught error:', {
      error,
      componentStack: errorInfo.componentStack,
    });

    // Send to error tracking service (e.g., Sentry)
    // captureException(error, { contexts: { react: { componentStack: errorInfo.componentStack } } });
  }

  handleReset = () => {
    this.setState({ hasError: false, error: undefined });
    this.props.onReset?.();
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback;
      }

      return (
        <div
          className={cn(
            'min-h-screen flex items-center justify-center',
            'bg-gradient-to-br from-surface to-surface-container',
            'p-4'
          )}
        >
          <div
            className={cn(
              'max-w-md w-full bg-white rounded-lg shadow-lg p-8',
              'border border-destructive/20'
            )}
          >
            {/* Error Icon */}
            <div
              className={cn(
                'flex justify-center mb-6',
                'w-16 h-16 mx-auto rounded-full',
                'bg-destructive/10 flex items-center justify-center'
              )}
            >
              <AlertTriangle className="h-8 w-8 text-destructive" />
            </div>

            {/* Error Title */}
            <h1 className={cn('font-headline-md text-headline-md text-center text-on-surface mb-2')}>
              Oops! Something went wrong
            </h1>

            {/* Error Message */}
            <p className={cn('font-body-md text-body-md text-center text-on-surface-variant mb-6')}>
              We encountered an unexpected error. Please try again or contact support if the problem
              persists.
            </p>

            {/* Error Details (Development Only) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <div
                className={cn(
                  'mb-6 p-3 rounded-lg bg-destructive/5 border border-destructive/20',
                  'max-h-32 overflow-auto'
                )}
              >
                <p className={cn('font-label-xs text-label-xs text-destructive font-mono')}>
                  {this.state.error.message}
                </p>
              </div>
            )}

            {/* Actions */}
            <div className={cn('flex gap-3')}>
              <Button
                variant="outline"
                onClick={() => window.location.href = '/'}
                className="flex-1"
              >
                Go Home
              </Button>
              <Button variant="default" onClick={this.handleReset} className={cn('flex-1 gap-2')}>
                <RefreshCw className="h-4 w-4" />
                Try Again
              </Button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
