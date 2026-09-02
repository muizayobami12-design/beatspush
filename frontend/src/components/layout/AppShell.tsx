'use client';

import { ReactNode } from 'react';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';

interface AppShellProps {
  children: ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="bg-background text-on-background antialiased selection:bg-secondary selection:text-on-secondary min-h-screen flex flex-col md:flex-row">
      {/* Desktop Sidebar */}
      <Sidebar />

      {/* Top Navigation & Content */}
      <div className="flex-1 md:ml-64 flex flex-col">
        <TopNav />
        {/* Main Content Area */}
        <main className="flex-1 pt-16 min-h-screen">
          {children}
        </main>
      </div>
    </div>
  );
}
