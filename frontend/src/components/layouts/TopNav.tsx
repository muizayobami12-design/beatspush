'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X, Bell, Search, User } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import { motion, AnimatePresence } from 'framer-motion';

interface TopNavProps {
  onMenuClick?: () => void;
}

export default function TopNav({ onMenuClick }: TopNavProps) {
  const { user } = useAuthStore();
  const [showNotifications, setShowNotifications] = useState(false);
  const [showProfile, setShowProfile] = useState(false);

  return (
    <header className="sticky top-0 z-30 bg-background/95 backdrop-blur-sm border-b border-yellow-400/20">
      <div className="px-4 md:px-8 py-4 flex items-center justify-between">
        {/* Left: Menu Button & Logo (Mobile) */}
        <div className="flex items-center gap-4">
          <button
            onClick={onMenuClick}
            className="md:hidden p-2 hover:bg-muted rounded-lg transition-colors"
            aria-label="Toggle menu"
          >
            <Menu className="w-6 h-6 text-yellow-400" />
          </button>
          
          {/* Mobile Logo */}
          <Link href="/dashboard" className="md:hidden flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-yellow-400 to-purple-600 flex items-center justify-center">
              <span className="text-xs font-black text-black">BP</span>
            </div>
          </Link>
        </div>

        {/* Center: Search (Desktop) */}
        <div className="hidden lg:flex flex-1 max-w-xs mx-8">
          <div className="w-full relative">
            <input
              type="text"
              placeholder="Search beats, artists..."
              className="w-full px-4 py-2 bg-muted border border-yellow-400/10 rounded-xl text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-yellow-400/50 transition-colors"
            />
            <Search className="absolute right-3 top-2.5 w-4 h-4 text-muted-foreground" />
          </div>
        </div>

        {/* Right: Actions & Profile */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="p-2 hover:bg-muted rounded-lg transition-colors relative group"
              aria-label="Notifications"
            >
              <Bell className="w-5 h-5 text-muted-foreground group-hover:text-yellow-400 transition-colors" />
              <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
            </button>

            {/* Notifications Dropdown */}
            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute right-0 mt-2 w-80 bg-card border border-yellow-400/20 rounded-xl shadow-2xl shadow-purple-600/10 overflow-hidden"
                >
                  <div className="p-4 border-b border-yellow-400/10">
                    <h3 className="font-bold text-foreground">Notifications</h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto scrollbar-hide">
                    <div className="p-4 text-center text-muted-foreground text-sm">
                      No new notifications
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Profile Menu */}
          <div className="relative">
            <button
              onClick={() => setShowProfile(!showProfile)}
              className="flex items-center gap-3 p-2 hover:bg-muted rounded-lg transition-colors group"
              aria-label="Profile menu"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-yellow-400 to-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform">
                <User className="w-4 h-4 text-black" />
              </div>
              <span className="hidden sm:block text-sm font-semibold text-foreground group-hover:text-yellow-400 transition-colors">
                {user?.full_name || user?.name || 'User'}
              </span>
            </button>

            {/* Profile Dropdown */}
            <AnimatePresence>
              {showProfile && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="absolute right-0 mt-2 w-56 bg-card border border-yellow-400/20 rounded-xl shadow-2xl shadow-purple-600/10 overflow-hidden"
                >
                  <div className="p-4 border-b border-yellow-400/10">
                    <p className="text-sm text-muted-foreground">{user?.email}</p>
                    <p className="font-semibold text-foreground capitalize">{user?.role}</p>
                  </div>
                  <div className="p-2 space-y-1">
                    <Link href="/dashboard/profile">
                      <button className="w-full text-left px-4 py-2 text-foreground hover:bg-muted rounded-lg transition-colors text-sm font-medium">
                        My Profile
                      </button>
                    </Link>
                    <Link href="/dashboard/settings">
                      <button className="w-full text-left px-4 py-2 text-foreground hover:bg-muted rounded-lg transition-colors text-sm font-medium">
                        Settings
                      </button>
                    </Link>
                    <button
                      onClick={() => {
                        // TODO: Implement logout
                        setShowProfile(false);
                      }}
                      className="w-full text-left px-4 py-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors text-sm font-medium"
                    >
                      Logout
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </header>
  );
}
