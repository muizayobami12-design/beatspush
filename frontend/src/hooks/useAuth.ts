import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuthStore } from '@/store/authStore';
import { authService, LoginCredentials, RegisterData } from '@/services/authService';
import { useRouter } from 'next/navigation';
import { QUERY_KEYS, ROUTES } from '@/lib/constants';

/**
 * Custom hook for authentication operations
 */
export function useAuth() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user, token, isAuthenticated, login: setAuth, logout: clearAuth } = useAuthStore();

  /**
   * Login mutation
   */
  const loginMutation = useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials.email, credentials.password),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token || data.token);
      queryClient.setQueryData([QUERY_KEYS.USER], data.user);
      router.push(ROUTES.DASHBOARD);
    },
  });

  /**
   * Register mutation
   */
  const registerMutation = useMutation({
    mutationFn: (data: RegisterData) => authService.register(data),
    onSuccess: (data) => {
      setAuth(data.user, data.access_token || data.token);
      queryClient.setQueryData([QUERY_KEYS.USER], data.user);
      router.push(ROUTES.DASHBOARD);
    },
  });

  /**
   * Logout mutation
   */
  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSuccess: () => {
      clearAuth();
      queryClient.clear();
      router.push(ROUTES.LOGIN);
    },
  });

  /**
   * Get current user query
   */
  const { data: currentUser, isLoading } = useQuery({
    queryKey: [QUERY_KEYS.USER],
    queryFn: authService.getCurrentUser,
    enabled: isAuthenticated && !!token,
    staleTime: Infinity,
  });

  return {
    user: currentUser || user,
    token,
    isAuthenticated,
    isLoading: isLoading || loginMutation.isPending || registerMutation.isPending,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: logoutMutation.mutate,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
}
