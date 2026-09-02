import Link from 'next/link';
import { Home, Search, RotateCcw } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-background via-background to-primary/5 p-6">
      <div className="text-center max-w-2xl w-full space-y-8">
        {/* 404 Visual */}
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full scale-150"></div>
            <h1 className="text-9xl font-black bg-gradient-to-r from-primary via-secondary to-primary bg-clip-text text-transparent relative">
              404
            </h1>
          </div>
        </div>

        {/* Message */}
        <div className="space-y-3">
          <h2 className="text-3xl font-bold text-foreground">
            Page Not Found
          </h2>
          <p className="text-lg text-muted-foreground">
            The page you're looking for doesn't exist or has been moved. Let's get you back on track!
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <Link href="/dashboard" className="w-full sm:w-auto">
            <button className="w-full inline-flex items-center justify-center gap-2 px-8 py-4 bg-gradient-to-r from-primary to-primary/80 text-primary-foreground font-semibold rounded-lg hover:shadow-lg hover:shadow-primary/50 transition-all hover:scale-105 active:scale-95">
              <Home className="h-5 w-5" />
              Go to Dashboard
            </button>
          </Link>
          
          <Link href="/discover" className="w-full sm:w-auto">
            <button className="w-full inline-flex items-center justify-center gap-2 px-8 py-4 bg-card border border-primary/30 text-foreground font-semibold rounded-lg hover:border-primary/60 hover:bg-primary/5 transition-all">
              <Search className="h-5 w-5" />
              Explore Beats
            </button>
          </Link>

          <button
            onClick={() => window.history.back()}
            className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-8 py-4 bg-card border border-border text-foreground font-semibold rounded-lg hover:bg-muted transition-all"
          >
            <RotateCcw className="h-5 w-5" />
            Go Back
          </button>
        </div>

        {/* Suggestions */}
        <div className="bg-card/50 border border-primary/20 rounded-lg p-6 text-sm text-muted-foreground space-y-4">
          <div>
            <p className="font-semibold text-foreground mb-3">Popular Pages:</p>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              <Link href="/dashboard" className="text-primary hover:text-primary/80 transition">
                • Dashboard
              </Link>
              <Link href="/discover" className="text-primary hover:text-primary/80 transition">
                • Discover Beats
              </Link>
              <Link href="/profile" className="text-primary hover:text-primary/80 transition">
                • My Profile
              </Link>
              <Link href="/messages" className="text-primary hover:text-primary/80 transition">
                • Messages
              </Link>
            </div>
          </div>
        </div>

        {/* Footer Note */}
        <p className="text-xs text-muted-foreground">
          If you think this is a mistake, please{' '}
          <a href="mailto:support@beatspush.com" className="text-primary hover:text-primary/80">
            contact support
          </a>
        </p>
      </div>
    </div>
  );
}
