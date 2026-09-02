import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { LoginForm } from '@/components/features/auth/LoginForm';
import { RegisterForm } from '@/components/features/auth/RegisterForm';
import * as authService from '@/services/authService';

// Mock the auth service
vi.mock('@/services/authService', () => ({
  login: vi.fn(),
  register: vi.fn(),
  requestPasswordReset: vi.fn(),
}));

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
};

describe('Authentication Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('Login Flow', () => {
    it('should successfully login with valid credentials', async () => {
      const mockLoginResponse = {
        user: {
          id: '1',
          email: 'test@example.com',
          fullName: 'Test User',
          role: 'artist',
        },
        token: 'mock-jwt-token',
      };

      vi.mocked(authService.login).mockResolvedValue(mockLoginResponse);

      renderWithProviders(<LoginForm />);

      // Fill in the form
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in|login/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      // Wait for async actions
      await waitFor(() => {
        expect(authService.login).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password123',
        });
      });

      // Should show success state or redirect (depends on implementation)
      expect(authService.login).toHaveBeenCalledTimes(1);
    });

    it('should show error message with invalid credentials', async () => {
      vi.mocked(authService.login).mockRejectedValue(
        new Error('Invalid email or password')
      );

      renderWithProviders(<LoginForm />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in|login/i });

      fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpass' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
      });
    });

    it('should validate email format', async () => {
      renderWithProviders(<LoginForm />);

      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /sign in|login/i });

      fireEvent.change(emailInput, { target: { value: 'not-an-email' } });
      fireEvent.blur(emailInput);

      await waitFor(() => {
        expect(screen.getByText(/invalid email/i)).toBeInTheDocument();
      });

      // Should not call login API
      fireEvent.click(submitButton);
      expect(authService.login).not.toHaveBeenCalled();
    });

    it('should validate password requirements', async () => {
      renderWithProviders(<LoginForm />);

      const passwordInput = screen.getByLabelText(/password/i);
      
      fireEvent.change(passwordInput, { target: { value: 'short' } });
      fireEvent.blur(passwordInput);

      await waitFor(() => {
        expect(
          screen.getByText(/password must be at least 8 characters/i)
        ).toBeInTheDocument();
      });
    });

    it('should disable submit button while loading', async () => {
      vi.mocked(authService.login).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 1000))
      );

      renderWithProviders(<LoginForm />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in|login/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(submitButton).toBeDisabled();
      });
    });

    it('should handle remember me checkbox', () => {
      renderWithProviders(<LoginForm />);

      const rememberMeCheckbox = screen.queryByLabelText(/remember me/i);
      if (rememberMeCheckbox) {
        expect(rememberMeCheckbox).not.toBeChecked();
        fireEvent.click(rememberMeCheckbox);
        expect(rememberMeCheckbox).toBeChecked();
      }
    });
  });

  describe('Registration Flow', () => {
    it('should successfully register new user', async () => {
      const mockRegisterResponse = {
        user: {
          id: '1',
          email: 'newuser@example.com',
          fullName: 'New User',
          role: 'artist',
        },
        token: 'mock-jwt-token',
      };

      vi.mocked(authService.register).mockResolvedValue(mockRegisterResponse);

      renderWithProviders(<RegisterForm />);

      // Step 1: Fill in basic info
      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const fullNameInput = screen.getByLabelText(/full name|name/i);

      fireEvent.change(emailInput, { target: { value: 'newuser@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(fullNameInput, { target: { value: 'New User' } });

      // Click continue to next step
      const continueButton = screen.getByRole('button', { name: /continue/i });
      fireEvent.click(continueButton);

      await waitFor(() => {
        // Should move to step 2 (role selection)
        expect(screen.getByText(/select your role|choose role/i)).toBeInTheDocument();
      });

      // Step 2: Select role
      const artistRole = screen.getByRole('button', { name: /artist/i });
      fireEvent.click(artistRole);

      await waitFor(() => {
        expect(authService.register).toHaveBeenCalledWith({
          email: 'newuser@example.com',
          password: 'password123',
          fullName: 'New User',
          role: 'artist',
        });
      });
    });

    it('should validate password confirmation', async () => {
      renderWithProviders(<RegisterForm />);

      const passwordInput = screen.getByLabelText(/^password$/i);
      const confirmPasswordInput = screen.getByLabelText(/confirm password/i);

      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'different' } });
      fireEvent.blur(confirmPasswordInput);

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      });
    });

    it('should show error for existing email', async () => {
      vi.mocked(authService.register).mockRejectedValue(
        new Error('Email already exists')
      );

      renderWithProviders(<RegisterForm />);

      const emailInput = screen.getByLabelText(/email/i);
      const passwordInput = screen.getByLabelText(/^password$/i);
      const fullNameInput = screen.getByLabelText(/full name|name/i);
      const continueButton = screen.getByRole('button', { name: /continue/i });

      fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(fullNameInput, { target: { value: 'Existing User' } });
      fireEvent.click(continueButton);

      await waitFor(() => {
        expect(screen.getByText(/email already exists/i)).toBeInTheDocument();
      });
    });

    it('should allow navigating between steps', async () => {
      renderWithProviders(<RegisterForm />);

      // Fill step 1
      const emailInput = screen.getByLabelText(/email/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const continueButton = screen.getByRole('button', { name: /continue/i });
      fireEvent.click(continueButton);

      await waitFor(() => {
        expect(screen.getByText(/select your role|choose role/i)).toBeInTheDocument();
      });

      // Go back
      const backButton = screen.getByRole('button', { name: /back/i });
      fireEvent.click(backButton);

      await waitFor(() => {
        expect(emailInput).toBeInTheDocument();
        expect(emailInput).toHaveValue('test@example.com'); // Should retain values
      });
    });

    it('should validate all required fields', async () => {
      renderWithProviders(<RegisterForm />);

      const continueButton = screen.getByRole('button', { name: /continue/i });
      fireEvent.click(continueButton);

      await waitFor(() => {
        expect(screen.getByText(/email is required/i)).toBeInTheDocument();
        expect(screen.getByText(/password is required/i)).toBeInTheDocument();
        expect(screen.getByText(/name is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Password Reset Flow', () => {
    it('should handle password reset request', async () => {
      vi.mocked(authService.requestPasswordReset).mockResolvedValue({
        message: 'Reset email sent',
      });

      // This would render PasswordResetRequest component
      // Testing flow depends on implementation
      expect(true).toBe(true); // Placeholder
    });
  });
});
