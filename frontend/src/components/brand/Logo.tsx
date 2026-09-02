'use client';

import { Music } from 'lucide-react';
import Link from 'next/link';
import { motion } from 'framer-motion';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

export default function Logo({ size = 'md', showText = true, className = '' }: LogoProps) {
  const sizes = {
    sm: { icon: 'h-6 w-6', text: 'text-lg', container: 'gap-2' },
    md: { icon: 'h-8 w-8', text: 'text-2xl', container: 'gap-2' },
    lg: { icon: 'h-12 w-12', text: 'text-4xl', container: 'gap-3' },
  };

  const current = sizes[size];

  return (
    <Link href="/" className={`inline-flex items-center ${current.container} ${className}`}>
      {/* Animated Icon */}
      <motion.div
        className="relative"
        whileHover={{ scale: 1.1, rotate: [0, -10, 10, 0] }}
        transition={{ duration: 0.5 }}
      >
        {/* Gradient background with pulse */}
        <motion.div
          className={`${current.icon} rounded-xl bg-gradient-to-br from-pink-500 via-purple-500 to-cyan-500 flex items-center justify-center shadow-lg`}
          animate={{
            boxShadow: [
              '0 0 20px rgba(236, 72, 153, 0.3)',
              '0 0 40px rgba(168, 85, 247, 0.5)',
              '0 0 20px rgba(236, 72, 153, 0.3)',
            ],
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <Music className={`${current.icon === 'h-6 w-6' ? 'h-4 w-4' : current.icon === 'h-8 w-8' ? 'h-5 w-5' : 'h-7 w-7'} text-white`} strokeWidth={2.5} />
        </motion.div>

        {/* Glow effect */}
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-pink-500 via-purple-500 to-cyan-500 blur-md opacity-30 -z-10" />
      </motion.div>

      {/* Text Logo */}
      {showText && (
        <div className="flex flex-col leading-none">
          <span className={`${current.text} font-black tracking-tight bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 bg-clip-text text-transparent`}>
            Beat<span className="text-white">Push</span>
          </span>
          {size === 'lg' && (
            <span className="text-xs text-gray-400 font-medium tracking-wider mt-1">
              MUSIC PLATFORM
            </span>
          )}
        </div>
      )}
    </Link>
  );
}
