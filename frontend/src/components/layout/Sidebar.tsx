'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ReactNode } from 'react';

interface NavItem {
  label: string;
  href: string;
  icon: string;
  badge?: number;
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: 'dashboard' },
  { label: 'Role Switcher', href: '/dashboard/switch-role', icon: 'supervised_user_circle' },
  { label: 'Royalties', href: '/dashboard/royalties', icon: 'payments' },
  { label: 'Inbox', href: '/dashboard/inbox', icon: 'move_to_inbox' },
  { label: 'Discovery', href: '/dashboard/discovery', icon: 'explore' },
  { label: 'Settings', href: '/dashboard/settings', icon: 'settings' },
];

export function Sidebar() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    if (href === '/dashboard') {
      return pathname === '/dashboard' || pathname === '/dashboard/';
    }
    return pathname.startsWith(href);
  };

  return (
    <>
      {/* Desktop Sidebar - Hidden on mobile */}
      <nav className="hidden md:flex flex-col h-screen py-stack-md px-4 bg-surface-container-lowest fixed left-0 top-0 w-64 border-r border-outline-variant/15 z-50">
        {/* Logo Section */}
        <div className="mb-stack-lg flex flex-col items-start px-2">
          <h1 className="font-headline-md text-headline-md font-bold text-primary">BeatsPush</h1>
          <p className="font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider mt-1">
            Modern Heritage
          </p>
        </div>

        {/* Navigation Links */}
        <div className="flex flex-col gap-2 flex-grow">
          {NAV_ITEMS.map((item) => {
            const active = isActive(item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg
                  font-medium transition-all duration-200
                  ${
                    active
                      ? 'text-secondary font-bold border-r-2 border-secondary scale-95 bg-surface-container-low'
                      : 'text-on-surface-variant hover:text-primary'
                  }
                `}
              >
                <span
                  className="material-symbols-outlined text-[20px]"
                  style={active ? { fontVariationSettings: "'FILL' 1" } : {}}
                >
                  {item.icon}
                </span>
                <span className="font-label-sm text-label-sm">{item.label}</span>
                {item.badge && (
                  <span className="ml-auto bg-secondary text-black text-xs font-bold px-2 py-1 rounded-full">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </div>

        {/* Submit Track Button */}
        <div className="mt-auto pt-stack-md">
          <button
            className="
              w-full flex items-center justify-center gap-2 py-3 px-4 rounded
              muted-gold-bg text-black font-label-sm text-label-sm
              uppercase tracking-wider hover:bg-opacity-90 transition-opacity
            "
          >
            <span className="material-symbols-outlined text-[16px]">upload</span>
            Submit Track
          </button>
        </div>
      </nav>

      {/* Mobile Navigation - Shown at bottom on mobile (placeholder) */}
      {/* This will be integrated into the TopNav component for mobile */}
    </>
  );
}
