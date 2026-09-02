import { apiClient } from './apiClient';

export interface InitiatePaymentData {
  beatId: string;
  amount: number;
  email: string;
}

export interface PaymentResponse {
  authorization_url: string;
  access_code: string;
  reference: string;
}

export interface VerifyPaymentResponse {
  status: 'success' | 'failed' | 'pending';
  reference: string;
  amount: number;
  currency: string;
  paid_at?: string;
  channel: string;
  transaction: {
    id: string;
    status: string;
    reference: string;
    amount: number;
  };
}

export interface Transaction {
  id: string;
  reference: string;
  amount: number;
  currency: string;
  status: 'pending' | 'success' | 'failed';
  beatId: string;
  beatTitle: string;
  createdAt: string;
  paidAt?: string;
}

class PaymentService {
  /**
   * Initialize Paystack payment for a beat purchase
   */
  async initiateBeatPurchase(beatId: string, licenseType: 'lease' | 'exclusive'): Promise<PaymentResponse> {
    const response = await apiClient.post<PaymentResponse>(
      `/payments/beats/${beatId}/initiate`,
      { license_type: licenseType }
    );
    return response.data;
  }

  /**
   * Verify payment after Paystack redirect
   */
  async verifyPayment(reference: string): Promise<VerifyPaymentResponse> {
    const response = await apiClient.get<VerifyPaymentResponse>(
      `/payments/verify/${reference}`
    );
    return response.data;
  }

  /**
   * Get user's transaction history
   */
  async getTransactions(page = 1, limit = 20): Promise<{
    transactions: Transaction[];
    total: number;
    page: number;
    pages: number;
  }> {
    const response = await apiClient.get('/payments/transactions', {
      params: { page, limit },
    });
    return response.data;
  }

  /**
   * Get transaction by ID
   */
  async getTransaction(id: string): Promise<Transaction> {
    const response = await apiClient.get<{ transaction: Transaction }>(
      `/payments/transactions/${id}`
    );
    return response.data.transaction;
  }

  /**
   * Get purchased beats
   */
  async getPurchasedBeats(page = 1, limit = 20): Promise<{
    beats: any[];
    total: number;
    page: number;
    pages: number;
  }> {
    const response = await apiClient.get('/beats/purchases/my', {
      params: { page, limit },
    });
    return response.data;
  }

  /**
   * Download purchased beat
   */
  async downloadBeat(purchaseId: string): Promise<{ download_url: string }> {
    const response = await apiClient.get(`/beats/purchases/${purchaseId}/download`);
    return response.data;
  }

  /**
   * Get payment statistics for seller
   */
  async getPaymentStats(): Promise<{
    totalRevenue: number;
    totalSales: number;
    pendingPayouts: number;
    monthlyRevenue: { month: string; revenue: number }[];
  }> {
    const response = await apiClient.get('/payments/stats');
    return response.data;
  }
}

export const paymentService = new PaymentService();
