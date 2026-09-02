'use client';

import { DollarSign, TrendingUp, TrendingDown, Music, Heart, Users, Briefcase } from 'lucide-react';
import { useMemo } from 'react';

interface RevenueSource {
  label: string;
  amount: number;
  percentage: number;
  icon: any;
  color: string;
}

interface RevenueBreakdownProps {
  totalRevenue: number;
  revenueBySource: {
    beatSales: number;
    tips: number;
    subscriptions: number;
    djSubmissions: number;
    premiumMixes: number;
  };
  growth: number; // percentage change from last period
  period?: string; // 'week' | 'month'
}

export function RevenueBreakdownCard({
  totalRevenue,
  revenueBySource,
  growth,
  period = 'month',
}: RevenueBreakdownProps) {
  // Calculate revenue sources with percentages
  const sources: RevenueSource[] = useMemo(() => {
    const total = totalRevenue || 1; // Prevent division by zero
    
    return [
      {
        label: 'Beat Sales',
        amount: revenueBySource.beatSales,
        percentage: (revenueBySource.beatSales / total) * 100,
        icon: Music,
        color: 'from-purple-500 to-pink-500',
      },
      {
        label: 'Tips Received',
        amount: revenueBySource.tips,
        percentage: (revenueBySource.tips / total) * 100,
        icon: Heart,
        color: 'from-pink-500 to-rose-500',
      },
      {
        label: 'Subscriptions',
        amount: revenueBySource.subscriptions,
        percentage: (revenueBySource.subscriptions / total) * 100,
        icon: Users,
        color: 'from-cyan-500 to-blue-500',
      },
      {
        label: 'DJ Submissions',
        amount: revenueBySource.djSubmissions,
        percentage: (revenueBySource.djSubmissions / total) * 100,
        icon: Briefcase,
        color: 'from-orange-500 to-amber-500',
      },
      {
        label: 'Premium Mixes',
        amount: revenueBySource.premiumMixes,
        percentage: (revenueBySource.premiumMixes / total) * 100,
        icon: Music,
        color: 'from-green-500 to-emerald-500',
      },
    ].sort((a, b) => b.amount - a.amount); // Sort by highest revenue
  }, [totalRevenue, revenueBySource]);

  // Format currency in Naira
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const isPositiveGrowth = growth >= 0;

  return (
    <div className="bg-card rounded-xl border p-6 space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-lg font-semibold mb-1">Revenue Breakdown</h3>
          <p className="text-sm text-muted-foreground">
            Your earnings by source this {period}
          </p>
        </div>
        <div className="p-3 rounded-lg bg-gradient-to-br from-purple-500 to-pink-500">
          <DollarSign className="h-6 w-6 text-white" />
        </div>
      </div>

      {/* Total Revenue */}
      <div className="space-y-2">
        <div className="flex items-baseline gap-3">
          <span className="text-4xl font-bold tracking-tight">
            {formatCurrency(totalRevenue)}
          </span>
          <div className={`flex items-center gap-1 text-sm font-medium ${
            isPositiveGrowth ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'
          }`}>
            {isPositiveGrowth ? (
              <TrendingUp className="h-4 w-4" />
            ) : (
              <TrendingDown className="h-4 w-4" />
            )}
            {Math.abs(growth)}%
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          {isPositiveGrowth ? 'Increase' : 'Decrease'} from last {period}
        </p>
      </div>

      {/* Revenue Sources */}
      <div className="space-y-4">
        {sources.map((source) => {
          const Icon = source.icon;
          
          return (
            <div key={source.label} className="space-y-2">
              {/* Source Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`p-2 rounded-lg bg-gradient-to-br ${source.color}`}>
                    <Icon className="h-4 w-4 text-white" />
                  </div>
                  <span className="text-sm font-medium">{source.label}</span>
                </div>
                <div className="text-right">
                  <div className="text-sm font-semibold">
                    {formatCurrency(source.amount)}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {source.percentage.toFixed(1)}%
                  </div>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="relative w-full h-2 bg-muted rounded-full overflow-hidden">
                <div
                  className={`absolute top-0 left-0 h-full bg-gradient-to-r ${source.color} transition-all duration-500 ease-out`}
                  style={{ width: `${source.percentage}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Platform Fee Notice */}
      <div className="pt-4 border-t">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">Platform Fee (15%)</span>
          <span className="font-medium text-muted-foreground">
            -{formatCurrency(totalRevenue * 0.15)}
          </span>
        </div>
        <div className="flex items-center justify-between text-sm mt-2">
          <span className="font-semibold">Your Net Earnings</span>
          <span className="font-bold text-lg">
            {formatCurrency(totalRevenue * 0.85)}
          </span>
        </div>
      </div>
    </div>
  );
}
