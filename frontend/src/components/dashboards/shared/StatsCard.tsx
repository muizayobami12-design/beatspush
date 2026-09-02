'use client';

import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  change?: {
    value: number;
    isPositive: boolean;
  };
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
}

export function StatsCard({
  icon: Icon,
  label,
  value,
  change,
  trend,
  className = '',
}: StatsCardProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.05, y: -5 }}
      className={`bg-card border border-yellow-400/20 rounded-2xl p-6 backdrop-blur-sm transition-all duration-300 hover:border-yellow-400/40 hover:shadow-2xl hover:shadow-yellow-400/20 ${className}`}
    >
      {/* Icon */}
      <div className="flex items-center justify-between mb-4">
        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-yellow-400/20 to-purple-600/20 flex items-center justify-center">
          <Icon className="w-6 h-6 text-yellow-400" />
        </div>
        {change && (
          <div
            className={`text-sm font-bold flex items-center gap-1 ${
              change.isPositive ? 'text-green-400' : 'text-red-400'
            }`}
          >
            {change.isPositive ? '↑' : '↓'} {Math.abs(change.value)}%
          </div>
        )}
      </div>

      {/* Label */}
      <p className="text-muted-foreground text-sm font-medium mb-2">{label}</p>

      {/* Value */}
      <p className="text-2xl md:text-3xl font-black text-gradient-neon">{value}</p>
    </motion.div>
  );
}
