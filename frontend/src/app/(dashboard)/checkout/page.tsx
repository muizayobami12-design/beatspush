'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ArrowLeft, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useCart, useVerifyPayment, useCreateOrder } from '@/hooks/useCartQueries';
import { useAuthStore } from '@/store/authStore';
import { useApiError } from '@/hooks/useApiError';
import { cn } from '@/lib/utils';

export default function CheckoutPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { handleError } = useApiError();
  
  // Fetch cart
  const { data: cartData, isLoading: cartLoading } = useCart(!!user?.id);
  const items = cartData?.items || [];

  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [paymentInitiated, setPaymentInitiated] = useState(false);

  const [formData, setFormData] = useState({
    email: user?.email || '',
    fullName: user?.full_name || '',
    phone: '',
  });

  const verifyPaymentMutation = useVerifyPayment();
  const createOrderMutation = useCreateOrder();

  const subtotal = items.reduce((sum, item) => sum + (item.beat.price * (item.quantity || 1)), 0);
  const platformFee = subtotal * 0.15;
  const grandTotal = subtotal + platformFee;

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  // Initialize Paystack payment
  const initializePayment = () => {
    if (!formData.email || !formData.fullName || !formData.phone) {
      setError('Please fill in all required fields');
      return;
    }

    setIsProcessing(true);
    setPaymentInitiated(true);

    // Load Paystack script
    const script = document.createElement('script');
    script.src = 'https://js.paystack.co/v1/inline.js';
    script.async = true;
    
    script.onload = () => {
      const PaystackPop = (window as any).PaystackPop;
      
      const handler = PaystackPop.setup({
        key: process.env.NEXT_PUBLIC_PAYSTACK_KEY || '',
        email: formData.email,
        amount: Math.round(grandTotal * 100), // Paystack wants amount in kobo
        currency: 'NGN',
        ref: `BP-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        onClose: () => {
          setIsProcessing(false);
          setError('Payment cancelled');
        },
        onSuccess: async (response: any) => {
          try {
            // Verify payment with backend
            await verifyPaymentMutation.mutateAsync({
              reference: response.reference,
              checkoutData: {
                email: formData.email,
                full_name: formData.fullName,
                phone: formData.phone,
                items: items.map(item => ({
                  beat_id: item.beat.id,
                  license_type: item.license_type,
                  quantity: item.quantity || 1,
                })),
                amount: grandTotal,
              },
            });

            handleError(null as any, {
              customMessage: 'Payment successful! Your beats are ready to download.',
              isSuccess: true,
            });

            // Redirect to downloads
            setTimeout(() => {
              router.push('/downloads?payment=success');
            }, 1500);
          } catch (err) {
            handleError(err as Error, { customMessage: 'Payment verified but order processing failed.' });
          } finally {
            setIsProcessing(false);
          }
        },
      });

      handler.openIframe();
    };

    document.head.appendChild(script);
  };

  if (cartLoading) {
    return (
      <div className="min-h-screen bg-background pb-24">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg flex items-center justify-center min-h-96">
          <Loader2 className="h-8 w-8 text-secondary animate-spin" />
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    router.push('/cart');
    return null;
  }

  if (!user) {
    return (
      <div className="min-h-screen bg-background pb-24">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              Please log in to complete checkout
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className={cn(
        'border-b border-outline-variant/20 bg-surface'
      )}>
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-md">
          <Link href="/cart">
            <Button 
              variant="ghost" 
              size="sm" 
              className="gap-2 mb-4 text-on-surface-variant hover:text-on-surface"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Cart
            </Button>
          </Link>
          <h1 className={cn(
            'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
            'text-on-surface'
          )}>
            Checkout
          </h1>
        </div>
      </div>

      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
          {/* Checkout Form */}
          <div className="lg:col-span-2 space-y-gutter">
            {/* Error Message */}
            {error && (
              <div className={cn(
                'rounded-lg border p-4',
                'bg-destructive/10 border-destructive/30'
              )}>
                <div className="flex gap-3">
                  <AlertCircle className="h-5 w-5 text-destructive flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="font-body-md text-destructive mb-1">{error}</p>
                    <p className={cn(
                      'text-xs font-label-sm',
                      'text-on-surface-variant'
                    )}>
                      If this persists, please contact our support team.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Contact Information Card */}
            <div className={cn(
              'rounded-lg border ghost-border p-stack-md',
              'bg-surface-container-low'
            )}>
              <h2 className={cn(
                'font-headline-md text-headline-md',
                'text-on-surface mb-6'
              )}>
                Billing Information
              </h2>
              <div className="space-y-4">
                <div>
                  <label className={cn(
                    'block font-body-md text-body-md',
                    'text-on-surface mb-2'
                  )}>
                    Email Address
                  </label>
                  <Input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="your@email.com"
                    disabled={isProcessing}
                    className={cn(
                      'px-3 py-2 rounded-lg',
                      'bg-surface-container border border-outline-variant/30',
                      'text-on-surface placeholder-on-surface-variant/50',
                      'focus:outline-none focus:ring-2 focus:ring-secondary/40',
                      'disabled:opacity-50 disabled:cursor-not-allowed',
                      'transition-all duration-200'
                    )}
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className={cn(
                      'block font-body-md text-body-md',
                      'text-on-surface mb-2'
                    )}>
                      Full Name
                    </label>
                    <Input
                      type="text"
                      required
                      value={formData.fullName}
                      onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                      placeholder="John Doe"
                      disabled={isProcessing}
                      className={cn(
                        'px-3 py-2 rounded-lg',
                        'bg-surface-container border border-outline-variant/30',
                        'text-on-surface placeholder-on-surface-variant/50',
                        'focus:outline-none focus:ring-2 focus:ring-secondary/40',
                        'disabled:opacity-50 disabled:cursor-not-allowed',
                        'transition-all duration-200'
                      )}
                    />
                  </div>

                  <div>
                    <label className={cn(
                      'block font-body-md text-body-md',
                      'text-on-surface mb-2'
                    )}>
                      Phone Number
                    </label>
                    <Input
                      type="tel"
                      required
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      placeholder="+234 800 000 0000"
                      disabled={isProcessing}
                      className={cn(
                        'px-3 py-2 rounded-lg',
                        'bg-surface-container border border-outline-variant/30',
                        'text-on-surface placeholder-on-surface-variant/50',
                        'focus:outline-none focus:ring-2 focus:ring-secondary/40',
                        'disabled:opacity-50 disabled:cursor-not-allowed',
                        'transition-all duration-200'
                      )}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Payment Section */}
            <div className={cn(
              'rounded-lg border ghost-border p-stack-md',
              'bg-surface-container-low'
            )}>
              <h2 className={cn(
                'font-headline-md text-headline-md',
                'text-on-surface mb-6'
              )}>
                Payment Method
              </h2>

              <Button
                size="lg"
                className={cn(
                  'w-full gap-2',
                  'bg-secondary text-on-secondary hover:bg-secondary-fixed'
                )}
                onClick={initializePayment}
                disabled={isProcessing || !formData.email || !formData.fullName || !formData.phone}
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    Pay {formatPrice(grandTotal)} with Paystack
                  </>
                )}
              </Button>

              <p className={cn(
                'text-xs font-label-sm',
                'text-on-surface-variant mt-4'
              )}>
                Secure payment powered by Paystack
              </p>
            </div>

            {/* Security Notice */}
            <div className={cn(
              'rounded-lg border p-4',
              'bg-secondary/10 border-secondary/30'
            )}>
              <div className="flex gap-3">
                <CheckCircle2 className="h-5 w-5 text-secondary flex-shrink-0 mt-0.5" />
                <div>
                  <p className={cn(
                    'font-body-md font-medium',
                    'text-secondary mb-1'
                  )}>
                    Secure & Safe
                  </p>
                  <p className={cn(
                    'text-xs font-label-sm',
                    'text-on-surface-variant'
                  )}>
                    Your payment information is encrypted and processed securely by Paystack. You'll receive license certificates and download links via email immediately after payment.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Order Summary Sidebar */}
          <div className="lg:col-span-1">
            <div className={cn(
              'rounded-lg border ghost-border p-stack-md',
              'bg-surface-container-low sticky top-4'
            )}>
              <h2 className={cn(
                'font-headline-md text-headline-md',
                'text-on-surface mb-6'
              )}>
                Order Summary
              </h2>

              {/* Items List */}
              <div className="space-y-3 mb-6 max-h-64 overflow-y-auto">
                {items.map((item) => (
                  <div 
                    key={item.id} 
                    className={cn(
                      'flex gap-3 pb-3',
                      'border-b border-outline-variant/20 last:border-0'
                    )}
                  >
                    <div className={cn(
                      'w-12 h-12 rounded-md flex-shrink-0',
                      'bg-gradient-to-br from-secondary/20 to-tertiary/20',
                      'border border-outline-variant/20'
                    )} />
                    <div className="flex-1 min-w-0">
                      <h4 className={cn(
                        'font-body-md font-semibold',
                        'text-on-surface truncate'
                      )}>
                        {item.beat.title}
                      </h4>
                      <p className={cn(
                        'text-xs font-label-sm',
                        'text-on-surface-variant'
                      )}>
                        {item.license_type || 'Standard'} License
                      </p>
                      <p className={cn(
                        'font-headline-md text-headline-md',
                        'text-secondary mt-1'
                      )}>
                        {formatPrice(item.beat.price)}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pricing Breakdown */}
              <div className={cn(
                'space-y-3 pt-4',
                'border-t border-outline-variant/20'
              )}>
                <div className="flex justify-between items-center">
                  <span className={cn(
                    'font-body-md text-body-md',
                    'text-on-surface-variant'
                  )}>
                    Subtotal
                  </span>
                  <span className={cn(
                    'font-label-sm font-medium',
                    'text-on-surface'
                  )}>
                    {formatPrice(subtotal)}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className={cn(
                    'font-body-md text-body-md',
                    'text-on-surface-variant'
                  )}>
                    Platform Fee (15%)
                  </span>
                  <span className={cn(
                    'font-label-sm font-medium',
                    'text-on-surface'
                  )}>
                    {formatPrice(platformFee)}
                  </span>
                </div>

                <div className={cn(
                  'flex justify-between items-center pt-3',
                  'border-t border-outline-variant/20'
                )}>
                  <span className={cn(
                    'font-headline-md text-headline-md',
                    'text-on-surface'
                  )}>
                    Total
                  </span>
                  <span className={cn(
                    'font-display-lg text-display-lg',
                    'text-secondary'
                  )}>
                    {formatPrice(grandTotal)}
                  </span>
                </div>
              </div>

              {/* Benefits List */}
              <div className={cn(
                'mt-6 pt-6 space-y-3',
                'border-t border-outline-variant/20'
              )}>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-secondary flex-shrink-0 mt-0.5" />
                  <p className={cn(
                    'text-xs font-label-sm',
                    'text-on-surface-variant'
                  )}>
                    Instant download after payment
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-secondary flex-shrink-0 mt-0.5" />
                  <p className={cn(
                    'text-xs font-label-sm',
                    'text-on-surface-variant'
                  )}>
                    License certificate included
                  </p>
                </div>
                <div className="flex items-start gap-2">
                  <CheckCircle2 className="h-4 w-4 text-secondary flex-shrink-0 mt-0.5" />
                  <p className={cn(
                    'text-xs font-label-sm',
                    'text-on-surface-variant'
                  )}>
                    Secure Paystack payment
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
