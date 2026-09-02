/**
 * Email Validation Service
 * Detects disposable/temporary email addresses
 */

// Common disposable email domains (top 100+)
const DISPOSABLE_DOMAINS = new Set([
  // Temporary email services
  'tempmail.com', 'temp-mail.org', 'temp-mail.io', 'temp-mail.io',
  '10minutemail.com', '10minutemail.net', '10minutemail.org',
  'guerrillamail.com', 'guerrillamail.net', 'guerrillamailblock.com',
  'mailinator.com', 'mailinator2.com', 'mailinator.net',
  'throwaway.email', 'throwawaymail.com',
  'getnada.com', 'getairmail.com',
  'sharklasers.com', 'guerrillamail.biz',
  'spam4.me', 'grr.la', 'maildrop.cc',
  'yopmail.com', 'yopmail.fr', 'yopmail.net',
  'trashmail.com', 'trashmail.net',
  'mohmal.com', 'mohmal.in', 'mohmal.tech',
  'emailondeck.com', 'mintemail.com',
  'mytrashmail.com', 'fakeinbox.com',
  'spamgourmet.com', 'mailnesia.com',
  'dispostable.com', 'disposeamail.com',
  'armyspy.com', 'cuvox.de', 'dayrep.com',
  'einrot.com', 'fleckens.hu', 'gustr.com',
  'jourrapide.com', 'rhyta.com', 'superrito.com',
  'teleworm.us', 'dropmail.me',
  'emailtemporar.ro', 'fakemail.net',
  
  // Recently added disposable services
  'mail.tm', 'internxt.com', 'mailto.plus',
  'protonmail.com', // Often used for spam (be careful with this one)
]);

/**
 * Check if email domain is disposable
 */
export function isDisposableEmail(email: string): boolean {
  try {
    const domain = email.toLowerCase().split('@')[1];
    if (!domain) return false;
    
    return DISPOSABLE_DOMAINS.has(domain);
  } catch (error) {
    console.error('Error checking disposable email:', error);
    return false;
  }
}

/**
 * Validate email format (RFC 5322 compliant)
 */
export function isValidEmailFormat(email: string): boolean {
  const emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/;
  return emailRegex.test(email);
}

/**
 * Check if email looks suspicious
 * Returns: { valid: boolean, reason?: string }
 */
export function validateEmail(email: string): { valid: boolean; reason?: string } {
  // Check format
  if (!isValidEmailFormat(email)) {
    return { valid: false, reason: 'Invalid email format' };
  }
  
  // Check for disposable email
  if (isDisposableEmail(email)) {
    return { valid: false, reason: 'Please use a permanent email address' };
  }
  
  // Check for suspicious patterns (but allow test emails in development)
  const isDevelopment = process.env.NODE_ENV === 'development' || 
                        process.env.NEXT_PUBLIC_ENV === 'development';
  
  if (!isDevelopment) {
    const suspiciousPatterns = [
      /test\d+@/i,           // test123@...
      /temp\d+@/i,           // temp456@...
      /fake\d+@/i,           // fake789@...
      /^\d+@/,               // Numbers only before @
      /[+]{2,}/,             // Multiple + signs
      /\.{2,}/,              // Multiple dots in a row
    ];
    
    for (const pattern of suspiciousPatterns) {
      if (pattern.test(email)) {
        return { valid: false, reason: 'Email appears suspicious' };
      }
    }
  }
  
  return { valid: true };
}

/**
 * Extract domain from email
 */
export function getEmailDomain(email: string): string | null {
  try {
    return email.toLowerCase().split('@')[1] || null;
  } catch {
    return null;
  }
}

/**
 * Check if email is from a known provider (Gmail, Yahoo, etc.)
 * These are generally trusted
 */
export function isKnownProvider(email: string): boolean {
  const domain = getEmailDomain(email);
  if (!domain) return false;
  
  const knownProviders = [
    'gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com',
    'icloud.com', 'aol.com', 'mail.com', 'zoho.com',
    'yandex.com', 'protonmail.ch', // ProtonMail's real domain
  ];
  
  return knownProviders.includes(domain);
}

/**
 * Comprehensive email validation for registration
 */
export async function validateRegistrationEmail(email: string): Promise<{
  valid: boolean;
  reason?: string;
  suggestions?: string[];
}> {
  // Basic validation
  const basicCheck = validateEmail(email);
  if (!basicCheck.valid) {
    return basicCheck;
  }
  
  // Check if from known provider
  if (isKnownProvider(email)) {
    return { valid: true };
  }
  
  // Domain-specific checks
  const domain = getEmailDomain(email);
  if (!domain) {
    return { valid: false, reason: 'Invalid email domain' };
  }
  
  // Check for common typos in popular domains
  const suggestions: string[] = [];
  const typoMap: Record<string, string> = {
    'gmial.com': 'gmail.com',
    'gmai.com': 'gmail.com',
    'yahooo.com': 'yahoo.com',
    'yaho.com': 'yahoo.com',
    'outlok.com': 'outlook.com',
    'hotmial.com': 'hotmail.com',
  };
  
  if (typoMap[domain]) {
    suggestions.push(`Did you mean ${email.replace(domain, typoMap[domain])}?`);
  }
  
  return {
    valid: true,
    suggestions: suggestions.length > 0 ? suggestions : undefined,
  };
}
