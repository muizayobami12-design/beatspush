'use client';

import { useEffect } from 'react';
import { useAuthStore } from '@/store/authStore';
import { useRouter } from 'next/navigation';

export default function ClearAuthPage() {
  const { logout } = useAuthStore();
  const router = useRouter();

  useEffect(() => {
    // Clear all auth data
    logout();
    
    // Clear all localStorage
    if (typeof window !== 'undefined') {
      localStorage.clear();
      
      // Clear all cookies
      document.cookie.split(";").forEach((c) => {
        document.cookie = c
          .replace(/^ +/, "")
          .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
      });
    }
    
    // Redirect to login after 2 seconds
    setTimeout(() => {
      router.push('/login');
    }, 2000);
  }, [logout, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
        <p className="text-lg font-semibold mb-2">Clearing authentication data...</p>
        <p className="text-muted-foreground">You will be redirected to login page</p>
      </div>
    </div>
  );
}
