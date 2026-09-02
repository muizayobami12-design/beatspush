'use client';

import { Turnstile as ReactTurnstile } from 'react-turnstile';
import { useEffect } from 'react';

interface TurnstileProps {
  onSuccess: (token: string) => void;
  onError?: () => void;
  onExpire?: () => void;
}

export function Turnstile({ onSuccess, onError, onExpire }: TurnstileProps) {
  const siteKey = process.env.NEXT_PUBLIC_TURNSTILE_SITE_KEY;

  // In development, auto-pass after a short delay
  useEffect(() => {
    if (process.env.NEXT_PUBLIC_ENV === 'development' && !siteKey) {
      const timer = setTimeout(() => {
        // Auto-generate a mock token for development
        onSuccess('dev-mock-token-' + Date.now());
      }, 500);
      return () => clearTimeout(timer);
    }
  }, [siteKey, onSuccess]);

  if (!siteKey) {
    console.warn('Turnstile site key not configured - using development mode auto-pass');
    return (
      <div className="text-xs text-yellow-500 p-2 bg-yellow-500/10 rounded border border-yellow-500/20">
        Development Mode: Security check auto-passed
      </div>
    );
  }

  return (
    <ReactTurnstile
      sitekey={siteKey}
      onVerify={onSuccess}
      onError={onError}
      onExpire={onExpire}
      theme="dark"
      size="normal"
    />
  );
}
