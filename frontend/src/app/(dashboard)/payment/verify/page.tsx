'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { CheckCircle, XCircle, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { paymentService } from '@/services/paymentService';

export default function PaymentVerifyPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const reference = searchParams.get('reference');
  
  const [status, setStatus] = useState<'loading' | 'success' | 'failed'>('loading');
  const [details, setDetails] = useState<any>(null);

  useEffect(() => {
    if (reference) {
      verifyPayment();
    } else {
      setStatus('failed');
    }
  }, [reference]);

  const verifyPayment = async () => {
    try {
      const result = await paymentService.verifyPayment(reference!);
      
      if (result.status === 'success') {
        setStatus('success');
        setDetails(result);
      } else {
        setStatus('failed');
        setDetails(result);
      }
    } catch (error) {
      console.error('Payment verification failed:', error);
      setStatus('failed');
    }
  };

  if (status === 'loading') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[600px] space-y-4">
        <Loader2 className="w-16 h-16 animate-spin text-primary" />
        <h2 className="text-2xl font-bold">Verifying Payment</h2>
        <p className="text-muted-foreground">Please wait while we confirm your payment...</p>
      </div>
    );
  }

  if (status === 'success') {
    return (
      <div className="flex flex-col items-center justify-center min-h-[600px] space-y-6">
        <div className="w-20 h-20 rounded-full bg-green-500/10 flex items-center justify-center">
          <CheckCircle className="w-12 h-12 text-green-500" />
        </div>
        
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold">Payment Successful!</h2>
          <p className="text-muted-foreground">
            Your payment has been confirmed
          </p>
        </div>

        {details && (
          <div className="bg-card border rounded-lg p-6 max-w-md w-full space-y-3">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Reference</span>
              <span className="font-medium">{details.reference}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Amount</span>
              <span className="font-medium">
                {(details.amount / 100).toLocaleString('en-NG', {
                  style: 'currency',
                  currency: details.currency || 'NGN',
                })}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Channel</span>
              <span className="font-medium capitalize">{details.channel}</span>
            </div>
            {details.paid_at && (
              <div className="flex justify-between">
                <span className="text-muted-foreground">Paid At</span>
                <span className="font-medium">
                  {new Date(details.paid_at).toLocaleString()}
                </span>
              </div>
            )}
          </div>
        )}

        <div className="flex gap-4">
          <Button onClick={() => router.push('/beats')}>
            Browse More Beats
          </Button>
          <Button variant="outline" onClick={() => router.push('/dashboard')}>
            Go to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[600px] space-y-6">
      <div className="w-20 h-20 rounded-full bg-red-500/10 flex items-center justify-center">
        <XCircle className="w-12 h-12 text-red-500" />
      </div>
      
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-bold">Payment Failed</h2>
        <p className="text-muted-foreground">
          {details?.message || 'We couldn\'t process your payment'}
        </p>
      </div>

      {details && (
        <div className="bg-card border rounded-lg p-6 max-w-md w-full space-y-3">
          <div className="flex justify-between">
            <span className="text-muted-foreground">Reference</span>
            <span className="font-medium">{reference}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">Status</span>
            <span className="font-medium text-red-500 capitalize">{details.status}</span>
          </div>
        </div>
      )}

      <div className="flex gap-4">
        <Button onClick={() => router.back()}>
          Try Again
        </Button>
        <Button variant="outline" onClick={() => router.push('/dashboard')}>
          Go to Dashboard
        </Button>
      </div>
    </div>
  );
}
