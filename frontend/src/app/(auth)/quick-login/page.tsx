'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function QuickLoginPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleQuickLogin = async () => {
    setIsLoading(true);
    setMessage('Logging in...');

    try {
      // Call backend directly
      console.log('[QuickLogin] Making login request...');
      const response = await fetch('http://127.0.0.1:8000/api/v1/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'testuser@example.com',
          password: 'TestPassword123',
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      console.log('[QuickLogin] Response:', data);

      // Get the token - could be 'access_token' or 'token'
      const token = data.token || data.access_token;
      if (!token) {
        throw new Error('No token in response');
      }

      console.log('[QuickLogin] Token received:', token.substring(0, 20) + '...');

      // Store directly in localStorage
      if (typeof window !== 'undefined') {
        console.log('[QuickLogin] Storing token in localStorage...');
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('auth_token', token);

        // Set cookie - try multiple approaches
        const expiresDate = new Date();
        expiresDate.setTime(expiresDate.getTime() + 7 * 24 * 60 * 60 * 1000);
        const expires = expiresDate.toUTCString();

        // Method 1: Standard cookie
        document.cookie = `auth_token=${token}; expires=${expires}; path=/`;

        // Method 2: Also try setting it in a more specific way
        document.cookie = `auth_token=${token}; max-age=${7 * 24 * 60 * 60}; path=/; SameSite=Lax`;

        console.log('[QuickLogin] Cookies after setting:', document.cookie);
        console.log('[QuickLogin] localStorage:', localStorage.getItem('auth_token'));

        setMessage('✅ Token stored successfully! Redirecting...');

        // Wait a moment then redirect
        setTimeout(() => {
          console.log('[QuickLogin] Redirecting to /dashboard...');
          router.push('/dashboard');
        }, 500);
      }
    } catch (error: any) {
      console.error('[QuickLogin] Error:', error);
      setMessage(`❌ Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background to-primary/5">
      <div className="w-full max-w-md space-y-6">
        <div className="text-center space-y-2">
          <h1 className="text-3xl font-bold bg-gradient-to-r from-[#667eea] to-[#764ba2] bg-clip-text text-transparent">
            Quick Login Test
          </h1>
          <p className="text-muted-foreground">
            Direct backend authentication test
          </p>
        </div>

        <div className="bg-card p-6 rounded-xl border border-border space-y-4">
          <div>
            <p className="text-sm text-muted-foreground mb-2">Test Credentials:</p>
            <p className="text-sm font-mono">Email: testuser@example.com</p>
            <p className="text-sm font-mono">Password: TestPassword123</p>
          </div>

          {message && (
            <div
              className={`p-3 rounded-lg text-sm ${
                message.includes('✅')
                  ? 'bg-green-500/10 text-green-400'
                  : message.includes('❌')
                    ? 'bg-red-500/10 text-red-400'
                    : 'bg-blue-500/10 text-blue-400'
              }`}
            >
              {message}
            </div>
          )}

          <button
            onClick={handleQuickLogin}
            disabled={isLoading}
            className="w-full px-6 py-3 bg-gradient-to-r from-[#667eea] to-[#764ba2] hover:opacity-90 disabled:opacity-50 text-white font-bold rounded-xl transition-opacity"
          >
            {isLoading ? 'Logging in...' : 'Quick Login'}
          </button>

          <div className="bg-muted p-4 rounded-lg">
            <p className="text-xs text-muted-foreground mb-2">Debug Info:</p>
            <p className="text-xs font-mono text-foreground">
              localStorage auth_token: {localStorage.getItem('auth_token') ? '✓ SET' : '✗ NOT SET'}
            </p>
            <p className="text-xs font-mono text-foreground">
              localStorage user: {localStorage.getItem('user') ? '✓ SET' : '✗ NOT SET'}
            </p>
          </div>
        </div>

        <div className="text-center">
          <a href="/login" className="text-sm text-primary hover:underline">
            Back to normal login
          </a>
        </div>
      </div>
    </div>
  );
}
