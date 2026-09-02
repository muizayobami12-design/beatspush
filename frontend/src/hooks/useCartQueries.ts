/**
 * React Query hooks for cart and order operations
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
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
  CheckoutData,
  OrderStatus,
  Cart,
  Order,
  OrdersResponse,
  PaymentIntent,
} from '@/services/cartService';
import { QUERY_KEYS, PAGINATION } from '@/lib/constants';

/**
 * Fetch user's cart
 */
export function useCart(enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'cart'],
    queryFn: () => getCart(),
    enabled,
    staleTime: 2 * 60 * 1000, // 2 minutes
    gcTime: 5 * 60 * 1000, // 5 minutes
  });
}

/**
 * Fetch user's orders
 */
export function useOrders(
  page: number = 1,
  page_size: number = PAGINATION.DEFAULT_PAGE_SIZE,
  status?: OrderStatus,
  enabled: boolean = true
) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'orders', page, status],
    queryFn: () => getOrders(page, page_size, status),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

/**
 * Fetch single order
 */
export function useOrder(orderId: string, enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'order', orderId],
    queryFn: () => getOrder(orderId),
    enabled,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 15 * 60 * 1000, // 15 minutes
  });
}

/**
 * Fetch payment methods
 */
export function usePaymentMethods(enabled: boolean = true) {
  return useQuery({
    queryKey: ['payment_methods'],
    queryFn: () => getPaymentMethods(),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Fetch available coupons
 */
export function useAvailableCoupons(enabled: boolean = true) {
  return useQuery({
    queryKey: ['coupons', 'available'],
    queryFn: () => getAvailableCoupons(),
    enabled,
    staleTime: 15 * 60 * 1000, // 15 minutes
    gcTime: 1 * 60 * 60 * 1000, // 1 hour
  });
}

/**
 * Fetch order statistics
 */
export function useOrderStats(enabled: boolean = true) {
  return useQuery({
    queryKey: [QUERY_KEYS.BEATS, 'orders', 'stats'],
    queryFn: () => getOrderStats(),
    enabled,
    staleTime: 10 * 60 * 1000, // 10 minutes
    gcTime: 30 * 60 * 1000, // 30 minutes
  });
}

/**
 * Add item to cart mutation
 */
export function useAddToCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      beatId,
      licenseType,
      quantity,
    }: {
      beatId: string;
      licenseType: string;
      quantity?: number;
    }) => addToCart(beatId, licenseType, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
    },
  });
}

/**
 * Update cart item mutation
 */
export function useUpdateCartItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ itemId, quantity }: { itemId: string; quantity: number }) =>
      updateCartItem(itemId, quantity),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
    },
  });
}

/**
 * Remove from cart mutation
 */
export function useRemoveFromCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (itemId: string) => removeFromCart(itemId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
    },
  });
}

/**
 * Clear cart mutation
 */
export function useClearCart() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => clearCart(),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
    },
  });
}

/**
 * Apply coupon mutation
 */
export function useApplyCoupon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (code: string) => applyCoupon(code),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
    },
  });
}

/**
 * Remove coupon mutation
 */
export function useRemoveCoupon() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (couponId: string) => removeCoupon(couponId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
    },
  });
}

/**
 * Validate coupon mutation
 */
export function useValidateCoupon() {
  return useMutation({
    mutationFn: (code: string) => validateCoupon(code),
  });
}

/**
 * Create payment intent mutation
 */
export function useCreatePaymentIntent() {
  return useMutation({
    mutationFn: ({ amount, email }: { amount: number; email: string }) =>
      createPaymentIntent(amount, email),
  });
}

/**
 * Verify payment mutation
 */
export function useVerifyPayment() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      reference,
      checkoutData,
    }: {
      reference: string;
      checkoutData: CheckoutData;
    }) => verifyPayment(reference, checkoutData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'orders'] });
    },
  });
}

/**
 * Create order mutation
 */
export function useCreateOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (checkoutData: CheckoutData) => createOrder(checkoutData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'cart'] });
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'orders'] });
    },
  });
}

/**
 * Get order download link mutation
 */
export function useGetOrderDownloadLink() {
  return useMutation({
    mutationFn: ({ orderId, itemId }: { orderId: string; itemId: string }) =>
      getOrderDownloadLink(orderId, itemId),
  });
}

/**
 * Cancel order mutation
 */
export function useCancelOrder() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) =>
      cancelOrder(orderId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'orders'] });
    },
  });
}

/**
 * Get order invoice mutation
 */
export function useGetOrderInvoice() {
  return useMutation({
    mutationFn: (orderId: string) => getOrderInvoice(orderId),
  });
}

/**
 * Request refund mutation
 */
export function useRequestRefund() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      orderId,
      reason,
      details,
    }: {
      orderId: string;
      reason: string;
      details?: string;
    }) => requestRefund(orderId, reason, details),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [QUERY_KEYS.BEATS, 'orders'] });
    },
  });
}

/**
 * Save payment method mutation
 */
export function useSavePaymentMethod() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      paymentMethodId,
      setAsDefault,
    }: {
      paymentMethodId: string;
      setAsDefault?: boolean;
    }) => savePaymentMethod(paymentMethodId, setAsDefault),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment_methods'] });
    },
  });
}

/**
 * Delete payment method mutation
 */
export function useDeletePaymentMethod() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (paymentMethodId: string) => deletePaymentMethod(paymentMethodId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payment_methods'] });
    },
  });
}

export default {
  useCart,
  useOrders,
  useOrder,
  usePaymentMethods,
  useAvailableCoupons,
  useOrderStats,
  useAddToCart,
  useUpdateCartItem,
  useRemoveFromCart,
  useClearCart,
  useApplyCoupon,
  useRemoveCoupon,
  useValidateCoupon,
  useCreatePaymentIntent,
  useVerifyPayment,
  useCreateOrder,
  useGetOrderDownloadLink,
  useCancelOrder,
  useGetOrderInvoice,
  useRequestRefund,
  useSavePaymentMethod,
  useDeletePaymentMethod,
};
