'use client';

import { motion } from 'framer-motion';

interface EarningItem {
  label: string;
  amount: number;
  percentage?: number;
  icon?: string;
}

interface EarningsBreakdownProps {
  title: string;
  total: number;
  currency?: string;
  items: EarningItem[];
  change?: number;
}

export function EarningsBreakdown({
  title,
  total,
  currency = '$',
  items,
  change,
}: EarningsBreakdownProps) {
  const maxAmount = Math.max(...items.map((i) => i.amount));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-card border border-yellow-400/20 rounded-2xl p-6 backdrop-blur-sm"
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <p className="text-muted-foreground text-sm font-medium mb-2">{title}</p>
          <h3 className="text-3xl md:text-4xl font-black text-gradient-neon">
            {currency}{total.toLocaleString()}
          </h3>
          {change !== undefined && (
            <p className={`text-sm mt-2 ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {change >= 0 ? '↑' : '↓'} {Math.abs(change)}% from last month
            </p>
          )}
        </div>
      </div>

      {/* Breakdown Items */}
      <div className="space-y-4">
        {items.map((item, index) => (
          <motion.div
            key={item.label}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="space-y-2"
          >
            {/* Label & Amount */}
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-foreground flex items-center gap-2">
                {item.icon && <span className="text-lg">{item.icon}</span>}
                {item.label}
              </span>
              <span className="text-sm font-bold text-yellow-400">
                {currency}{item.amount.toLocaleString()}
              </span>
            </div>

            {/* Progress bar */}
            <div className="w-full h-2 bg-muted/50 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(item.amount / maxAmount) * 100}%` }}
                transition={{ delay: 0.3 + index * 0.1, duration: 0.6 }}
                className="h-full bg-gradient-to-r from-yellow-400 to-purple-600 rounded-full"
              />
            </div>

            {/* Percentage */}
            {item.percentage && (
              <p className="text-xs text-muted-foreground">{item.percentage}% of total</p>
            )}
          </motion.div>
        ))}
      </div>
    </motion.div>
  );
}
