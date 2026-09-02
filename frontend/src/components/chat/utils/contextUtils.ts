/**
 * Context utilities for extracting page-specific context
 */

import type { PageContext, PageType } from '../types';
import { CONTEXT_EXTRACTORS } from '../constants';

/**
 * Extract page context from current location and props
 */
export function extractPageContext(
  pageType: PageType,
  props?: Record<string, any>
): PageContext {
  const contextDef = CONTEXT_EXTRACTORS[pageType];
  
  if (!contextDef) {
    return {
      pageType: 'general',
      pageUrl: typeof window !== 'undefined' ? window.location.pathname : '',
      contextData: {},
    };
  }

  return {
    pageType: contextDef.pageType,
    pageUrl: typeof window !== 'undefined' ? window.location.pathname : '',
    contextData: contextDef.extractContext(props || {}),
  };
}

/**
 * Detect page type from URL pathname
 */
export function detectPageType(pathname: string): PageType {
  if (pathname.includes('/beats/upload')) return 'beat_upload';
  if (pathname.includes('/beats/') && pathname.includes('/edit')) return 'beat_edit';
  if (pathname.includes('/campaigns/')) return 'campaign_dashboard';
  if (pathname.includes('/analytics')) return 'analytics';
  if (pathname.includes('/profile')) return 'profile_edit';
  if (pathname.includes('/feed') || pathname.includes('/social')) return 'social_feed';
  if (pathname.includes('/messages')) return 'messaging';
  
  return 'general';
}

/**
 * Get context display string
 */
export function getContextDisplay(pageType: PageType): string {
  const contextDef = CONTEXT_EXTRACTORS[pageType];
  return contextDef?.contextDisplay || 'AI Assistant';
}

/**
 * Check if required context fields are present
 */
export function hasRequiredContext(
  contextData: Record<string, any>,
  requiredFields: string[]
): boolean {
  return requiredFields.every((field) => {
    const value = contextData[field];
    return value !== undefined && value !== null && value !== '';
  });
}

/**
 * Sanitize context data (remove sensitive information)
 */
export function sanitizeContextData(
  contextData: Record<string, any>
): Record<string, any> {
  const sensitiveKeys = [
    'password',
    'token',
    'secret',
    'apiKey',
    'creditCard',
    'ssn',
    'email', // Be cautious with email
  ];

  const sanitized: Record<string, any> = {};

  for (const [key, value] of Object.entries(contextData)) {
    // Skip sensitive keys
    const lowerKey = key.toLowerCase();
    if (sensitiveKeys.some((sensitive) => lowerKey.includes(sensitive))) {
      continue;
    }

    // Recursively sanitize nested objects
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      sanitized[key] = sanitizeContextData(value);
    } else {
      sanitized[key] = value;
    }
  }

  return sanitized;
}

/**
 * Format context data for prompt injection
 */
export function formatContextForPrompt(context: PageContext): string {
  const { pageType, contextData } = context;
  
  if (Object.keys(contextData).length === 0) {
    return '';
  }

  const lines: string[] = [`Page: ${pageType}`];

  for (const [key, value] of Object.entries(contextData)) {
    if (value === undefined || value === null) continue;

    if (typeof value === 'object') {
      lines.push(`${key}: ${JSON.stringify(value)}`);
    } else {
      lines.push(`${key}: ${value}`);
    }
  }

  return lines.join('\n');
}

/**
 * Merge multiple context objects
 */
export function mergeContexts(...contexts: PageContext[]): PageContext {
  if (contexts.length === 0) {
    return {
      pageType: 'general',
      pageUrl: '',
      contextData: {},
    };
  }

  const merged: PageContext = {
    pageType: contexts[0].pageType,
    pageUrl: contexts[0].pageUrl,
    contextData: {},
  };

  for (const context of contexts) {
    merged.contextData = {
      ...merged.contextData,
      ...context.contextData,
    };
  }

  return merged;
}
