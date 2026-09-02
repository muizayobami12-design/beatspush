import { apiClient } from './apiClient';

export interface Tip {
  id: string;
  from_user_id: string;
  from_user_name: string;
  to_user_id: string;
  to_user_name: string;
  amount: number;
  currency: string;
  message?: string;
  payment_status: string;
  created_at: string;
}

export interface TipRequest {
  to_user_id: string;
  amount: number;
  message?: string;
  content_type?: 'beat' | 'track' | 'mix' | 'profile';
  content_id?: string;
}

class TipService {
  private readonly baseUrl = '/tips';

  async sendTip(data: TipRequest): Promise<Tip> {
    const response = await apiClient.post(this.baseUrl, data);
    return response.data;
  }

  async getTipsReceived(params: {
    page?: number;
    page_size?: number;
  } = {}): Promise<{ tips: Tip[]; total: number; total_amount: number }> {
    const response = await apiClient.get(`${this.baseUrl}/received`, { params });
    return response.data;
  }

  async getTipsSent(params: {
    page?: number;
    page_size?: number;
  } = {}): Promise<{ tips: Tip[]; total: number; total_amount: number }> {
    const response = await apiClient.get(`${this.baseUrl}/sent`, { params });
    return response.data;
  }

  async getTipStats(): Promise<{
    total_received: number;
    total_sent: number;
    tips_received_count: number;
    tips_sent_count: number;
  }> {
    const response = await apiClient.get(`${this.baseUrl}/stats`);
    return response.data;
  }
}

export const tipService = new TipService();
