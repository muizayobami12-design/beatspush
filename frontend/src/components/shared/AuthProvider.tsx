'use client';

import { useEffect, ReactNode } from 'react';
import { useAuthStore } from '@/store/authStore';
import { STORAGE_KEYS } from '@/lib/constants';

interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Auth Provider Component
 * Handles authentication state hydration from localStorage
 * Must wrap the app to ensure auth state is properly initialized
 */
export function AuthProvider({ children }: AuthProviderProps) {
  const setUser = useAuthStore((state) => state.setUser);
  const setToken = useAuthStore((state) => state.setToken);
  const login = useAuthStore((state) => state.login);

  useEffect(() => {
    // Hydrate auth state from localStorage on client mount
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
      const userJson = localStorage.getItem(STORAGE_KEYS.USER);
      
      if (token && userJson) {
        try {
          const storedState = JSON.parse(userJson);
          if (storedState.user && storedState.token) {
            // Restore auth state
            login(storedState.user, storedState.token);
            console.log('[AuthProvider] Auth state restored from localStorage');
          }
        } catch (error) {
          console.error('[AuthProvider] Failed to parse stored auth state:', error);
          // Clear invalid data
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.USER);
        }
      }
    }
  }, [login, setUser, setToken]);

  return <>{children}</>;
}
