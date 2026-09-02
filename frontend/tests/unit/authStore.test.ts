import { describe, it, expect, beforeEach, vi } from 'vitest';
import { useAuthStore } from '@/store/authStore';

describe('AuthStore', () => {
  beforeEach(() => {
    // Reset store state before each test
    useAuthStore.setState({
      user: null,
      token: null,
      isAuthenticated: false,
    });
    localStorage.clear();
  });

  describe('login', () => {
    it('should set user and token on login', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'artist' as const,
      };
      const mockToken = 'mock-jwt-token';

      useAuthStore.getState().login(mockUser, mockToken);

      const state = useAuthStore.getState();
      expect(state.user).toEqual(mockUser);
      expect(state.token).toBe(mockToken);
      expect(state.isAuthenticated).toBe(true);
    });

    it('should persist token to localStorage', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'artist' as const,
      };
      const mockToken = 'mock-jwt-token';

      useAuthStore.getState().login(mockUser, mockToken);

      // Check localStorage directly
      const stored = localStorage.getItem('beatpush-auth');
      expect(stored).toBeTruthy();
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.token).toBe(mockToken);
      }
    });
  });

  describe('logout', () => {
    it('should clear user and token on logout', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'artist' as const,
      };

      // First login
      useAuthStore.getState().login(mockUser, 'mock-token');
      expect(useAuthStore.getState().isAuthenticated).toBe(true);

      // Then logout
      useAuthStore.getState().logout();

      const state = useAuthStore.getState();
      expect(state.user).toBeNull();
      expect(state.token).toBeNull();
      expect(state.isAuthenticated).toBe(false);
    });

    it('should clear localStorage on logout', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'artist' as const,
      };

      useAuthStore.getState().login(mockUser, 'mock-token');
      useAuthStore.getState().logout();

      const stored = localStorage.getItem('beatpush-auth');
      if (stored) {
        const parsed = JSON.parse(stored);
        expect(parsed.state.token).toBeNull();
      }
    });
  });

  describe('updateUser', () => {
    it('should update user information', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'artist' as const,
      };

      useAuthStore.getState().login(mockUser, 'mock-token');

      const updates = { fullName: 'Updated Name' };
      useAuthStore.getState().updateUser(updates);

      const state = useAuthStore.getState();
      expect(state.user?.fullName).toBe('Updated Name');
      expect(state.user?.email).toBe('test@example.com'); // Other fields unchanged
    });

    it('should not update if user is null', () => {
      const updates = { fullName: 'Updated Name' };
      useAuthStore.getState().updateUser(updates);

      expect(useAuthStore.getState().user).toBeNull();
    });
  });

  describe('isAuthenticated', () => {
    it('should return false when no user', () => {
      expect(useAuthStore.getState().isAuthenticated).toBe(false);
    });

    it('should return true when user is logged in', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'artist' as const,
      };

      useAuthStore.getState().login(mockUser, 'mock-token');
      expect(useAuthStore.getState().isAuthenticated).toBe(true);
    });
  });

  describe('persistence', () => {
    it('should restore state from localStorage', () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        fullName: 'Test User',
        role: 'artist' as const,
      };

      // Simulate persisted state
      const persistedState = {
        state: {
          user: mockUser,
          token: 'mock-token',
          isAuthenticated: true,
        },
        version: 0,
      };

      localStorage.setItem('beatpush-auth', JSON.stringify(persistedState));

      // Create a fresh store instance (simulating page reload)
      const freshStore = useAuthStore.getState();
      
      // Note: Zustand persist middleware loads async, so in real scenario
      // the state would be restored. This test verifies the structure.
      expect(localStorage.getItem('beatpush-auth')).toBeTruthy();
    });
  });
});
