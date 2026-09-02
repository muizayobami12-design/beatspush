'use client';

import Link from 'next/link';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export function TopNav() {
  const router = useRouter();
  const [isSearchFocused, setIsSearchFocused] = useState(false);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // TODO: Connect to actual user session when available
  const session = null;

  const handleLogout = async () => {
    try {
      // Call your logout API endpoint
      const response = await fetch('/api/auth/logout', { method: 'POST' });
      if (response.ok) {
        router.push('/');
        router.refresh();
      }
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <header
      className="
        fixed top-0 right-0 w-full md:w-[calc(100%-16rem)]
        bg-surface/80 backdrop-blur-md
        flex justify-between items-center h-16
        px-margin-mobile md:px-margin-desktop z-40
        border-b border-outline-variant/15
      "
    >
      {/* Mobile Logo - Hidden on desktop */}
      <div className="md:hidden flex items-center">
        <h1 className="font-headline-md text-headline-md font-bold text-primary text-xl">
          BeatsPush
        </h1>
      </div>

      {/* Desktop Search - Hidden on mobile */}
      <div
        className={`
          hidden md:flex flex-1 items-center gap-2 max-w-md
          ${isSearchFocused ? 'ring-1 ring-secondary/50' : ''}
          px-3 py-2 rounded transition-all duration-200
        `}
      >
        <span className="material-symbols-outlined text-on-surface-variant text-[20px]">
          search
        </span>
        <input
          type="text"
          placeholder="Search artists, tracks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onFocus={() => setIsSearchFocused(true)}
          onBlur={() => setIsSearchFocused(false)}
          className="
            w-full bg-transparent border-none text-body-md
            font-body-md text-on-surface placeholder:text-on-surface-variant/40
            focus:ring-0 outline-none
          "
        />
      </div>

      {/* Right Actions */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button
          className="
            text-on-surface-variant hover:text-primary
            transition-colors duration-200
            relative
          "
          title="Notifications"
        >
          <span className="material-symbols-outlined text-[24px]">notifications</span>
          {/* Notification Badge - Optional */}
          <span className="absolute -top-1 -right-1 w-2 h-2 bg-secondary rounded-full"></span>
        </button>

        {/* Wallet / Tips */}
        <button
          className="
            text-on-surface-variant hover:text-primary
            transition-colors duration-200
          "
          title="Wallet"
        >
          <span className="material-symbols-outlined text-[24px]">account_balance_wallet</span>
        </button>

        {/* User Profile Dropdown */}
        <div className="relative">
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="
              w-8 h-8 rounded-full overflow-hidden ghost-border
              hover:opacity-80 transition-opacity duration-200
              flex items-center justify-center
              bg-surface-container
            "
            title="User menu"
          >
            <span className="material-symbols-outlined text-[18px] text-on-surface-variant">
              account_circle
            </span>
          </button>

          {/* Dropdown Menu */}
          {isMenuOpen && (
            <div
              className="
                absolute right-0 mt-2 w-48
                bg-surface-container-low glass-panel rounded-lg
                shadow-xl z-50
                overflow-hidden
              "
            >
              {/* User Info */}
              {session && (
                <div className="px-4 py-3 border-b border-outline-variant/15">
                  <p className="font-body-md text-on-surface truncate">
                    {session?.user?.name || 'User'}
                  </p>
                  <p className="font-label-sm text-on-surface-variant text-xs truncate">
                    {session?.user?.email}
                  </p>
                </div>
              )}

              {/* Menu Items */}
              <div className="py-2">
                <Link
                  href="/dashboard/profile"
                  className="
                    block px-4 py-2 text-on-surface hover:bg-surface-container
                    transition-colors duration-150 font-body-md text-sm
                  "
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span className="material-symbols-outlined text-[16px] mr-2 align-middle">
                    person
                  </span>
                  Profile
                </Link>

                <Link
                  href="/dashboard/settings"
                  className="
                    block px-4 py-2 text-on-surface hover:bg-surface-container
                    transition-colors duration-150 font-body-md text-sm
                  "
                  onClick={() => setIsMenuOpen(false)}
                >
                  <span className="material-symbols-outlined text-[16px] mr-2 align-middle">
                    settings
                  </span>
                  Settings
                </Link>

                <div className="border-t border-outline-variant/15 my-2"></div>

                <button
                  onClick={() => {
                    setIsMenuOpen(false);
                    handleLogout();
                  }}
                  className="
                    w-full text-left px-4 py-2 text-error hover:bg-error/10
                    transition-colors duration-150 font-body-md text-sm
                  "
                >
                  <span className="material-symbols-outlined text-[16px] mr-2 align-middle">
                    logout
                  </span>
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Mobile Menu Toggle - For future mobile nav implementation */}
      <button className="md:hidden ml-4 text-on-surface-variant hover:text-primary">
        <span className="material-symbols-outlined text-[24px]">menu</span>
      </button>
    </header>
  );
}
