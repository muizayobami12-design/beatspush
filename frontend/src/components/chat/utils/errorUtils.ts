/**
 * Error Utilities - Helper functions for error handling in AI Chat Interface
 * Provides utilities for creating, classifying, and transforming errors
 */

import { ChatErrorType, type ChatError, type ErrorAction } from '../types';
import { ERROR_MESSAGES } from '../constants';

/**
 * Create a ChatError from an error type and optional custom message
 */
export function createChatError(
  type: ChatErrorType,
  customMessage?: string,
  metadata?: Record<string, any>
): ChatError {
  const baseMessage = ERROR_MESSAGES[type];
  const message = customMessage || baseMessage;
  
  // Determine if error is retryable based on type
  const retryable = [
    ChatErrorType.CONNECTION_FAILED,
    ChatErrorType.WEBSOCKET_CLOSED,
    ChatErrorType.MESSAGE_SEND_FAILED,
    ChatErrorType.STREAMING_INTERRUPTED,
    ChatErrorType.TIMEOUT,
    ChatErrorType.SERVER_ERROR,
  ].includes(type);
  
  // Determine appropriate action based on error type
  let action: ErrorAction | undefined;
  switch (type) {
    case ChatErrorType.QUOTA_EXCEEDED:
      action = 'upgrade';
      break;
    case ChatErrorType.AUTHENTICATION_FAILED:
      action = 'login';
      break;
    case ChatErrorType.RATE_LIMIT:
      action = 'wait';
      break;
    case ChatErrorType.CONNECTION_FAILED:
    case ChatErrorType.WEBSOCKET_CLOSED:
    case ChatErrorType.MESSAGE_SEND_FAILED:
    case ChatErrorType.STREAMING_INTERRUPTED:
    case ChatErrorType.TIMEOUT:
    case ChatErrorType.SERVER_ERROR:
      action = 'retry';
      break;
    default:
      action = undefined;
  }
  
  return {
    type,
    message,
    retryable,
    action,
    ...metadata,
  };
}

/**
 * Classify an error from WebSocket or HTTP response
 * Maps status codes and error messages to ChatErrorType
 */
export function classifyError(error: any): ChatErrorType {
  // Handle HTTP status codes
  if (typeof error === 'object' && 'status' in error) {
    const status = error.status;
    
    if (status === 401 || status === 403) {
      return ChatErrorType.AUTHENTICATION_FAILED;
    }
    if (status === 429) {
      return ChatErrorType.RATE_LIMIT;
    }
    if (status === 503 || status === 502 || status === 504) {
      return ChatErrorType.SERVER_ERROR;
    }
  }
  
  // Handle error messages
  if (typeof error === 'string') {
    const lowerError = error.toLowerCase();
    
    if (lowerError.includes('quota') || lowerError.includes('limit exceeded')) {
      return ChatErrorType.QUOTA_EXCEEDED;
    }
    if (lowerError.includes('rate limit') || lowerError.includes('too many requests')) {
      return ChatErrorType.RATE_LIMIT;
    }
    if (lowerError.includes('timeout') || lowerError.includes('timed out')) {
      return ChatErrorType.TIMEOUT;
    }
    if (lowerError.includes('authentication') || lowerError.includes('unauthorized')) {
      return ChatErrorType.AUTHENTICATION_FAILED;
    }
    if (lowerError.includes('connection') || lowerError.includes('network')) {
      return ChatErrorType.CONNECTION_FAILED;
    }
  }
  
  // Handle Error objects
  if (error instanceof Error) {
    return classifyError(error.message);
  }
  
  // Default to server error for unknown errors
  return ChatErrorType.SERVER_ERROR;
}

/**
 * Create a ChatError from a generic error or exception
 */
export function fromError(error: any): ChatError {
  const errorType = classifyError(error);
  
  let message: string;
  if (typeof error === 'string') {
    message = error;
  } else if (error instanceof Error) {
    message = error.message;
  } else if (typeof error === 'object' && 'message' in error) {
    message = error.message;
  } else {
    message = ERROR_MESSAGES[errorType];
  }
  
  return createChatError(errorType, message);
}

/**
 * Check if an error is retryable
 */
export function isRetryable(error: ChatError): boolean {
  return error.retryable;
}

/**
 * Check if an error requires user action (upgrade, login, wait)
 */
export function requiresUserAction(error: ChatError): boolean {
  return error.action !== 'retry' && error.action !== undefined;
}

/**
 * Extract retry delay from error message or metadata
 * Returns delay in seconds
 */
export function extractRetryDelay(error: ChatError): number | null {
  // Check if error message contains retry delay information
  const match = error.message.match(/wait (\d+) seconds?/i);
  if (match) {
    return parseInt(match[1], 10);
  }
  
  // Check metadata for retry-after header
  if (error && typeof error === 'object' && 'retryAfter' in error) {
    const retryAfter = (error as any).retryAfter;
    if (typeof retryAfter === 'number') {
      return retryAfter;
    }
    if (typeof retryAfter === 'string') {
      const parsed = parseInt(retryAfter, 10);
      if (!isNaN(parsed)) {
        return parsed;
      }
    }
  }
  
  // Default retry delays based on error type
  switch (error.type) {
    case ChatErrorType.RATE_LIMIT:
      return 60; // 60 seconds for rate limit
    case ChatErrorType.CONNECTION_FAILED:
      return 5; // 5 seconds for connection failure
    case ChatErrorType.TIMEOUT:
      return 0; // Immediate retry for timeout
    default:
      return null;
  }
}

/**
 * Check if an error should trigger auto-retry
 */
export function shouldAutoRetry(error: ChatError): boolean {
  const autoRetryTypes: ChatErrorType[] = [
    ChatErrorType.CONNECTION_FAILED,
    ChatErrorType.STREAMING_INTERRUPTED,
    ChatErrorType.MESSAGE_SEND_FAILED,
    ChatErrorType.TIMEOUT,
  ];
  
  return autoRetryTypes.includes(error.type);
}

/**
 * Format error message with dynamic values
 * Replaces {key} placeholders with values from params
 */
export function formatErrorMessage(
  message: string,
  params: Record<string, string | number>
): string {
  let formatted = message;
  
  Object.entries(params).forEach(([key, value]) => {
    formatted = formatted.replace(`{${key}}`, String(value));
  });
  
  return formatted;
}

/**
 * Get user-friendly error message for display
 * Handles dynamic value replacement
 */
export function getDisplayMessage(
  error: ChatError,
  params?: Record<string, string | number>
): string {
  if (!params) {
    return error.message;
  }
  
  return formatErrorMessage(error.message, params);
}

/**
 * Check if error is a quota-related error
 */
export function isQuotaError(error: ChatError): boolean {
  return error.type === ChatErrorType.QUOTA_EXCEEDED;
}

/**
 * Check if error is an authentication error
 */
export function isAuthError(error: ChatError): boolean {
  return error.type === ChatErrorType.AUTHENTICATION_FAILED;
}

/**
 * Check if error is a connection error
 */
export function isConnectionError(error: ChatError): boolean {
  return [
    ChatErrorType.CONNECTION_FAILED,
    ChatErrorType.WEBSOCKET_CLOSED,
  ].includes(error.type);
}

/**
 * Check if error is a timeout error
 */
export function isTimeoutError(error: ChatError): boolean {
  return error.type === ChatErrorType.TIMEOUT;
}

/**
 * Convert error to loggable format (removes sensitive data)
 */
export function toLoggableError(error: ChatError): Record<string, any> {
  return {
    type: error.type,
    message: error.message,
    retryable: error.retryable,
    action: error.action,
    timestamp: new Date().toISOString(),
  };
}

/**
 * Merge multiple errors into a single error message
 * Useful when multiple operations fail
 */
export function mergeErrors(errors: ChatError[]): ChatError {
  if (errors.length === 0) {
    return createChatError(ChatErrorType.SERVER_ERROR, 'Unknown error occurred');
  }
  
  if (errors.length === 1) {
    return errors[0];
  }
  
  // Prioritize certain error types
  const priorityOrder = [
    ChatErrorType.AUTHENTICATION_FAILED,
    ChatErrorType.QUOTA_EXCEEDED,
    ChatErrorType.RATE_LIMIT,
    ChatErrorType.CONNECTION_FAILED,
    ChatErrorType.TIMEOUT,
    ChatErrorType.SERVER_ERROR,
  ];
  
  for (const type of priorityOrder) {
    const error = errors.find((e) => e.type === type);
    if (error) {
      return error;
    }
  }
  
  // Return first error if no priority match
  return errors[0];
}

/**
 * Create error from HTTP response
 */
export function fromHttpResponse(response: Response, errorData?: any): ChatError {
  const status = response.status;
  
  // Map status codes to error types
  let errorType: ChatErrorType;
  let message: string;
  
  switch (status) {
    case 401:
    case 403:
      errorType = ChatErrorType.AUTHENTICATION_FAILED;
      message = errorData?.message || 'Authentication failed. Please log in again.';
      break;
    case 429:
      errorType = ChatErrorType.RATE_LIMIT;
      message = errorData?.message || 'Too many requests. Please wait before trying again.';
      break;
    case 503:
    case 502:
    case 504:
      errorType = ChatErrorType.SERVER_ERROR;
      message = errorData?.message || 'Service temporarily unavailable. Please try again later.';
      break;
    default:
      errorType = ChatErrorType.SERVER_ERROR;
      message = errorData?.message || `Request failed with status ${status}`;
  }
  
  const error = createChatError(errorType, message);
  
  // Add retry-after header if present
  const retryAfter = response.headers.get('Retry-After');
  if (retryAfter) {
    (error as any).retryAfter = parseInt(retryAfter, 10);
  }
  
  return error;
}
