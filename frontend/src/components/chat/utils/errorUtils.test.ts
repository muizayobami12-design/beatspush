/**
 * Error Utilities - Unit tests
 */

import { describe, it, expect } from 'vitest';
import {
  createChatError,
  classifyError,
  fromError,
  isRetryable,
  requiresUserAction,
  extractRetryDelay,
  shouldAutoRetry,
  formatErrorMessage,
  getDisplayMessage,
  isQuotaError,
  isAuthError,
  isConnectionError,
  isTimeoutError,
  toLoggableError,
  mergeErrors,
  fromHttpResponse,
} from './errorUtils';
import { ChatErrorType } from '../types';
import type { ChatError } from '../types';

describe('errorUtils', () => {
  describe('createChatError', () => {
    it('should create error with correct type and message', () => {
      const error = createChatError(ChatErrorType.MESSAGE_SEND_FAILED);
      
      expect(error.type).toBe(ChatErrorType.MESSAGE_SEND_FAILED);
      expect(error.message).toBeDefined();
      expect(error.retryable).toBe(true);
      expect(error.action).toBe('retry');
    });

    it('should use custom message when provided', () => {
      const customMessage = 'Custom error message';
      const error = createChatError(ChatErrorType.SERVER_ERROR, customMessage);
      
      expect(error.message).toBe(customMessage);
    });

    it('should set retryable to false for QUOTA_EXCEEDED', () => {
      const error = createChatError(ChatErrorType.QUOTA_EXCEEDED);
      
      expect(error.retryable).toBe(false);
      expect(error.action).toBe('upgrade');
    });

    it('should set action to login for AUTHENTICATION_FAILED', () => {
      const error = createChatError(ChatErrorType.AUTHENTICATION_FAILED);
      
      expect(error.action).toBe('login');
    });

    it('should set action to wait for RATE_LIMIT', () => {
      const error = createChatError(ChatErrorType.RATE_LIMIT);
      
      expect(error.action).toBe('wait');
    });
  });

  describe('classifyError', () => {
    it('should classify 401 status as AUTHENTICATION_FAILED', () => {
      const type = classifyError({ status: 401 });
      expect(type).toBe(ChatErrorType.AUTHENTICATION_FAILED);
    });

    it('should classify 429 status as RATE_LIMIT', () => {
      const type = classifyError({ status: 429 });
      expect(type).toBe(ChatErrorType.RATE_LIMIT);
    });

    it('should classify 503 status as SERVER_ERROR', () => {
      const type = classifyError({ status: 503 });
      expect(type).toBe(ChatErrorType.SERVER_ERROR);
    });

    it('should classify quota error message', () => {
      const type = classifyError('Quota exceeded for this request');
      expect(type).toBe(ChatErrorType.QUOTA_EXCEEDED);
    });

    it('should classify timeout error message', () => {
      const type = classifyError('Request timed out after 30 seconds');
      expect(type).toBe(ChatErrorType.TIMEOUT);
    });

    it('should classify connection error message', () => {
      const type = classifyError('Connection failed to establish');
      expect(type).toBe(ChatErrorType.CONNECTION_FAILED);
    });

    it('should classify Error object', () => {
      const error = new Error('Connection lost');
      const type = classifyError(error);
      expect(type).toBe(ChatErrorType.CONNECTION_FAILED);
    });

    it('should default to SERVER_ERROR for unknown errors', () => {
      const type = classifyError({ unknown: 'error' });
      expect(type).toBe(ChatErrorType.SERVER_ERROR);
    });
  });

  describe('fromError', () => {
    it('should create ChatError from string', () => {
      const error = fromError('Connection failed');
      
      expect(error.type).toBe(ChatErrorType.CONNECTION_FAILED);
      expect(error.message).toBe('Connection failed');
    });

    it('should create ChatError from Error object', () => {
      const jsError = new Error('Quota exceeded');
      const error = fromError(jsError);
      
      expect(error.type).toBe(ChatErrorType.QUOTA_EXCEEDED);
      expect(error.message).toBe('Quota exceeded');
    });

    it('should create ChatError from object with message', () => {
      const obj = { status: 429, message: 'Too many requests' };
      const error = fromError(obj);
      
      expect(error.type).toBe(ChatErrorType.RATE_LIMIT);
      expect(error.message).toBe('Too many requests');
    });
  });

  describe('isRetryable', () => {
    it('should return true for retryable errors', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      expect(isRetryable(error)).toBe(true);
    });

    it('should return false for non-retryable errors', () => {
      const error = createChatError(ChatErrorType.QUOTA_EXCEEDED);
      expect(isRetryable(error)).toBe(false);
    });
  });

  describe('requiresUserAction', () => {
    it('should return true for upgrade action', () => {
      const error = createChatError(ChatErrorType.QUOTA_EXCEEDED);
      expect(requiresUserAction(error)).toBe(true);
    });

    it('should return true for login action', () => {
      const error = createChatError(ChatErrorType.AUTHENTICATION_FAILED);
      expect(requiresUserAction(error)).toBe(true);
    });

    it('should return false for retry action', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      expect(requiresUserAction(error)).toBe(false);
    });
  });

  describe('extractRetryDelay', () => {
    it('should extract delay from error message', () => {
      const error = createChatError(
        ChatErrorType.RATE_LIMIT,
        'Please wait 30 seconds before trying again'
      );
      
      const delay = extractRetryDelay(error);
      expect(delay).toBe(30);
    });

    it('should return default delay for RATE_LIMIT', () => {
      const error = createChatError(ChatErrorType.RATE_LIMIT);
      const delay = extractRetryDelay(error);
      expect(delay).toBe(60);
    });

    it('should return default delay for CONNECTION_FAILED', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      const delay = extractRetryDelay(error);
      expect(delay).toBe(5);
    });

    it('should return 0 for TIMEOUT', () => {
      const error = createChatError(ChatErrorType.TIMEOUT);
      const delay = extractRetryDelay(error);
      expect(delay).toBe(0);
    });

    it('should return null for errors without delay', () => {
      const error = createChatError(ChatErrorType.QUOTA_EXCEEDED);
      const delay = extractRetryDelay(error);
      expect(delay).toBe(null);
    });
  });

  describe('shouldAutoRetry', () => {
    it('should return true for CONNECTION_FAILED', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      expect(shouldAutoRetry(error)).toBe(true);
    });

    it('should return true for STREAMING_INTERRUPTED', () => {
      const error = createChatError(ChatErrorType.STREAMING_INTERRUPTED);
      expect(shouldAutoRetry(error)).toBe(true);
    });

    it('should return false for QUOTA_EXCEEDED', () => {
      const error = createChatError(ChatErrorType.QUOTA_EXCEEDED);
      expect(shouldAutoRetry(error)).toBe(false);
    });

    it('should return false for AUTHENTICATION_FAILED', () => {
      const error = createChatError(ChatErrorType.AUTHENTICATION_FAILED);
      expect(shouldAutoRetry(error)).toBe(false);
    });
  });

  describe('formatErrorMessage', () => {
    it('should replace placeholders with values', () => {
      const template = 'Connection lost. Retrying in {seconds}s...';
      const formatted = formatErrorMessage(template, { seconds: 5 });
      
      expect(formatted).toBe('Connection lost. Retrying in 5s...');
    });

    it('should replace multiple placeholders', () => {
      const template = 'Failed after {attempts} attempts. Wait {seconds} seconds.';
      const formatted = formatErrorMessage(template, { attempts: 3, seconds: 30 });
      
      expect(formatted).toBe('Failed after 3 attempts. Wait 30 seconds.');
    });

    it('should handle missing placeholders gracefully', () => {
      const template = 'Error: {message}';
      const formatted = formatErrorMessage(template, { other: 'value' });
      
      expect(formatted).toBe('Error: {message}');
    });
  });

  describe('getDisplayMessage', () => {
    it('should return error message without params', () => {
      const error = createChatError(ChatErrorType.SERVER_ERROR, 'Service unavailable');
      const message = getDisplayMessage(error);
      
      expect(message).toBe('Service unavailable');
    });

    it('should format message with params', () => {
      const error = createChatError(
        ChatErrorType.RATE_LIMIT,
        'Please wait {seconds} seconds'
      );
      const message = getDisplayMessage(error, { seconds: 30 });
      
      expect(message).toBe('Please wait 30 seconds');
    });
  });

  describe('isQuotaError', () => {
    it('should return true for QUOTA_EXCEEDED', () => {
      const error = createChatError(ChatErrorType.QUOTA_EXCEEDED);
      expect(isQuotaError(error)).toBe(true);
    });

    it('should return false for other error types', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      expect(isQuotaError(error)).toBe(false);
    });
  });

  describe('isAuthError', () => {
    it('should return true for AUTHENTICATION_FAILED', () => {
      const error = createChatError(ChatErrorType.AUTHENTICATION_FAILED);
      expect(isAuthError(error)).toBe(true);
    });

    it('should return false for other error types', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      expect(isAuthError(error)).toBe(false);
    });
  });

  describe('isConnectionError', () => {
    it('should return true for CONNECTION_FAILED', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      expect(isConnectionError(error)).toBe(true);
    });

    it('should return true for WEBSOCKET_CLOSED', () => {
      const error = createChatError(ChatErrorType.WEBSOCKET_CLOSED);
      expect(isConnectionError(error)).toBe(true);
    });

    it('should return false for other error types', () => {
      const error = createChatError(ChatErrorType.TIMEOUT);
      expect(isConnectionError(error)).toBe(false);
    });
  });

  describe('isTimeoutError', () => {
    it('should return true for TIMEOUT', () => {
      const error = createChatError(ChatErrorType.TIMEOUT);
      expect(isTimeoutError(error)).toBe(true);
    });

    it('should return false for other error types', () => {
      const error = createChatError(ChatErrorType.CONNECTION_FAILED);
      expect(isTimeoutError(error)).toBe(false);
    });
  });

  describe('toLoggableError', () => {
    it('should convert error to loggable format', () => {
      const error = createChatError(ChatErrorType.SERVER_ERROR, 'Service down');
      const loggable = toLoggableError(error);
      
      expect(loggable).toHaveProperty('type', ChatErrorType.SERVER_ERROR);
      expect(loggable).toHaveProperty('message', 'Service down');
      expect(loggable).toHaveProperty('retryable');
      expect(loggable).toHaveProperty('action');
      expect(loggable).toHaveProperty('timestamp');
    });

    it('should include timestamp in ISO format', () => {
      const error = createChatError(ChatErrorType.SERVER_ERROR);
      const loggable = toLoggableError(error);
      
      expect(loggable.timestamp).toMatch(/^\d{4}-\d{2}-\d{2}T/);
    });
  });

  describe('mergeErrors', () => {
    it('should return single error for array with one error', () => {
      const error = createChatError(ChatErrorType.SERVER_ERROR);
      const merged = mergeErrors([error]);
      
      expect(merged).toBe(error);
    });

    it('should prioritize AUTHENTICATION_FAILED', () => {
      const errors: ChatError[] = [
        createChatError(ChatErrorType.SERVER_ERROR),
        createChatError(ChatErrorType.AUTHENTICATION_FAILED),
        createChatError(ChatErrorType.CONNECTION_FAILED),
      ];
      
      const merged = mergeErrors(errors);
      expect(merged.type).toBe(ChatErrorType.AUTHENTICATION_FAILED);
    });

    it('should prioritize QUOTA_EXCEEDED over CONNECTION_FAILED', () => {
      const errors: ChatError[] = [
        createChatError(ChatErrorType.CONNECTION_FAILED),
        createChatError(ChatErrorType.QUOTA_EXCEEDED),
      ];
      
      const merged = mergeErrors(errors);
      expect(merged.type).toBe(ChatErrorType.QUOTA_EXCEEDED);
    });

    it('should return first error if no priority match', () => {
      const errors: ChatError[] = [
        createChatError(ChatErrorType.MESSAGE_SEND_FAILED),
        createChatError(ChatErrorType.STREAMING_INTERRUPTED),
      ];
      
      const merged = mergeErrors(errors);
      expect(merged.type).toBe(ChatErrorType.MESSAGE_SEND_FAILED);
    });

    it('should handle empty array', () => {
      const merged = mergeErrors([]);
      expect(merged.type).toBe(ChatErrorType.SERVER_ERROR);
      expect(merged.message).toBe('Unknown error occurred');
    });
  });

  describe('fromHttpResponse', () => {
    it('should create AUTHENTICATION_FAILED for 401', () => {
      const response = new Response(null, { status: 401 });
      const error = fromHttpResponse(response);
      
      expect(error.type).toBe(ChatErrorType.AUTHENTICATION_FAILED);
    });

    it('should create RATE_LIMIT for 429', () => {
      const response = new Response(null, { status: 429 });
      const error = fromHttpResponse(response);
      
      expect(error.type).toBe(ChatErrorType.RATE_LIMIT);
    });

    it('should create SERVER_ERROR for 503', () => {
      const response = new Response(null, { status: 503 });
      const error = fromHttpResponse(response);
      
      expect(error.type).toBe(ChatErrorType.SERVER_ERROR);
    });

    it('should use custom message from errorData', () => {
      const response = new Response(null, { status: 401 });
      const errorData = { message: 'Token expired' };
      const error = fromHttpResponse(response, errorData);
      
      expect(error.message).toBe('Token expired');
    });

    it('should extract retry-after header', () => {
      const headers = new Headers({ 'Retry-After': '60' });
      const response = new Response(null, { status: 429, headers });
      const error = fromHttpResponse(response);
      
      expect((error as any).retryAfter).toBe(60);
    });
  });
});
