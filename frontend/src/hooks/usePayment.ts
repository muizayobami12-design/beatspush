import { useState, useCallback } from 'react';
import { paymentService, VerifyPaymentResponse, Transaction } from '@/services/paymentService';

export interface UsePaymentOptions {
  /** Callback on successful payment */
  onSuccess?: (reference: string, transactionId: string) => void;
  /** Callback on payment error */
  onError?: (error: Error) => void;
}

export interface UsePaymentReturn {
  /** Is payment processing */
  isProcessing: boolean;
  /** Payment status */
  status: 'idle' | 'processing' | 'success' | 'error';
  /** Error message if any */
  error: string | null;
  /** Initiate beat purchase */
  initiateBeatPurchase: (beatId: string, licenseType: 'lease' | 'exclusive') => Promise<any>;
  /** Verify payment after Paystack redirect */
  verifyPayment: (reference: string) => Promise<VerifyPaymentResponse>;
  /** Get transaction history */
  getTransactions: (page?: number, limit?: number) => Promise<any>;
  /** Get purchased beats */
  getPurchasedBeats: (page?: number, limit?: number) => Promise<any>;
  /** Download beat */
  downloadBeat: (purchaseId: string) => Promise<{ download_url: string }>;
  /** Reset state */
  reset: () => void;
}

/**
 * Hook for managing Paystack payments
 * Handles payment initiation, verification, and transaction history
 */
export function usePayment({
  onSuccess,
  onError,
}: UsePaymentOptions = {}): UsePaymentReturn {
  const [isProcessing, setIsProcessing] = useState(false);
  const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [error, setError] = useState<string | null>(null);

  const handleInitiateBeatPurchase = useCallback(
    async (beatId: string, licenseType: 'lease' | 'exclusive' = 'lease') => {
      setIsProcessing(true);
      setStatus('processing');
      setError(null);

      try {
        const response = await paymentService.initiateBeatPurchase(beatId, licenseType);
        return response;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to initiate payment');
        setError(error.message);
        setStatus('error');

        if (onError) {
          onError(error);
        }

        throw error;
      } finally {
        setIsProcessing(false);
      }
    },
    [onError]
  );

  const handleVerifyPayment = useCallback(
    async (reference: string) => {
      setIsProcessing(true);
      setStatus('processing');
      setError(null);

      try {
        const response = await paymentService.verifyPayment(reference);

        if (response.status === 'success') {
          setStatus('success');

          if (onSuccess) {
            onSuccess(reference, response.transaction.id);
          }
        } else {
          throw new Error(`Payment ${response.status}`);
        }

        return response;
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Payment verification failed');
        setError(error.message);
        setStatus('error');

        if (onError) {
          onError(error);
        }

        throw error;
      } finally {
        setIsProcessing(false);
      }
    },
    [onSuccess, onError]
  );

  const handleGetTransactions = useCallback(async (page = 1, limit = 20) => {
    setIsProcessing(true);

    try {
      const response = await paymentService.getTransactions(page, limit);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch transactions');
      setError(error.message);

      if (onError) {
        onError(error);
      }

      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [onError]);

  const handleGetPurchasedBeats = useCallback(async (page = 1, limit = 20) => {
    setIsProcessing(true);

    try {
      const response = await paymentService.getPurchasedBeats(page, limit);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to fetch purchased beats');
      setError(error.message);

      if (onError) {
        onError(error);
      }

      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [onError]);

  const handleDownloadBeat = useCallback(async (purchaseId: string) => {
    setIsProcessing(true);

    try {
      const response = await paymentService.downloadBeat(purchaseId);
      return response;
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Failed to download beat');
      setError(error.message);

      if (onError) {
        onError(error);
      }

      throw error;
    } finally {
      setIsProcessing(false);
    }
  }, [onError]);

  const handleReset = useCallback(() => {
    setIsProcessing(false);
    setStatus('idle');
    setError(null);
  }, []);

  return {
    isProcessing,
    status,
    error,
    initiateBeatPurchase: handleInitiateBeatPurchase,
    verifyPayment: handleVerifyPayment,
    getTransactions: handleGetTransactions,
    getPurchasedBeats: handleGetPurchasedBeats,
    downloadBeat: handleDownloadBeat,
    reset: handleReset,
  };
}
