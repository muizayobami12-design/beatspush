'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

interface AuthGuardProps {
  children: React.ReactNode;
  requiredRole?: 'artist' | 'dj' | 'producer' | 'fan' | 'admin';
  redirectTo?: string;
}

export function AuthGuard({ 
  children, 
  requiredRole,
  redirectTo = '/login' 
}: AuthGuardProps) {
  const router = useRouter();
  const { user, isAuthenticated } = useAuthStore();

  useEffect(() => {
    // Check if user is authenticated
    if (!isAuthenticated || !user) {
      router.push(redirectTo);
      return;
    }

    // Check if user has required role
    if (requiredRole && user.role !== requiredRole) {
      // Redirect to home if user doesn't have required role
      router.push('/dashboard');
      return;
    }
  }, [isAuthenticated, user, requiredRole, redirectTo, router]);

  // Don't render children if not authenticated or doesn't have required role
  if (!isAuthenticated || !user) {
    return null;
  }

  if (requiredRole && user.role !== requiredRole) {
    return null;
  }

  return <>{children}</>;
}

// Convenience wrapper for admin-only routes
export function AdminGuard({ children }: { children: React.ReactNode }) {
  return <AuthGuard requiredRole="admin">{children}</AuthGuard>;
}
