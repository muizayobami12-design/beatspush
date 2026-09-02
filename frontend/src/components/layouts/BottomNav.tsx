'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { motion } from 'framer-motion';
import {
  Home,
  Compass,
  Plus,
  MessageSquare,
  User,
} from 'lucide-react';

const navItems = [
  { name: 'Home', href: '/dashboard', icon: Home },
  { name: 'Discover', href: '/dashboard/discover', icon: Compass },
  { name: 'Upload', href: '/dashboard/beats/new', icon: Plus, primary: true },
  { name: 'Messages', href: '/dashboard/messages', icon: MessageSquare },
  { name: 'Profile', href: '/dashboard/profile', icon: User },
];

export default function BottomNav() {
  const pathname = usePathname();

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-gradient-to-t from-background via-background to-background/80 border-t border-yellow-400/20 backdrop-blur-sm z-20">
      <div className="flex items-center justify-around px-4 py-3">
        {navItems.map((item, index) => {
          const Icon = item.icon;
          const active = isActive(item.href);

          return (
            <motion.div
              key={item.href}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05 }}
            >
              <Link href={item.href}>
                <div
                  className={`relative flex flex-col items-center justify-center py-2 px-3 rounded-xl transition-all duration-300 group ${
                    item.primary
                      ? 'bg-gradient-to-br from-yellow-400 to-purple-600 text-black shadow-lg shadow-yellow-400/30 hover:shadow-xl hover:shadow-yellow-400/50'
                      : active
                      ? 'text-yellow-400'
                      : 'text-muted-foreground hover:text-yellow-400'
                  }`}
                >
                  {/* Glow effect for active non-primary */}
                  {active && !item.primary && (
                    <motion.div
                      layoutId="active-bottom-nav"
                      className="absolute inset-0 bg-gradient-to-t from-yellow-400/20 to-transparent rounded-xl -z-10"
                      transition={{ type: 'spring', stiffness: 300, damping: 30 }}
                    />
                  )}

                  <Icon className={`w-6 h-6 transition-transform duration-300 ${item.primary ? '' : 'group-hover:scale-110'}`} />
                  <span className={`text-xs font-bold mt-1 transition-colors duration-300 ${item.primary ? 'text-black' : ''}`}>
                    {item.name}
                  </span>
                </div>
              </Link>
            </motion.div>
          );
        })}
      </div>

      {/* Safe area spacer for notch/home indicator */}
      <div className="pb-2" />
    </nav>
  );
}
