'use client';

import { useState, useEffect } from 'react';
import { Loader2, AlertCircle, CheckCircle2, CreditCard } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import { useToast } from '@/hooks/useToast';
import { paymentService } from '@/services/paymentService';

export interface PaymentFormProps {
  /** Item being purchased (beat, license, etc.) */
  itemId: string;
  /** Item title for display */
  itemTitle: string;
  /** Amount in currency units (NGN) */
  amount: number;
  /** Currency code (NGN, USD, etc.) */
  currency?: 'NGN' | 'USD';
  /** License type for beats */
  licenseType?: 'lease' | 'exclusive';
  /** Pre-filled email */
  email?: string;
  /** Callback on successful payment */
  onSuccess?: (reference: string, transactionId: string) => void;
  /** Callback on payment error */
  onError?: (error: Error) => void;
  /** Additional product details */
  description?: string;
  /** Button text */
  buttonText?: string;
  /** Disable form */
  disabled?: boolean;
  /** Custom className */
  className?: string;
}

/**
 * PaymentForm - Paystack payment integration component
 * Handles beat purchases, tips, subscriptions with Paystack
 */
export function PaymentForm({
  itemId,
  itemTitle,
  amount,
  currency = 'NGN',
  licenseType = 'lease',
  email: initialEmail,
  onSuccess,
  onError,
  description,
  buttonText = 'Pay Now',
  disabled = false,
  className,
}: PaymentFormProps) {
  const { toast } = useToast();

  // Form state
  const [email, setEmail] = useState(initialEmail || '');
  const [isProcessing, setIsProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState<string>('');

  // Paystack script state
  const [paystackReady, setPaystackReady] = useState(false);

  // Load Paystack script
  useEffect(() => {
    if (document.getElementById('paystack-script')) {
      setPaystackReady(true);
      return;
    }

    const script = document.createElement('script');
    script.id = 'paystack-script';
    script.src = 'https://js.paystack.co/v1/inline.js';
    script.async = true;
    script.onload = () => setPaystackReady(true);
    script.onerror = () => {
      setErrorMessage('Failed to load payment processor. Please try again.');
      toast({
        title: 'Error',
        description: 'Failed to load payment processor',
        variant: 'destructive',
      });
    };
    document.body.appendChild(script);
  }, [toast]);

  // Validate form
  const isFormValid = email.trim().length > 0 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);

  // Handle payment
  const handlePayment = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!isFormValid) {
      setErrorMessage('Please enter a valid email address');
      return;
    }

    if (!paystackReady) {
      setErrorMessage('Payment processor not ready. Please try again.');
      return;
    }

    setIsProcessing(true);
    setPaymentStatus('processing');
    setErrorMessage('');

    try {
      // Initiate payment with backend
      const paymentResponse = await paymentService.initiateBeatPurchase(
        itemId,
        licenseType
      );

      // Use Paystack inline popup
      const handler = (window as any).PaystackPop.setup({
        key: process.env.NEXT_PUBLIC_PAYSTACK_KEY,
        email: email,
        amount: amount * 100, // Paystack uses kobo (cents)
        ref: paymentResponse.reference,
        currency: currency,
        onClose: () => {
          setIsProcessing(false);
          setPaymentStatus('idle');
          toast({
            title: 'Payment Cancelled',
            description: 'You cancelled the payment process',
          });
        },
        onSuccess: async (response: any) => {
          try {
            // Verify payment with backend
            const verificationResponse = await paymentService.verifyPayment(
              response.reference
            );

            if (verificationResponse.status === 'success') {
              setPaymentStatus('success');
              toast({
                title: 'Payment Successful',
                description: `Payment of ${currency} ${amount.toLocaleString()} completed`,
              });

              // Call success callback
              if (onSuccess) {
                onSuccess(response.reference, verificationResponse.transaction.id);
              }

              // Reset form after 2 seconds
              setTimeout(() => {
                setEmail('');
                setPaymentStatus('idle');
              }, 2000);
            } else {
              throw new Error('Payment verification failed');
            }
          } catch (error) {
            const err = error instanceof Error ? error : new Error('Payment verification failed');
            setPaymentStatus('error');
            setErrorMessage(err.message);
            toast({
              title: 'Verification Failed',
              description: 'Payment was received but verification failed. Please contact support.',
              variant: 'destructive',
            });

            if (onError) {
              onError(err);
            }
          } finally {
            setIsProcessing(false);
          }
        },
      });

      handler.openIframe();
    } catch (error) {
      const err = error instanceof Error ? error : new Error('Payment initiation failed');
      setPaymentStatus('error');
      setErrorMessage(err.message || 'Failed to initiate payment. Please try again.');
      setIsProcessing(false);

      toast({
        title: 'Payment Error',
        description: err.message || 'Failed to process payment',
        variant: 'destructive',
      });

      if (onError) {
        onError(err);
      }
    }
  };

  return (
    <div className={cn('w-full max-w-md', className)}>
      {/* Order Summary */}
      <div className="mb-6 p-4 rounded-lg bg-surface-container-low border border-outline-variant/20">
        <h3 className="text-sm font-semibold text-on-surface mb-3">Order Summary</h3>

        <div className="space-y-2">
          <div className="flex justify-between items-start">
            <span className="text-sm text-on-surface-variant">{itemTitle}</span>
            <span className="font-medium text-on-surface">
              {currency} {amount.toLocaleString()}
            </span>
          </div>

          {description && (
            <p className="text-xs text-on-surface-variant italic">{description}</p>
          )}

          {licenseType === 'exclusive' && (
            <div className="pt-2 border-t border-outline-variant/20">
              <span className="text-xs font-medium text-secondary">Exclusive License</span>
            </div>
          )}
        </div>
      </div>

      {/* Payment Form */}
      <form onSubmit={handlePayment} className="space-y-4">
        {/* Email Input */}
        <div>
          <label htmlFor="payment-email" className="block text-sm font-medium text-on-surface mb-2">
            Email Address
          </label>
          <Input
            id="payment-email"
            type="email"
            placeholder="your@email.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            disabled={isProcessing || disabled}
            required
            className={cn(
              'w-full px-3 py-2 rounded-lg',
              'bg-surface-container-low border border-outline-variant/30',
              'text-on-surface placeholder-on-surface-variant/50',
              'focus:outline-none focus:ring-2 focus:ring-secondary/40',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              'transition-all duration-200'
            )}
          />
          <p className="text-xs text-on-surface-variant mt-1">
            Payment confirmation will be sent to this email
          </p>
        </div>

        {/* Error Message */}
        {errorMessage && (
          <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 flex gap-2">
            <AlertCircle className="w-4 h-4 text-destructive flex-shrink-0 mt-0.5" />
            <p className="text-sm text-destructive">{errorMessage}</p>
          </div>
        )}

        {/* Success Message */}
        {paymentStatus === 'success' && (
          <div className="p-3 rounded-lg bg-secondary/10 border border-secondary/30 flex gap-2">
            <CheckCircle2 className="w-4 h-4 text-secondary flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-secondary">Payment Successful</p>
              <p className="text-xs text-on-surface-variant">
                Your purchase has been completed. Check your email for details.
              </p>
            </div>
          </div>
        )}

        {/* Amount Display */}
        <div className="p-4 rounded-lg bg-surface-container border border-secondary/20">
          <div className="flex items-center justify-between">
            <span className="text-sm text-on-surface-variant">Total Amount</span>
            <span className="text-2xl font-bold text-secondary">
              {currency} {amount.toLocaleString()}
            </span>
          </div>
          <p className="text-xs text-on-surface-variant mt-2">
            Secure payment powered by Paystack
          </p>
        </div>

        {/* Pay Button */}
        <Button
          type="submit"
          disabled={!isFormValid || isProcessing || disabled || !paystackReady}
          className={cn(
            'w-full h-10 rounded-lg font-medium',
            'bg-secondary text-on-secondary hover:bg-secondary-fixed',
            'border border-transparent',
            'disabled:opacity-50 disabled:cursor-not-allowed',
            'transition-all duration-200',
            'flex items-center justify-center gap-2'
          )}
        >
          {isProcessing ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Processing...
            </>
          ) : (
            <>
              <CreditCard className="w-4 h-4" />
              {buttonText}
            </>
          )}
        </Button>

        {/* Security Notice */}
        <p className="text-xs text-on-surface-variant text-center">
          🔒 Your payment information is secure and encrypted
        </p>
      </form>

      {/* Paystack Info */}
      <div className="mt-4 p-3 rounded-lg bg-surface-container-low border border-outline-variant/20">
        <p className="text-xs text-on-surface-variant text-center">
          Payments are processed securely by{' '}
          <a
            href="https://paystack.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-secondary hover:underline font-medium"
          >
            Paystack
          </a>
        </p>
      </div>
    </div>
  );
}

export default PaymentForm;
