'use client';

import { useParams, useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { CheckCircle, Download, Music, ArrowLeft, Loader2, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export default function PurchaseSuccessPage() {
  const params = useParams();
  const router = useRouter();
  const reference = params.reference as string;
  const [verifying, setVerifying] = useState(true);
  const [verified, setVerified] = useState(false);

  // Simulate verification (in production, verify with backend)
  useEffect(() => {
    const timer = setTimeout(() => {
      setVerifying(false);
      setVerified(true);
    }, 2000);

    return () => clearTimeout(timer);
  }, []);

  if (verifying) {
    return (
      <div className="container max-w-2xl py-16">
        <div className="flex flex-col items-center justify-center text-center space-y-6">
          <Loader2 className="w-16 h-16 animate-spin text-primary" />
          <div>
            <h1 className="text-2xl font-bold mb-2">Verifying Payment</h1>
            <p className="text-muted-foreground">
              Please wait while we confirm your transaction...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (!verified) {
    return (
      <div className="container max-w-2xl py-16">
        <div className="flex flex-col items-center justify-center text-center space-y-6">
          <XCircle className="w-16 h-16 text-destructive" />
          <div>
            <h1 className="text-2xl font-bold mb-2">Payment Verification Failed</h1>
            <p className="text-muted-foreground mb-6">
              We couldn't verify your payment. Please contact support with reference: <br />
              <code className="text-sm bg-muted px-2 py-1 rounded">{reference}</code>
            </p>
            <div className="flex gap-3 justify-center">
              <Button variant="outline" onClick={() => router.push('/beats')}>
                Back to Beats
              </Button>
              <Button onClick={() => window.location.href = 'mailto:support@beatpush.com'}>
                Contact Support
              </Button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-2xl py-16">
      <div className="flex flex-col items-center justify-center text-center space-y-6">
        {/* Success Icon */}
        <div className="relative">
          <div className="absolute inset-0 bg-green-500/20 rounded-full blur-2xl" />
          <CheckCircle className="relative w-24 h-24 text-green-500" />
        </div>

        {/* Success Message */}
        <div className="space-y-2">
          <h1 className="text-3xl font-bold">Purchase Successful!</h1>
          <p className="text-lg text-muted-foreground">
            Your payment has been processed successfully
          </p>
        </div>

        {/* Transaction Details */}
        <div className="w-full max-w-md bg-card border rounded-lg p-6 space-y-3 text-left">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Transaction Reference</span>
            <code className="text-xs bg-muted px-2 py-1 rounded font-mono">
              {reference}
            </code>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Status</span>
            <span className="text-green-500 font-medium">Completed</span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Date</span>
            <span className="font-medium">
              {new Date().toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </span>
          </div>
        </div>

        {/* Download Section */}
        <div className="w-full max-w-md bg-primary/10 border border-primary/20 rounded-lg p-6 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-primary/20 flex items-center justify-center">
              <Music className="w-6 h-6 text-primary" />
            </div>
            <div className="flex-1 text-left">
              <h3 className="font-semibold">Your Beat is Ready!</h3>
              <p className="text-sm text-muted-foreground">
                Download your files and start creating
              </p>
            </div>
          </div>

          <Button className="w-full gap-2" size="lg">
            <Download className="w-5 h-5" />
            Download Files
          </Button>

          <div className="text-xs text-muted-foreground space-y-1">
            <p>✓ High-quality WAV file (24-bit)</p>
            <p>✓ Tagged MP3 file (320kbps)</p>
            <p>✓ License agreement (PDF)</p>
            <p>✓ Stems available (Optional)</p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex flex-col sm:flex-row gap-3 w-full max-w-md">
          <Button
            variant="outline"
            onClick={() => router.push('/beats')}
            className="flex-1"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Browse More Beats
          </Button>
          
          <Link href="/purchases" className="flex-1">
            <Button variant="default" className="w-full">
              View All Purchases
            </Button>
          </Link>
        </div>

        {/* Receipt */}
        <div className="text-sm text-muted-foreground">
          A receipt has been sent to your email address
        </div>
      </div>
    </div>
  );
}
