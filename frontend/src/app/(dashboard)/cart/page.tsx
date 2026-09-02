'use client';

import { ShoppingCart, Trash2, Music2, ArrowRight, CheckCircle2, Zap, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { useCart, useRemoveFromCart, useClearCart } from '@/hooks/useCartQueries';
import { useApiError } from '@/hooks/useApiError';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

export default function CartPage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { handleError } = useApiError();
  
  // Fetch cart from API
  const { data: cartData, isLoading, error } = useCart(!!user?.id);
  const removeFromCartMutation = useRemoveFromCart();
  const clearCartMutation = useClearCart();

  // Handle errors
  if (error) {
    handleError(error, { customMessage: 'Failed to load cart. Please try again.' });
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const items = cartData?.items || [];
  const itemCount = items.length;
  const subtotal = items.reduce((sum, item) => sum + (item.beat.price * (item.quantity || 1)), 0);
  const platformFee = subtotal * 0.15;
  const grandTotal = subtotal + platformFee;

  const handleCheckout = () => {
    if (items.length === 0) return;
    router.push('/checkout');
  };

  const handleRemoveItem = async (itemId: string) => {
    try {
      await removeFromCartMutation.mutateAsync(itemId);
    } catch (err) {
      handleError(err as Error, { customMessage: 'Failed to remove item from cart.' });
    }
  };

  const handleClearCart = async () => {
    if (!confirm('Are you sure you want to clear your cart?')) return;
    try {
      await clearCartMutation.mutateAsync();
    } catch (err) {
      handleError(err as Error, { customMessage: 'Failed to clear cart.' });
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background pb-24">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg flex items-center justify-center min-h-96">
          <div className="text-center">
            <Loader2 className="h-8 w-8 text-secondary animate-spin mx-auto mb-4" />
            <p className={cn('font-body-md text-body-md text-on-surface-variant')}>
              Loading your cart...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Not authenticated
  if (!user) {
    return (
      <div className="min-h-screen bg-background pb-24">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg flex items-center justify-center min-h-96">
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              Please log in to view your cart
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className={cn(
              'p-6 rounded-lg mb-6',
              'bg-surface-container border border-outline-variant/20'
            )}>
              <ShoppingCart className="h-16 w-16 text-on-surface-variant" />
            </div>
            <h2 className={cn(
              'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
              'text-on-surface mb-2'
            )}>
              Your cart is empty
            </h2>
            <p className={cn(
              'font-body-lg text-body-lg',
              'text-on-surface-variant mb-8 max-w-md'
            )}>
              Browse our marketplace and add beats to your cart to get started.
            </p>
            <Link href="/discover">
              <Button className="gap-2 bg-secondary text-on-secondary hover:bg-secondary-fixed">
                Browse Beats
                <ArrowRight className="h-5 w-5" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="border-b border-outline-variant/20 bg-surface">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-md">
          <div className="flex items-center justify-between flex-col md:flex-row gap-4">
            <div>
              <h1 className={cn(
                'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
                'text-on-surface mb-2'
              )}>
                Shopping Cart
              </h1>
              <p className={cn(
                'font-body-md text-body-md',
                'text-on-surface-variant'
              )}>
                {itemCount} {itemCount === 1 ? 'item' : 'items'} in your cart
              </p>
            </div>
            {items.length > 0 && (
              <Button 
                variant="ghost" 
                onClick={handleClearCart}
                disabled={clearCartMutation.isPending}
                className="text-destructive hover:bg-destructive/10 hover:text-destructive"
              >
                {clearCartMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Clearing...
                  </>
                ) : (
                  'Clear Cart'
                )}
              </Button>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-gutter">
          {/* Cart Items */}
          <div className="lg:col-span-2 space-y-gutter">
            {items.map((item) => (
              <div
                key={item.id}
                className={cn(
                  'rounded-lg border ghost-border p-stack-md',
                  'bg-surface-container-low hover:bg-surface-container',
                  'transition-all duration-200 group'
                )}
              >
                <div className="flex gap-stack-md">
                  {/* Beat Cover */}
                  <Link href={`/discover`} className="flex-shrink-0">
                    <div className={cn(
                      'w-24 h-24 rounded-md overflow-hidden',
                      'bg-gradient-to-br from-secondary/20 to-tertiary/20',
                      'border border-outline-variant/20'
                    )}>
                      {item.beat.cover_url ? (
                        <img
                          src={item.beat.cover_url}
                          alt={item.beat.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-200"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Music2 className="h-10 w-10 text-on-surface-variant opacity-30" />
                        </div>
                      )}
                    </div>
                  </Link>

                  {/* Beat Info */}
                  <div className="flex-1 min-w-0">
                    <h3 className={cn(
                      'font-body-md font-semibold text-on-surface',
                      'mb-1'
                    )}>
                      {item.beat.title}
                    </h3>
                    <p className={cn(
                      'font-label-sm text-label-sm',
                      'text-on-surface-variant mb-3'
                    )}>
                      by {item.beat.artist_name}
                    </p>

                    {/* License Type */}
                    <div className="flex items-center gap-2 mb-4">
                      <span className={cn(
                        'px-3 py-2 rounded-md font-label-sm text-label-sm',
                        'bg-secondary/20 text-secondary'
                      )}>
                        {item.license_type || 'Standard'}
                      </span>
                    </div>

                    {/* Beat Details */}
                    <div className="flex items-center gap-3 text-xs font-label-sm text-on-surface-variant">
                      <span className="px-2 py-1 bg-surface-container rounded">{item.beat.genre}</span>
                      {item.beat.bpm && (
                        <>
                          <span>•</span>
                          <span>{item.beat.bpm} BPM</span>
                        </>
                      )}
                      {item.beat.key && (
                        <>
                          <span>•</span>
                          <span>{item.beat.key}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Price & Remove */}
                  <div className="flex flex-col items-end justify-between">
                    <p className={cn(
                      'font-headline-md text-headline-md',
                      'text-secondary'
                    )}>
                      {formatPrice(item.beat.price)}
                    </p>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleRemoveItem(item.id)}
                      disabled={removeFromCartMutation.isPending}
                      className={cn(
                        'text-destructive hover:bg-destructive/10',
                        'font-label-sm text-label-sm'
                      )}
                    >
                      {removeFromCartMutation.isPending ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <>
                          <Trash2 className="h-4 w-4 mr-2" />
                          Remove
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Order Summary */}
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

              <div className="space-y-4 mb-6">
                <div className="flex justify-between items-center">
                  <span className={cn(
                    'font-body-md text-body-md',
                    'text-on-surface-variant'
                  )}>
                    Subtotal ({itemCount} {itemCount === 1 ? 'item' : 'items'})
                  </span>
                  <span className="font-label-sm font-medium text-on-surface">
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
                  <span className="font-label-sm font-medium text-on-surface">
                    {formatPrice(platformFee)}
                  </span>
                </div>
                <div className="border-t border-outline-variant/20 pt-4">
                  <div className="flex justify-between items-center">
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
              </div>

              <Button 
                size="lg" 
                className={cn(
                  'w-full mb-4 gap-2',
                  'bg-secondary text-on-secondary hover:bg-secondary-fixed'
                )}
                onClick={handleCheckout}
                disabled={isLoading || items.length === 0}
              >
                Proceed to Checkout
                <ArrowRight className="h-5 w-5" />
              </Button>

              <div className="space-y-3 text-xs font-label-sm text-on-surface-variant mb-6">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-secondary flex-shrink-0" />
                  <span>Instant delivery after payment</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-secondary flex-shrink-0" />
                  <span>Secure payment processing</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-secondary flex-shrink-0" />
                  <span>License certificate included</span>
                </div>
              </div>

              <div className="pt-6 border-t border-outline-variant/20">
                <p className={cn(
                  'text-xs text-center',
                  'text-on-surface-variant'
                )}>
                  By proceeding, you agree to our Terms of Service and License Agreement
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
