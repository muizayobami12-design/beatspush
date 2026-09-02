import type { Metadata, Viewport } from 'next';
import { Inter } from 'next/font/google';
import '@/styles/globals.css';
import { Providers } from './providers';
import { cn } from '@/lib/utils';
import { Toaster } from 'sonner';

const inter = Inter({ 
  subsets: ['latin'],
  variable: '--font-sans',
  display: 'swap',
});

export const metadata: Metadata = {
  title: {
    default: 'BeatPush - AI-Powered Music Promotion Platform',
    template: '%s | BeatPush',
  },
  description:
    'Empower African music creators with AI-driven promotion, analytics, and monetization tools.',
  keywords: [
    'music promotion',
    'African music',
    'beat marketplace',
    'music analytics',
    'artist platform',
    'music distribution',
    'beat sales',
    'music monetization',
  ],
  authors: [{ name: 'BeatPush' }],
  creator: 'BeatPush',
  openGraph: {
    title: 'BeatPush - AI-Powered Music Promotion Platform',
    description:
      'Empower African music creators with AI-driven promotion, analytics, and monetization tools.',
    type: 'website',
    locale: 'en_US',
    url: 'https://beatspush-1.onrender.com',
    siteName: 'BeatPush',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'BeatPush - AI-Powered Music Promotion Platform',
    description:
      'Empower African music creators with AI-driven promotion, analytics, and monetization tools.',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: [
    { media: '(prefers-color-scheme: light)', color: '#ffffff' },
    { media: '(prefers-color-scheme: dark)', color: '#0a0a0a' },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className={cn('font-sans', inter.variable)}>
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              try {
                const theme = JSON.parse(localStorage.getItem('theme') || '{"state":{"theme":"light"}}').state.theme;
                document.documentElement.classList.add(theme);
                document.documentElement.setAttribute('data-theme', theme);
              } catch (e) {
                document.documentElement.classList.add('light');
              }
            `,
          }}
        />
      </head>
      <body className={inter.className}>
        {/* Skip Navigation Link for Accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-4 focus:py-2 focus:text-primary-foreground focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        >
          Skip to main content
        </a>
        
        <Providers>{children}</Providers>
        <Toaster position="top-right" richColors expand={true} />
      </body>
    </html>
  );
}
