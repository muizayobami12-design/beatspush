import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/types';
import { STORAGE_KEYS } from '@/lib/constants';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  login: (user: User, token: string) => void;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
  setLoading: (loading: boolean) => void;
  // For debugging
  _hydrated?: boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      _hydrated: false,

      setUser: (user) => {
        console.log('[authStore.setUser]', user?.email);
        set({ user, isAuthenticated: !!user, _hydrated: true });
      },

      setToken: (token) => {
        console.log('[authStore.setToken]', token ? 'SET' : 'CLEARED');
        set({ token, _hydrated: true });
      },

      login: (user, token) => {
        console.log('[authStore.login]', user.email, token.substring(0, 20) + '...');
        
        // Store token in localStorage
        if (typeof window !== 'undefined') {
          console.log('[authStore.login] Storing in localStorage...');
          localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, token);
          localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
          
          // Store token in cookie with proper options
          const expiresDate = new Date();
          expiresDate.setTime(expiresDate.getTime() + (7 * 24 * 60 * 60 * 1000)); // 7 days
          const expires = `expires=${expiresDate.toUTCString()}`;
          document.cookie = `auth_token=${token}; ${expires}; path=/; SameSite=Lax`;
          
          console.log('[authStore.login] localStorage and cookie set');
          console.log('[authStore.login] Cookies:', document.cookie);
        }
        
        set({ user, token, isAuthenticated: true, _hydrated: true });
        console.log('[authStore.login] State updated:', { isAuthenticated: true, user: user.email, token: token.substring(0, 20) + '...' });
      },

      logout: () => {
        console.log('[authStore.logout]');
        // Clear storage
        if (typeof window !== 'undefined') {
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
          
          // Clear cookie
          document.cookie = 'auth_token=; path=/; max-age=0';
        }
        set({ user: null, token: null, isAuthenticated: false, _hydrated: true });
      },

      updateUser: (updates) => {
        console.log('[authStore.updateUser]', updates);
        set((state) => ({
          user: state.user ? { ...state.user, ...updates } : null,
          _hydrated: true,
        }));
      },

      setLoading: (loading) => {
        set({ isLoading: loading, _hydrated: true });
      },
    }),
    {
      name: STORAGE_KEYS.USER,
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        console.log('[authStore] Hydration complete', {
          user: state?.user?.email,
          token: state?.token ? state.token.substring(0, 20) + '...' : 'MISSING',
          isAuthenticated: state?.isAuthenticated,
        });
      },
    }
  )
);
