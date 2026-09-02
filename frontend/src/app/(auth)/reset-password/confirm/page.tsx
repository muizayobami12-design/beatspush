'use client';

import { useSearchParams } from 'next/navigation';
import { Suspense } from 'react';
import { PasswordResetConfirm } from '@/components/features/auth/PasswordResetConfirm';

function ResetPasswordConfirmContent() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md text-center space-y-4">
          <h1 className="text-2xl font-bold text-destructive">Invalid Reset Link</h1>
          <p className="text-muted-foreground">
            This password reset link is invalid or has expired.
          </p>
          <a
            href="/reset-password"
            className="inline-block text-primary hover:underline"
          >
            Request a new reset link
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-gradient-to-br from-background via-background to-primary/5">
      <PasswordResetConfirm token={token} />
    </div>
  );
}

export default function ResetPasswordConfirmPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse">Loading...</div>
      </div>
    }>
      <ResetPasswordConfirmContent />
    </Suspense>
  );
}
