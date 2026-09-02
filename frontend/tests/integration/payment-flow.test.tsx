import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { usePayment } from '@/hooks/usePayment';
import * as paymentUtils from '@/lib/payment/paystack';

// Mock Paystack
const mockPaystackPop = {
  setup: vi.fn(() => ({
    openIframe: vi.fn(),
  })),
};

global.PaystackPop = mockPaystackPop as any;

vi.mock('@/lib/payment/paystack', () => ({
  initializePayment: vi.fn(),
  generateReference: vi.fn(() => 'TEST-REF-123'),
  validatePaymentData: vi.fn(() => true),
  formatAmount: vi.fn((amount) => amount * 100),
  convertToNaira: vi.fn((amount) => amount * 1500),
}));

vi.mock('@/services/beatService', () => ({
  purchaseBeat: vi.fn(),
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('Payment Flow Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock environment variable
    process.env.NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY = 'pk_test_mock';
  });

  it('should initialize payment with correct parameters', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(paymentUtils.initializePayment).toHaveBeenCalledWith(
        expect.objectContaining({
          amount: expect.any(Number),
          email: expect.any(String),
          reference: 'TEST-REF-123',
          metadata: expect.objectContaining({
            beatId: 'beat-123',
            beatTitle: 'Test Beat',
          }),
        })
      );
    });
  });

  it('should generate unique payment reference', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    vi.mocked(paymentUtils.generateReference).mockReturnValue('UNIQUE-REF-456');

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(paymentUtils.generateReference).toHaveBeenCalled();
    });
  });

  it('should convert USD to NGN for Paystack', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(paymentUtils.convertToNaira).toHaveBeenCalledWith(29.99);
    });
  });

  it('should format amount to kobo (smallest currency unit)', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'NGN' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      // Amount should be multiplied by 100 for kobo
      expect(paymentUtils.formatAmount).toHaveBeenCalledWith(29.99);
    });
  });

  it('should validate payment data before processing', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(paymentUtils.validatePaymentData).toHaveBeenCalled();
    });
  });

  it('should handle payment success callback', async () => {
    const onSuccess = vi.fn();
    
    const { result } = renderHook(() => usePayment({ onSuccess }), {
      wrapper: createWrapper(),
    });

    vi.mocked(paymentUtils.initializePayment).mockImplementation(
      ({ onSuccess: cb }) => {
        // Simulate successful payment
        cb?.({ reference: 'TEST-REF-123', status: 'success' });
        return Promise.resolve();
      }
    );

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalledWith(
        expect.objectContaining({
          reference: 'TEST-REF-123',
          status: 'success',
        })
      );
    });
  });

  it('should handle payment failure callback', async () => {
    const onError = vi.fn();
    
    const { result } = renderHook(() => usePayment({ onError }), {
      wrapper: createWrapper(),
    });

    vi.mocked(paymentUtils.initializePayment).mockImplementation(
      ({ onError: cb }) => {
        // Simulate payment failure
        cb?.(new Error('Payment failed'));
        return Promise.resolve();
      }
    );

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(onError).toHaveBeenCalledWith(expect.any(Error));
    });
  });

  it('should handle user closing payment modal', async () => {
    const onClose = vi.fn();
    
    const { result } = renderHook(() => usePayment({ onClose }), {
      wrapper: createWrapper(),
    });

    vi.mocked(paymentUtils.initializePayment).mockImplementation(
      ({ onClose: cb }) => {
        // Simulate user closing modal
        cb?.();
        return Promise.resolve();
      }
    );

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(onClose).toHaveBeenCalled();
    });
  });

  it('should show loading state during payment', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    expect(result.current.isProcessing).toBe(false);

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    result.current.handlePayment(paymentData);

    // Should show loading immediately
    expect(result.current.isProcessing).toBe(true);

    await waitFor(() => {
      expect(result.current.isProcessing).toBe(false);
    });
  });

  it('should prevent duplicate payment submissions', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    vi.mocked(paymentUtils.initializePayment).mockImplementation(
      () => new Promise((resolve) => setTimeout(resolve, 1000))
    );

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    // Trigger payment twice quickly
    result.current.handlePayment(paymentData);
    result.current.handlePayment(paymentData);

    await waitFor(() => {
      // initializePayment should only be called once
      expect(paymentUtils.initializePayment).toHaveBeenCalledTimes(1);
    });
  });

  it('should include user email in payment data', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    // Mock user email from auth store
    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(paymentUtils.initializePayment).toHaveBeenCalledWith(
        expect.objectContaining({
          email: expect.any(String),
        })
      );
    });
  });

  it('should handle missing Paystack public key', async () => {
    delete process.env.NEXT_PUBLIC_PAYSTACK_PUBLIC_KEY;

    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await expect(result.current.handlePayment(paymentData)).rejects.toThrow();
  });

  it('should include metadata for transaction tracking', async () => {
    const { result } = renderHook(() => usePayment(), {
      wrapper: createWrapper(),
    });

    const paymentData = {
      beatId: 'beat-123',
      beatTitle: 'Test Beat',
      amount: 29.99,
      currency: 'USD' as const,
    };

    await result.current.handlePayment(paymentData);

    await waitFor(() => {
      expect(paymentUtils.initializePayment).toHaveBeenCalledWith(
        expect.objectContaining({
          metadata: expect.objectContaining({
            beatId: 'beat-123',
            beatTitle: 'Test Beat',
            custom_fields: expect.any(Array),
          }),
        })
      );
    });
  });
});
