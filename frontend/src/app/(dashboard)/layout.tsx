'use client';

import { ErrorBoundary } from '@/components/ErrorBoundary';
import { ChatProvider } from '@/components/chat';
import { AppShell } from '@/components/layout/AppShell';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ErrorBoundary>
      <ChatProvider>
        <AppShell>
          <ErrorBoundary>
            {children}
          </ErrorBoundary>
        </AppShell>
      </ChatProvider>
    </ErrorBoundary>
  );
}

