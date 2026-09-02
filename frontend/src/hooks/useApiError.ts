/**
 * Hook for handling API errors with toast notifications
 */

import { useCallback } from 'react';
import { useToast } from './useToast';
import {
  getErrorMessage,
  isNetworkError,
  isAuthenticationError,
  isAuthorizationError,
  isValidationError,
  isServerError,
} from '@/lib/api/client';

export interface ErrorOptions {
  showToast?: boolean;
  silent?: boolean;
  customMessage?: string;
}

/**
 * Hook for handling API errors
 */
export function useApiError() {
  const { toast } = useToast();

  /**
   * Handle error and optionally show toast
   */
  const handleError = useCallback(
    (error: unknown, options: ErrorOptions = {}) => {
      const { showToast: show = true, silent = false, customMessage } = options;

      const message = customMessage || getErrorMessage(error);

      // Determine error type and toast variant
      let variant: 'default' | 'destructive' | 'warning' | 'success' = 'destructive';

      if (isNetworkError(error)) {
        variant = 'warning';
      } else if (isServerError(error)) {
        variant = 'destructive';
      }

      // Show toast unless silent
      if (show && !silent) {
        toast({
          title: 'Error',
          description: message,
          variant,
        });
      }

      // Log in development
      if (process.env.NODE_ENV === 'development') {
        console.error('[useApiError]', {
          error,
          message,
          type: {
            network: isNetworkError(error),
            authentication: isAuthenticationError(error),
            authorization: isAuthorizationError(error),
            validation: isValidationError(error),
            server: isServerError(error),
          },
        });
      }

      return {
        message,
        isNetworkError: isNetworkError(error),
        isAuthenticationError: isAuthenticationError(error),
        isAuthorizationError: isAuthorizationError(error),
        isValidationError: isValidationError(error),
        isServerError: isServerError(error),
      };
    },
    [toast]
  );

  return {
    handleError,
    isNetworkError,
    isAuthenticationError,
    isAuthorizationError,
    isValidationError,
    isServerError,
  };
}

export default useApiError;
