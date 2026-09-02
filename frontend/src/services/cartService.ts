/**
 * Cart Service
 * Handles all cart and order-related API operations
 */

import { apiClient, getErrorMessage } from '@/lib/apiClient';
import { QUERY_KEYS, PAGINATION } from '@/lib/constants';

/**
 * Cart item data model
 */
export interface CartItem {
  id: string;
  cart_id: string;
  beat_id: string;
  beat_title: string;
  beat_artist: string;
  beat_cover_url?: string;
  license_type: string;
  price: number;
  quantity: number;
  added_at: string;
}

/**
 * Cart response
 */
export interface Cart {
  id: string;
  user_id: string;
  items: CartItem[];
  subtotal: number;
  tax: number;
  platform_fee: number;
  total: number;
  item_count: number;
  updated_at: string;
}

/**
 * Order item data model
 */
export interface OrderItem {
  id: string;
  order_id: string;
  beat_id: string;
  beat_title: string;
  license_type: string;
  price: number;
  download_url?: string;
  expires_at?: string;
}

/**
 * Order status enum
 */
export type OrderStatus = 'pending' | 'paid' | 'processing' | 'completed' | 'failed' | 'cancelled';

/**
 * Order data model
 */
export interface Order {
  id: string;
  user_id: string;
  order_number: string;
  items: OrderItem[];
  subtotal: number;
  tax: number;
  platform_fee: number;
  total: number;
  status: OrderStatus;
  payment_method?: string;
  transaction_id?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Orders list response
 */
export interface OrdersResponse {
  orders: Order[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_more: boolean;
}

/**
 * Payment intent (for Paystack)
 */
export interface PaymentIntent {
  id: string;
  amount: number;
  currency: string;
  status: string;
  reference: string;
  authorization_url: string;
  access_code: string;
}

/**
 * Checkout data
 */
export interface CheckoutData {
  email: string;
  full_name: string;
  phone: string;
  payment_method: 'paystack' | 'stripe' | 'bank_transfer';
  save_payment_method?: boolean;
}

/**
 * Get current user's cart
 */
export async function getCart(): Promise<Cart> {
  try {
    const response = await apiClient.get<Cart>('/cart');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch cart:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Add item to cart
 */
export async function addToCart(
  beatId: string,
  licenseType: string,
  quantity: number = 1
): Promise<Cart> {
  try {
    const response = await apiClient.post<Cart>('/cart/items', {
      beat_id: beatId,
      license_type: licenseType,
      quantity,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to add item to cart:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Update cart item quantity
 */
export async function updateCartItem(
  itemId: string,
  quantity: number
): Promise<Cart> {
  try {
    const response = await apiClient.patch<Cart>(`/cart/items/${itemId}`, {
      quantity,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to update cart item:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Remove item from cart
 */
export async function removeFromCart(itemId: string): Promise<Cart> {
  try {
    const response = await apiClient.delete<Cart>(`/cart/items/${itemId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to remove item from cart:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Clear entire cart
 */
export async function clearCart(): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.delete<{ success: boolean }>('/cart');
    return response.data;
  } catch (error) {
    console.error('Failed to clear cart:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Apply coupon code to cart
 */
export async function applyCoupon(code: string): Promise<Cart> {
  try {
    const response = await apiClient.post<Cart>('/cart/coupons', { code });
    return response.data;
  } catch (error) {
    console.error('Failed to apply coupon:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Remove coupon from cart
 */
export async function removeCoupon(couponId: string): Promise<Cart> {
  try {
    const response = await apiClient.delete<Cart>(`/cart/coupons/${couponId}`);
    return response.data;
  } catch (error) {
    console.error('Failed to remove coupon:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Create payment intent (Paystack)
 */
export async function createPaymentIntent(
  amount: number,
  email: string
): Promise<PaymentIntent> {
  try {
    const response = await apiClient.post<PaymentIntent>('/payments/intent', {
      amount,
      email,
      currency: 'NGN',
    });
    return response.data;
  } catch (error) {
    console.error('Failed to create payment intent:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Verify payment and create order
 */
export async function verifyPayment(
  reference: string,
  checkoutData: CheckoutData
): Promise<Order> {
  try {
    const response = await apiClient.post<Order>('/payments/verify', {
      reference,
      ...checkoutData,
    });
    return response.data;
  } catch (error) {
    console.error('Failed to verify payment:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Create order directly (without payment)
 */
export async function createOrder(
  checkoutData: CheckoutData
): Promise<Order> {
  try {
    const response = await apiClient.post<Order>('/orders', checkoutData);
    return response.data;
  } catch (error) {
    console.error('Failed to create order:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get user's orders
 */
export async function getOrders(
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  status?: OrderStatus
): Promise<OrdersResponse> {
  try {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: Math.min(page_size, PAGINATION.MAX_PAGE_SIZE).toString(),
    });

    if (status) params.append('status', status);

    const response = await apiClient.get<OrdersResponse>(`/orders?${params}`);
    return response.data;
  } catch (error) {
    console.error('Failed to fetch orders:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get single order details
 */
export async function getOrder(orderId: string): Promise<Order> {
  try {
    const response = await apiClient.get<Order>(`/orders/${orderId}`);
    return response.data;
  } catch (error) {
    console.error(`Failed to fetch order ${orderId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get order download link
 */
export async function getOrderDownloadLink(
  orderId: string,
  itemId: string
): Promise<{ download_url: string; expires_at: string }> {
  try {
    const response = await apiClient.get<{ download_url: string; expires_at: string }>(
      `/orders/${orderId}/items/${itemId}/download`
    );
    return response.data;
  } catch (error) {
    console.error('Failed to get download link:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Cancel order
 */
export async function cancelOrder(orderId: string, reason?: string): Promise<Order> {
  try {
    const response = await apiClient.post<Order>(`/orders/${orderId}/cancel`, {
      reason,
    });
    return response.data;
  } catch (error) {
    console.error(`Failed to cancel order ${orderId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get invoice for order
 */
export async function getOrderInvoice(orderId: string): Promise<{ url: string }> {
  try {
    const response = await apiClient.get<{ url: string }>(`/orders/${orderId}/invoice`);
    return response.data;
  } catch (error) {
    console.error(`Failed to get invoice for order ${orderId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Request refund for order
 */
export async function requestRefund(
  orderId: string,
  reason: string,
  details?: string
): Promise<{ refund_id: string; status: string }> {
  try {
    const response = await apiClient.post<{ refund_id: string; status: string }>(
      `/orders/${orderId}/refund`,
      { reason, details }
    );
    return response.data;
  } catch (error) {
    console.error(`Failed to request refund for order ${orderId}:`, getErrorMessage(error));
    throw error;
  }
}

/**
 * Get payment methods
 */
export async function getPaymentMethods(): Promise<any[]> {
  try {
    const response = await apiClient.get<{ methods: any[] }>('/payments/methods');
    return response.data.methods;
  } catch (error) {
    console.error('Failed to fetch payment methods:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Save payment method
 */
export async function savePaymentMethod(
  paymentMethodId: string,
  setAsDefault: boolean = false
): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.post<{ success: boolean }>(
      '/payments/methods/save',
      {
        payment_method_id: paymentMethodId,
        set_as_default: setAsDefault,
      }
    );
    return response.data;
  } catch (error) {
    console.error('Failed to save payment method:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Delete payment method
 */
export async function deletePaymentMethod(paymentMethodId: string): Promise<{ success: boolean }> {
  try {
    const response = await apiClient.delete<{ success: boolean }>(
      `/payments/methods/${paymentMethodId}`
    );
    return response.data;
  } catch (error) {
    console.error('Failed to delete payment method:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get available coupons
 */
export async function getAvailableCoupons(): Promise<any[]> {
  try {
    const response = await apiClient.get<{ coupons: any[] }>('/coupons/available');
    return response.data.coupons;
  } catch (error) {
    console.error('Failed to fetch available coupons:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Validate coupon code
 */
export async function validateCoupon(code: string): Promise<{
  valid: boolean;
  discount: number;
  message?: string;
}> {
  try {
    const response = await apiClient.post<{
      valid: boolean;
      discount: number;
      message?: string;
    }>('/coupons/validate', { code });
    return response.data;
  } catch (error) {
    console.error('Failed to validate coupon:', getErrorMessage(error));
    throw error;
  }
}

/**
 * Get order statistics (admin/seller only)
 */
export async function getOrderStats(): Promise<{
  total_orders: number;
  total_revenue: number;
  pending_orders: number;
  completed_orders: number;
}> {
  try {
    const response = await apiClient.get('/orders/stats');
    return response.data;
  } catch (error) {
    console.error('Failed to fetch order statistics:', getErrorMessage(error));
    throw error;
  }
}

export default {
  getCart,
  addToCart,
  updateCartItem,
  removeFromCart,
  clearCart,
  applyCoupon,
  removeCoupon,
  createPaymentIntent,
  verifyPayment,
  createOrder,
  getOrders,
  getOrder,
  getOrderDownloadLink,
  cancelOrder,
  getOrderInvoice,
  requestRefund,
  getPaymentMethods,
  savePaymentMethod,
  deletePaymentMethod,
  getAvailableCoupons,
  validateCoupon,
  getOrderStats,
};
