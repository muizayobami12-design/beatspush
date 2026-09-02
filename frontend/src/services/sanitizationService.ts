import DOMPurify from 'isomorphic-dompurify';

/**
 * Sanitize AI-generated text (strict - no HTML allowed)
 * Use for: titles, names, short text fields
 */
export function sanitizeText(text: string): string {
  return DOMPurify.sanitize(text, {
    ALLOWED_TAGS: [], // No HTML tags
    ALLOWED_ATTR: [], // No attributes
    KEEP_CONTENT: true, // Keep text content
  });
}

/**
 * Sanitize AI-generated description (basic formatting allowed)
 * Use for: descriptions, bio, longer text with formatting
 */
export function sanitizeDescription(text: string): string {
  return DOMPurify.sanitize(text, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'br', 'p'], // Basic formatting
    ALLOWED_ATTR: [], // No attributes (no onclick, onerror, etc.)
    KEEP_CONTENT: true,
  });
}

/**
 * Sanitize HTML content (for rich text editors)
 * Use for: blog posts, press releases
 */
export function sanitizeHTML(html: string): string {
  return DOMPurify.sanitize(html, {
    ALLOWED_TAGS: [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'br', 'strong', 'em', 'b', 'i', 'u',
      'ul', 'ol', 'li',
      'a', 'blockquote', 'code', 'pre'
    ],
    ALLOWED_ATTR: {
      'a': ['href', 'title', 'target'], // Links only
    },
    ALLOWED_URI_REGEXP: /^(?:(?:(?:f|ht)tps?|mailto|tel|callto|sms|cid|xmpp):|[^a-z]|[a-z+.\-]+(?:[^a-z+.\-:]|$))/i,
  });
}

/**
 * Check if sanitization changed the content
 * Returns true if potential malicious content was removed
 */
export function wasSanitized(original: string, sanitized: string): boolean {
  return original.trim() !== sanitized.trim();
}

/**
 * Log suspicious sanitization (potential attack attempt)
 */
export async function logSuspiciousSanitization(
  original: string,
  sanitized: string,
  context: string
) {
  if (!wasSanitized(original, sanitized)) return;
  
  // Log to backend for security monitoring
  try {
    await fetch('/api/v1/security/suspicious-content', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        original,
        sanitized,
        context,
        timestamp: new Date().toISOString(),
      }),
    });
  } catch (error) {
    console.error('Failed to log suspicious sanitization:', error);
  }
}

/**
 * Sanitize AI service responses
 * Use this wrapper for all AI-generated content
 */
export class SecureAIService {
  /**
   * Sanitize AI title generation
   */
  static sanitizeTitle(title: string, logContext?: string): string {
    const sanitized = sanitizeText(title);
    
    if (wasSanitized(title, sanitized) && logContext) {
      logSuspiciousSanitization(title, sanitized, logContext);
    }
    
    return sanitized;
  }

  /**
   * Sanitize AI description generation
   */
  static sanitizeDescription(description: string, logContext?: string): string {
    const sanitized = sanitizeDescription(description);
    
    if (wasSanitized(description, sanitized) && logContext) {
      logSuspiciousSanitization(description, sanitized, logContext);
    }
    
    return sanitized;
  }

  /**
   * Sanitize array of AI-generated items
   */
  static sanitizeArray(items: string[], logContext?: string): string[] {
    return items.map(item => this.sanitizeTitle(item, logContext));
  }
}
