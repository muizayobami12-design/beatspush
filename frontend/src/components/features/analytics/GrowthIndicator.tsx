'use client';

import { TrendingUp, TrendingDown, Minus, ArrowUp, ArrowDown } from 'lucide-react';

interface GrowthData {
  current: number;
  previous: number;
  label: string;
}

interface GrowthIndicatorProps {
  data: GrowthData;
  format?: 'number' | 'currency' | 'percentage';
  showComparison?: boolean;
}

export function GrowthIndicator({
  data,
  format = 'number',
  showComparison = true,
}: GrowthIndicatorProps) {
  // Calculate growth percentage
  const growthPercentage = data.previous > 0
    ? ((data.current - data.previous) / data.previous) * 100
    : data.current > 0
    ? 100
    : 0;

  const isPositive = growthPercentage > 0;
  const isNeutral = growthPercentage === 0;
  const absoluteChange = data.current - data.previous;

  // Format value based on type
  const formatValue = (value: number) => {
    switch (format) {
      case 'currency':
        return new Intl.NumberFormat('en-NG', {
          style: 'currency',
          currency: 'NGN',
          minimumFractionDigits: 0,
          maximumFractionDigits: 0,
        }).format(value);
      case 'percentage':
        return `${value.toFixed(1)}%`;
      case 'number':
      default:
        if (value >= 1000000) {
          return `${(value / 1000000).toFixed(1)}M`;
        }
        if (value >= 1000) {
          return `${(value / 1000).toFixed(1)}K`;
        }
        return new Intl.NumberFormat('en-US').format(value);
    }
  };

  // Get color classes
  const getColorClasses = () => {
    if (isNeutral) {
      return {
        text: 'text-muted-foreground',
        bg: 'bg-muted',
        border: 'border-muted',
        icon: 'text-muted-foreground',
      };
    }
    if (isPositive) {
      return {
        text: 'text-green-600 dark:text-green-400',
        bg: 'bg-green-500/10',
        border: 'border-green-500/20',
        icon: 'text-green-500',
      };
    }
    return {
      text: 'text-red-600 dark:text-red-400',
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      icon: 'text-red-500',
    };
  };

  const colors = getColorClasses();

  // Get icon
  const Icon = isNeutral ? Minus : isPositive ? TrendingUp : TrendingDown;
  const ArrowIcon = isPositive ? ArrowUp : ArrowDown;

  return (
    <div className="space-y-3">
      {/* Current Value */}
      <div>
        <div className="text-3xl font-bold tracking-tight mb-1">
          {formatValue(data.current)}
        </div>
        <div className="text-sm text-muted-foreground">{data.label}</div>
      </div>

      {/* Growth Badge */}
      {showComparison && (
        <div className="flex items-center gap-2">
          <div
            className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full ${colors.bg} border ${colors.border}`}
          >
            <Icon className={`h-4 w-4 ${colors.icon}`} />
            <span className={`text-sm font-semibold ${colors.text}`}>
              {isNeutral ? '0%' : `${isPositive ? '+' : ''}${growthPercentage.toFixed(1)}%`}
            </span>
          </div>

          {/* Absolute Change */}
          {!isNeutral && (
            <div className="flex items-center gap-1 text-sm text-muted-foreground">
              <ArrowIcon className={`h-3 w-3 ${colors.icon}`} />
              <span>
                {isPositive ? '+' : ''}{formatValue(absoluteChange)}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Comparison Text */}
      {showComparison && (
        <div className="text-xs text-muted-foreground">
          {isNeutral ? (
            'No change from previous period'
          ) : (
            <>
              {isPositive ? 'Increase' : 'Decrease'} of{' '}
              <span className="font-semibold">{formatValue(Math.abs(absoluteChange))}</span>{' '}
              from previous period
            </>
          )}
        </div>
      )}
    </div>
  );
}

// Compact version for use in cards
export function GrowthBadge({
  percentage,
  compact = false,
}: {
  percentage: number;
  compact?: boolean;
}) {
  const isPositive = percentage > 0;
  const isNeutral = percentage === 0;

  const colors = isNeutral
    ? 'text-muted-foreground bg-muted'
    : isPositive
    ? 'text-green-600 dark:text-green-400 bg-green-500/10'
    : 'text-red-600 dark:text-red-400 bg-red-500/10';

  const Icon = isNeutral ? Minus : isPositive ? TrendingUp : TrendingDown;

  return (
    <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full ${colors}`}>
      <Icon className="h-3 w-3" />
      <span className={`text-xs font-semibold ${compact ? '' : ''}`}>
        {isNeutral ? '0%' : `${isPositive ? '+' : ''}${Math.abs(percentage).toFixed(1)}%`}
      </span>
    </div>
  );
}
