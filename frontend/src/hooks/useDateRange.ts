import { useState, useCallback } from 'react';

export interface DateRange {
  from: Date | null;
  to: Date | null;
}

export interface UseDateRangeOptions {
  /** Initial date range */
  initialRange?: DateRange;
  /** Callback when range changes */
  onChange?: (range: DateRange) => void;
}

export interface UseDateRangeReturn {
  /** Current date range */
  range: DateRange;
  /** Set date range */
  setRange: (range: DateRange) => void;
  /** Get number of days in range */
  getDaysCount: () => number;
  /** Format range as string */
  formatRange: () => string;
  /** Set preset range (last N days) */
  setLastNDays: (days: number) => void;
  /** Set preset range (this month) */
  setThisMonth: () => void;
  /** Set preset range (last month) */
  setLastMonth: () => void;
  /** Clear range */
  clear: () => void;
  /** Check if range is valid */
  isValid: () => boolean;
  /** Check if date is in range */
  isInRange: (date: Date) => boolean;
}

/**
 * Hook for managing date range state
 * Provides utilities for common date range operations
 */
export function useDateRange({
  initialRange = { from: null, to: null },
  onChange,
}: UseDateRangeOptions = {}): UseDateRangeReturn {
  const [range, setRange] = useState<DateRange>(initialRange);

  const handleSetRange = useCallback(
    (newRange: DateRange) => {
      setRange(newRange);
      if (onChange) {
        onChange(newRange);
      }
    },
    [onChange]
  );

  const getDaysCount = useCallback(() => {
    if (!range.from || !range.to) {
      return 0;
    }

    const diffTime = Math.abs(range.to.getTime() - range.from.getTime());
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  }, [range]);

  const formatRange = useCallback(() => {
    if (!range.from || !range.to) {
      return '';
    }

    const formatDate = (date: Date) =>
      date.toLocaleDateString('en-NG', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });

    return `${formatDate(range.from)} - ${formatDate(range.to)}`;
  }, [range]);

  const setLastNDays = useCallback(
    (days: number) => {
      const to = new Date();
      const from = new Date();
      from.setDate(from.getDate() - days);

      handleSetRange({ from, to });
    },
    [handleSetRange]
  );

  const setThisMonth = useCallback(() => {
    const now = new Date();
    const from = new Date(now.getFullYear(), now.getMonth(), 1);
    const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);

    handleSetRange({ from, to });
  }, [handleSetRange]);

  const setLastMonth = useCallback(() => {
    const now = new Date();
    const from = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const to = new Date(now.getFullYear(), now.getMonth(), 0);

    handleSetRange({ from, to });
  }, [handleSetRange]);

  const clear = useCallback(() => {
    handleSetRange({ from: null, to: null });
  }, [handleSetRange]);

  const isValid = useCallback(() => {
    return range.from !== null && range.to !== null && range.from <= range.to;
  }, [range]);

  const isInRange = useCallback(
    (date: Date) => {
      if (!range.from || !range.to) {
        return false;
      }

      return date >= range.from && date <= range.to;
    },
    [range]
  );

  return {
    range,
    setRange: handleSetRange,
    getDaysCount,
    formatRange,
    setLastNDays,
    setThisMonth,
    setLastMonth,
    clear,
    isValid,
    isInRange,
  };
}
