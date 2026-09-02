'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Music, 
  MessageSquare, 
  User, 
  BarChart3, 
  Settings,
  Menu,
  X,
  LogOut,
  Rss,
  Shield,
  ShoppingCart,
  Radio,
  Mic2,
  Users,
  Sparkles,
  MessageCircle,
  TrendingUp,
  Calendar,
  Heart,
  Bell,
  Link2,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { GlobalSearchBar } from '@/components/features/search/GlobalSearchBar';
import { useAuthStore } from '@/store/authStore';
import { useCartStore } from '@/store/cartStore';
import { cn } from '@/lib/utils';
import NotificationBell from '@/components/features/notifications/NotificationBell';
import { ChatTriggerButton } from '@/components/chat';

const navigation = [
  { name: 'Home', href: '/dashboard', icon: Home, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: true },
  { name: 'AI Publish', href: '/ai-publish', icon: Sparkles, roles: ['artist', 'producer', 'dj'], featured: true, desktop: true },
  { name: 'Discover', href: '/discover', icon: Sparkles, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: true },
  { name: 'Trending', href: '/trending', icon: TrendingUp, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: true },
  { name: 'Campaigns', href: '/campaigns', icon: MessageCircle, roles: ['artist', 'producer', 'dj'], desktop: true },
  { name: 'Bookings', href: '/bookings', icon: Calendar, roles: ['artist', 'producer', 'dj'], desktop: true },
  { name: 'Tips', href: '/tips', icon: Heart, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: true },
  { name: 'Notifications', href: '/notifications', icon: Bell, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: true },
  { name: 'Promo Links', href: '/promo-links', icon: Link2, roles: ['artist', 'dj', 'producer'], desktop: true },
  { name: 'Feed', href: '/feed', icon: Rss, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: false },
  { name: 'Beats', href: '/beats', icon: Music, roles: ['artist', 'producer', 'fan', 'admin'], desktop: true },
  { name: 'Tracks', href: '/tracks', icon: Mic2, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: false },
  { name: 'DJs', href: '/djs', icon: Radio, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: false },
  { name: 'Fan Clubs', href: '/fan-clubs', icon: Users, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: false },
  { name: 'Messages', href: '/messages', icon: MessageSquare, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: true },
  { name: 'Analytics', href: '/analytics', icon: BarChart3, roles: ['artist', 'dj', 'producer', 'admin'], desktop: true },
  { name: 'Profile', href: '/profile', icon: User, roles: ['artist', 'dj', 'producer', 'fan', 'admin'], desktop: false },
];

const adminNavigation = [
  { name: 'Admin', href: '/admin', icon: Shield },
];

export function MainNav() {
  const pathname = usePathname();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const { getItemCount } = useCartStore();
  const cartItemCount = getItemCount();

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
  };

  return (
    <nav className="sticky top-0 z-50 w-full backdrop-blur-lg bg-background/80 border-b border-border shadow-sm dark:bg-card/80 dark:border-border/40">
      <div className="mx-auto px-4 max-w-[100vw]">
        <div className="flex h-16 items-center justify-between gap-2 md:gap-4">
          {/* Logo */}
          <Link href="/dashboard" className="flex items-center space-x-2 group flex-shrink-0">
            <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 via-cyan-400 to-purple-500 shadow-lg group-hover:scale-110 transition-transform">
              <Music className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-black bg-gradient-to-r from-emerald-500 via-cyan-500 to-purple-600 bg-clip-text text-transparent hidden lg:inline">
              BeatPush
            </span>
          </Link>

          {/* Search Bar - Desktop Only */}
          <div className="hidden md:block flex-1 max-w-md">
            <GlobalSearchBar placeholder="Search beats, artists..." />
          </div>

          {/* Desktop Navigation */}
          <div className="hidden lg:flex items-center space-x-1 flex-shrink-0">
            {navigation
              .filter(item => item.desktop && (!user?.role || item.roles.includes(user.role)))
              .map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap',
                    isActive
                      ? 'bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                      : 'text-foreground/70 hover:bg-muted hover:text-foreground'
                  )}
                >
                  <item.icon className="h-4 w-4 flex-shrink-0" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
            {/* Admin Link */}
            {user?.role === 'admin' && adminNavigation.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'flex items-center space-x-2 px-3 py-2 rounded-lg text-sm font-medium transition-all whitespace-nowrap',
                    isActive
                      ? 'bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30'
                      : 'text-foreground/70 hover:bg-muted hover:text-foreground'
                  )}
                >
                  <item.icon className="h-4 w-4 flex-shrink-0" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
          </div>

          {/* Right Section */}
          <div className="flex items-center gap-1 md:gap-2 flex-shrink-0">
            {/* AI Chat Trigger */}
            <ChatTriggerButton />

            {/* Cart */}
            <Link href="/cart" className="flex-shrink-0">
              <Button variant="ghost" size="icon" className="relative rounded-full hover:bg-muted h-10 w-10">
                <ShoppingCart className="h-5 w-5" />
                {cartItemCount > 0 && (
                  <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-gradient-to-r from-emerald-500 to-cyan-600 text-white text-xs font-bold flex items-center justify-center">
                    {cartItemCount}
                  </span>
                )}
                <span className="sr-only">Shopping Cart ({cartItemCount})</span>
              </Button>
            </Link>

            {/* Notifications */}
            <div className="flex-shrink-0">
              <NotificationBell />
            </div>

            {/* Settings - Goes to Settings page for theme toggle */}
            <Link href="/settings" className="flex-shrink-0">
              <Button variant="ghost" size="icon" className="rounded-full hover:bg-muted h-10 w-10">
                <Settings className="h-5 w-5" />
                <span className="sr-only">Settings</span>
              </Button>
            </Link>

            {/* User Menu - Desktop */}
            <div className="hidden md:flex items-center space-x-3 pl-3 ml-3 border-l border-border">
              <div className="flex items-center space-x-2">
                <div className="w-9 h-9 rounded-full bg-gradient-to-br from-emerald-400 via-cyan-400 to-purple-500 flex items-center justify-center text-white text-sm font-bold shadow-lg">
                  {user?.fullName?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div className="hidden lg:block">
                  <p className="text-sm font-semibold text-foreground">{user?.fullName}</p>
                  <p className="text-xs text-muted-foreground capitalize">{user?.role}</p>
                </div>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={handleLogout}
                className="rounded-full hover:bg-muted"
                title="Logout"
              >
                <LogOut className="h-4 w-4" />
              </Button>
            </div>

            {/* Mobile Menu Button */}
            <Button
              variant="ghost"
              size="icon"
              className="md:hidden rounded-full hover:bg-muted"
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              {isMobileMenuOpen ? (
                <X className="h-5 w-5" />
              ) : (
                <Menu className="h-5 w-5" />
              )}
              <span className="sr-only">Toggle menu</span>
            </Button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMobileMenuOpen && (
          <div className="md:hidden py-4 space-y-1 border-t border-border">
            {navigation
              .filter(item => !user?.role || item.roles.includes(user.role))
              .map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={cn(
                    'flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium transition-all',
                    isActive
                      ? 'bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 text-emerald-600 dark:text-emerald-400'
                      : 'text-foreground/70 hover:bg-muted hover:text-foreground'
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
            
            {/* Admin Link (mobile) */}
            {user?.role === 'admin' && adminNavigation.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(`${item.href}/`);
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  onClick={() => setIsMobileMenuOpen(false)}
                  className={cn(
                    'flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium transition-all',
                    isActive
                      ? 'bg-gradient-to-r from-emerald-500/10 to-cyan-500/10 text-emerald-600 dark:text-emerald-400'
                      : 'text-foreground/70 hover:bg-muted hover:text-foreground'
                  )}
                >
                  <item.icon className="h-5 w-5" />
                  <span>{item.name}</span>
                </Link>
              );
            })}
            
            <div className="pt-4 mt-4 border-t border-border space-y-1">
              <Link
                href="/settings"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium text-foreground/70 hover:bg-muted hover:text-foreground"
              >
                <Settings className="h-5 w-5" />
                <span>Settings</span>
              </Link>
              
              <button
                onClick={() => {
                  setIsMobileMenuOpen(false);
                  handleLogout();
                }}
                className="w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-base font-medium text-foreground/70 hover:bg-muted hover:text-foreground"
              >
                <LogOut className="h-5 w-5" />
                <span>Logout</span>
              </button>
            </div>

            {/* Mobile User Info */}
            <div className="pt-4 mt-4 border-t border-border px-4">
              <div className="flex items-center space-x-3">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-emerald-400 via-cyan-400 to-purple-500 flex items-center justify-center text-white font-bold shadow-lg">
                  {user?.fullName?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <div>
                  <p className="text-sm font-semibold text-foreground">{user?.fullName}</p>
                  <p className="text-xs text-muted-foreground">{user?.email}</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
