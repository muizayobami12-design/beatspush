'use client';

import { useEffect } from 'react';
import { AlertCircle, Home, RotateCcw } from 'lucide-react';
import Link from 'next/link';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('=== APPLICATION ERROR ===');
    console.error('Error:', error);
    console.error('Message:', error.message);
    console.error('Stack:', error.stack);
    console.error('========================');
  }, [error]);

  const isDevelopment = process.env.NODE_ENV === 'development';

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-6">
      <div className="text-center max-w-2xl w-full space-y-8">
        {/* Error Icon */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-red-500/20 blur-xl rounded-full"></div>
            <AlertCircle className="h-20 w-20 text-red-500 relative" />
          </div>
        </div>

        {/* Error Message */}
        <div className="space-y-3">
          <h1 className="text-5xl font-black bg-gradient-to-r from-red-500 via-red-400 to-red-600 bg-clip-text text-transparent">
            Oops!
          </h1>
          <h2 className="text-3xl font-bold text-foreground">
            Something went wrong
          </h2>
          <p className="text-lg text-muted-foreground">
            We encountered an unexpected error. Our team has been notified.
          </p>
        </div>

        {/* Error Details (Development Only) */}
        {isDevelopment && (
          <div className="rounded-lg bg-red-950/30 border border-red-500/30 p-6 text-left space-y-3">
            <p className="font-semibold text-red-400 flex items-center gap-2">
              <AlertCircle className="h-4 w-4" />
              Error Details (Development):
            </p>
            <pre className="overflow-auto text-xs text-red-300 whitespace-pre-wrap max-h-96 font-mono bg-black/30 p-3 rounded border border-red-500/20">
              {error.message}
              {error.stack && `\n\n${error.stack}`}
            </pre>
            {error.digest && (
              <p className="text-xs text-red-400">
                Error ID: <code className="bg-black/30 px-2 py-1 rounded">{error.digest}</code>
              </p>
            )}
          </div>
        )}

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground font-semibold rounded-lg hover:shadow-lg hover:shadow-primary/50 transition-all hover:scale-105 active:scale-95"
          >
            <RotateCcw className="h-5 w-5" />
            Try Again
          </button>
          <Link href="/dashboard">
            <button className="inline-flex items-center justify-center gap-2 px-8 py-4 bg-card border border-primary/30 text-foreground font-semibold rounded-lg hover:border-primary/60 hover:bg-primary/5 transition-all w-full sm:w-auto">
              <Home className="h-5 w-5" />
              Go to Dashboard
            </button>
          </Link>
        </div>

        {/* Helpful Tips */}
        <div className="bg-card/50 border border-primary/20 rounded-lg p-6 text-sm text-muted-foreground">
          <p className="font-semibold text-foreground mb-2">What can you try?</p>
          <ul className="space-y-2 text-left">
            <li>• Refresh the page to reload the data</li>
            <li>• Clear your browser cache if the problem persists</li>
            <li>• Check your internet connection</li>
            <li>• Try again in a few moments</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
