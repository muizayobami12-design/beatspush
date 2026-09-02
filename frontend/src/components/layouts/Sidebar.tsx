'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Home,
  Music,
  Compass,
  TrendingUp,
  Megaphone,
  Calendar,
  MessageSquare,
  DollarSign,
  Share2,
  Zap,
  BarChart3,
  User,
  Settings,
  LogOut,
  ChevronRight,
} from 'lucide-react';

const navItems = [
  { name: 'Home', href: '/dashboard', icon: Home },
  { name: 'Beats', href: '/dashboard/beats', icon: Music },
  { name: 'Discover', href: '/dashboard/discover', icon: Compass },
  { name: 'Trending', href: '/dashboard/trending', icon: TrendingUp },
  { name: 'Campaigns', href: '/dashboard/campaigns', icon: Megaphone },
  { name: 'Bookings', href: '/dashboard/bookings', icon: Calendar },
  { name: 'Messages', href: '/dashboard/messages', icon: MessageSquare },
  { name: 'Tips', href: '/dashboard/tips', icon: DollarSign },
  { name: 'Promo Links', href: '/dashboard/promo-links', icon: Share2 },
  { name: 'Free Tools', href: '/dashboard/free-tools', icon: Zap },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
];

const bottomItems = [
  { name: 'Profile', href: '/dashboard/profile', icon: User },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

interface SidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ isOpen = true, onClose }: SidebarProps) {
  const pathname = usePathname();

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <>
      {/* Desktop Sidebar */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.3 }}
        className="hidden md:flex fixed left-0 top-0 w-72 h-screen bg-gradient-to-b from-background via-background to-background/80 border-r border-yellow-400/20 flex-col backdrop-blur-sm z-40"
      >
        {/* Logo */}
        <div className="px-6 py-8 border-b border-yellow-400/20">
          <Link href="/dashboard" className="flex items-center gap-3 group">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-purple-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
              <Music className="w-6 h-6 text-black" />
            </div>
            <div>
              <h1 className="text-xl font-black text-yellow-400 group-hover:text-yellow-300 transition-colors">
                BeatPush
              </h1>
              <p className="text-xs text-muted-foreground group-hover:text-purple-400 transition-colors">
                Music Platform
              </p>
            </div>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-2 scrollbar-hide">
          {navItems.map((item, index) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <motion.div key={item.href} initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.03 }}>
                <Link href={item.href}>
                  <div
                    className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group relative overflow-hidden ${
                      active
                        ? 'bg-gradient-to-r from-yellow-400/20 to-purple-600/20 border border-yellow-400/30'
                        : 'hover:bg-muted border border-transparent hover:border-yellow-400/10'
                    }`}
                  >
                    {/* Glow effect for active */}
                    {active && (
                      <motion.div
                        layoutId="active-nav"
                        className="absolute inset-0 bg-gradient-to-r from-yellow-400/10 to-purple-600/10 rounded-xl -z-10"
                        transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                      />
                    )}

                    {/* Icon */}
                    <div
                      className={`flex-shrink-0 transition-all duration-300 ${
                        active ? 'text-yellow-400 scale-110' : 'text-muted-foreground group-hover:text-yellow-400'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                    </div>

                    {/* Label */}
                    <span
                      className={`flex-1 font-semibold text-sm transition-colors duration-300 ${
                        active ? 'text-yellow-400' : 'text-foreground group-hover:text-yellow-400'
                      }`}
                    >
                      {item.name}
                    </span>

                    {/* Active indicator */}
                    {active && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 30 }}
                        className="text-purple-400"
                      >
                        <ChevronRight className="w-4 h-4" />
                      </motion.div>
                    )}
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </nav>

        {/* Bottom Navigation */}
        <div className="px-4 py-6 border-t border-yellow-400/20 space-y-2">
          {bottomItems.map((item, index) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link key={item.href} href={item.href}>
                <div
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 group ${
                    active
                      ? 'bg-gradient-to-r from-yellow-400/20 to-purple-600/20 border border-yellow-400/30'
                      : 'hover:bg-muted border border-transparent hover:border-yellow-400/10'
                  }`}
                >
                  <Icon
                    className={`w-5 h-5 transition-colors duration-300 ${
                      active ? 'text-yellow-400' : 'text-muted-foreground group-hover:text-yellow-400'
                    }`}
                  />
                  <span
                    className={`font-semibold text-sm transition-colors duration-300 ${
                      active ? 'text-yellow-400' : 'text-foreground group-hover:text-yellow-400'
                    }`}
                  >
                    {item.name}
                  </span>
                </div>
              </Link>
            );
          })}

          {/* Logout Button */}
          <button
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 hover:border-red-500/40 transition-all duration-300 font-semibold text-sm group mt-4"
            onClick={() => {
              // TODO: Implement logout
              console.log('Logout clicked');
            }}
          >
            <LogOut className="w-5 h-5 group-hover:scale-110 transition-transform" />
            <span>Logout</span>
          </button>
        </div>
      </motion.aside>

      {/* Mobile Sidebar Overlay */}
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          className="fixed inset-0 bg-black/50 md:hidden z-30"
        />
      )}

      {/* Mobile Sidebar */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: isOpen ? 0 : -280 }}
        transition={{ duration: 0.3 }}
        className="fixed left-0 top-0 w-72 h-screen bg-background border-r border-yellow-400/20 flex flex-col md:hidden z-40"
      >
        {/* Logo */}
        <div className="px-6 py-8 border-b border-yellow-400/20">
          <Link href="/dashboard" className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400 to-purple-600 flex items-center justify-center">
              <Music className="w-6 h-6 text-black" />
            </div>
            <div>
              <h1 className="text-xl font-black text-yellow-400">BeatPush</h1>
              <p className="text-xs text-muted-foreground">Music Platform</p>
            </div>
          </Link>
        </div>

        {/* Main Navigation */}
        <nav className="flex-1 overflow-y-auto px-4 py-6 space-y-2 scrollbar-hide">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link key={item.href} href={item.href} onClick={onClose}>
                <div
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                    active
                      ? 'bg-gradient-to-r from-yellow-400/20 to-purple-600/20 border border-yellow-400/30 text-yellow-400'
                      : 'text-foreground hover:bg-muted'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-semibold text-sm">{item.name}</span>
                </div>
              </Link>
            );
          })}
        </nav>

        {/* Bottom Navigation */}
        <div className="px-4 py-6 border-t border-yellow-400/20 space-y-2">
          {bottomItems.map((item) => {
            const Icon = item.icon;
            const active = isActive(item.href);

            return (
              <Link key={item.href} href={item.href} onClick={onClose}>
                <div
                  className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${
                    active
                      ? 'bg-gradient-to-r from-yellow-400/20 to-purple-600/20 border border-yellow-400/30 text-yellow-400'
                      : 'text-foreground hover:bg-muted'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-semibold text-sm">{item.name}</span>
                </div>
              </Link>
            );
          })}

          {/* Logout Button */}
          <button
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20 transition-all duration-300 font-semibold text-sm mt-4"
            onClick={() => {
              onClose?.();
              // TODO: Implement logout
            }}
          >
            <LogOut className="w-5 h-5" />
            <span>Logout</span>
          </button>
        </div>
      </motion.aside>
    </>
  );
}
