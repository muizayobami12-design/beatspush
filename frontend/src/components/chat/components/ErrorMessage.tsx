/**
 * ErrorMessage - Display error messages with retry button
 * Shows user-friendly error messages in conversation as system messages
 */

'use client';

import React, { useState, useEffect } from 'react';
import { AlertCircle, RotateCcw, LogIn, Clock, Zap } from 'lucide-react';
import type { ChatError } from '../types';
import { ChatErrorType } from '../types';
import { getErrorMessage } from '../constants';

interface ErrorMessageProps {
  error: ChatError;
  onRetry?: () => void;
  onUpgrade?: () => void;
  onLogin?: () => void;
}

export function ErrorMessage({ error, onRetry, onUpgrade, onLogin }: ErrorMessageProps) {
  const [countdown, setCountdown] = useState<number>(0);
  const [cooldownSeconds, setCooldownSeconds] = useState<number>(0);

  // Handle CONNECTION_FAILED with auto-retry countdown
  useEffect(() => {
    if (error.type === ChatErrorType.CONNECTION_FAILED && onRetry) {
      // Start 5 second countdown
      setCountdown(5);
      
      const interval = setInterval(() => {
        setCountdown((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            // Auto-retry when countdown reaches 0
            onRetry();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [error.type, onRetry]);

  // Handle RATE_LIMIT with cooldown timer
  useEffect(() => {
    if (error.type === ChatErrorType.RATE_LIMIT) {
      // Extract cooldown seconds from error message if available
      // Default to 60 seconds
      setCooldownSeconds(60);
      
      const interval = setInterval(() => {
        setCooldownSeconds((prev) => {
          if (prev <= 1) {
            clearInterval(interval);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(interval);
    }
  }, [error.type]);

  // Get appropriate icon for error type
  const getIcon = () => {
    switch (error.type) {
      case ChatErrorType.QUOTA_EXCEEDED:
        return <Zap className="w-5 h-5" />;
      case ChatErrorType.AUTHENTICATION_FAILED:
        return <LogIn className="w-5 h-5" />;
      case ChatErrorType.RATE_LIMIT:
        return <Clock className="w-5 h-5" />;
      default:
        return <AlertCircle className="w-5 h-5" />;
    }
  };

  // Get appropriate button action
  const renderActionButton = () => {
    switch (error.action) {
      case 'retry':
        if (error.type === ChatErrorType.CONNECTION_FAILED && countdown > 0) {
          return (
            <button
              disabled
              className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-500 bg-gray-100 rounded-lg cursor-not-allowed"
            >
              <RotateCcw className="w-4 h-4" />
              Retrying in {countdown}s...
            </button>
          );
        }
        return (
          <button
            onClick={onRetry}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-purple-600 rounded-lg hover:bg-purple-700 transition-colors"
          >
            <RotateCcw className="w-4 h-4" />
            Try Again
          </button>
        );

      case 'upgrade':
        return (
          <button
            onClick={onUpgrade}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg hover:opacity-90 transition-opacity"
          >
            <Zap className="w-4 h-4" />
            Upgrade Now
          </button>
        );

      case 'login':
        return (
          <button
            onClick={onLogin}
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 transition-colors"
          >
            <LogIn className="w-4 h-4" />
            Log In
          </button>
        );

      case 'wait':
        return (
          <div className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg">
            <Clock className="w-4 h-4" />
            Please wait {cooldownSeconds}s
          </div>
        );

      default:
        return null;
    }
  };

  // Get error message with dynamic values
  const getMessage = () => {
    if (error.type === ChatErrorType.CONNECTION_FAILED && countdown > 0) {
      return getErrorMessage(ChatErrorType.CONNECTION_FAILED, { seconds: countdown });
    }
    if (error.type === ChatErrorType.RATE_LIMIT && cooldownSeconds > 0) {
      return getErrorMessage(ChatErrorType.RATE_LIMIT, { seconds: cooldownSeconds });
    }
    return error.message;
  };

  return (
    <div className="flex items-start gap-3 p-4 my-2 mx-4 bg-red-50 border border-red-200 rounded-lg animate-fade-in">
      {/* Icon */}
      <div className="flex-shrink-0 text-red-600">
        {getIcon()}
      </div>

      {/* Content */}
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-red-900 mb-1">
          Error
        </p>
        <p className="text-sm text-red-700">
          {getMessage()}
        </p>

        {/* Action Button */}
        {renderActionButton() && (
          <div className="mt-3">
            {renderActionButton()}
          </div>
        )}

        {/* Additional info for specific errors */}
        {error.type === ChatErrorType.QUOTA_EXCEEDED && (
          <p className="mt-2 text-xs text-red-600">
            Your daily quota will reset at midnight. Upgrade to Premium for unlimited access!
          </p>
        )}

        {error.type === ChatErrorType.TIMEOUT && (
          <p className="mt-2 text-xs text-red-600">
            Try asking a simpler question or break your request into smaller parts.
          </p>
        )}
      </div>

      {/* Timestamp */}
      <div className="flex-shrink-0 text-xs text-red-500">
        {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
      </div>
    </div>
  );
}
