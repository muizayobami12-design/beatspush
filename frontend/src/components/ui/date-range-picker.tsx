'use client';

import { useState, useRef, useEffect } from 'react';
import { ChevronLeft, ChevronRight, Calendar, X } from 'lucide-react';
import { Button } from './button';
import { cn } from '@/lib/utils';

export interface DateRange {
  from: Date | null;
  to: Date | null;
}

export interface DateRangePickerProps {
  /** Selected date range */
  value: DateRange;
  /** Callback when date range changes */
  onChange: (range: DateRange) => void;
  /** Placeholder text */
  placeholder?: string;
  /** Custom className */
  className?: string;
  /** Show time picker */
  showTime?: boolean;
  /** Preset ranges */
  presets?: {
    label: string;
    getValue: () => DateRange;
  }[];
  /** Disable future dates */
  disableFuture?: boolean;
  /** Disable past dates */
  disablePast?: boolean;
}

const PRESET_RANGES = [
  {
    label: 'Last 7 days',
    getValue: () => ({
      from: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000),
      to: new Date(),
    }),
  },
  {
    label: 'Last 30 days',
    getValue: () => ({
      from: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
      to: new Date(),
    }),
  },
  {
    label: 'Last 90 days',
    getValue: () => ({
      from: new Date(Date.now() - 90 * 24 * 60 * 60 * 1000),
      to: new Date(),
    }),
  },
  {
    label: 'This month',
    getValue: () => {
      const now = new Date();
      const from = new Date(now.getFullYear(), now.getMonth(), 1);
      const to = new Date(now.getFullYear(), now.getMonth() + 1, 0);
      return { from, to };
    },
  },
  {
    label: 'Last month',
    getValue: () => {
      const now = new Date();
      const from = new Date(now.getFullYear(), now.getMonth() - 1, 1);
      const to = new Date(now.getFullYear(), now.getMonth(), 0);
      return { from, to };
    },
  },
];

/**
 * DateRangePicker - A comprehensive date range selection component
 * Includes preset ranges, calendar navigation, and time selection
 */
export function DateRangePicker({
  value,
  onChange,
  placeholder = 'Select date range',
  className,
  showTime = false,
  presets = PRESET_RANGES,
  disableFuture = false,
  disablePast = false,
}: DateRangePickerProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [month, setMonth] = useState(new Date());
  const [selectingEnd, setSelectingEnd] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  const formatDate = (date: Date | null) => {
    if (!date) return '';
    return date.toLocaleDateString('en-NG', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleDateClick = (date: Date) => {
    const now = new Date();
    now.setHours(0, 0, 0, 0);

    // Respect disable past/future
    if (disableFuture && date > now) return;
    if (disablePast && date < now) return;

    if (!value.from || (value.from && value.to)) {
      // Start new selection
      onChange({ from: date, to: null });
      setSelectingEnd(false);
    } else {
      // Complete selection
      if (date < value.from) {
        onChange({ from: date, to: value.from });
      } else {
        onChange({ from: value.from, to: date });
      }
      setSelectingEnd(true);
      setTimeout(() => setIsOpen(false), 200);
    }
  };

  const handlePreset = (range: DateRange) => {
    onChange(range);
    setSelectingEnd(true);
    setTimeout(() => setIsOpen(false), 200);
  };

  const getDaysInMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0).getDate();
  };

  const getFirstDayOfMonth = (date: Date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1).getDay();
  };

  const renderCalendar = () => {
    const daysInMonth = getDaysInMonth(month);
    const firstDay = getFirstDayOfMonth(month);
    const days = [];
    const now = new Date();
    now.setHours(0, 0, 0, 0);

    // Empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
      days.push(<div key={`empty-${i}`} className="h-10" />);
    }

    // Days of month
    for (let day = 1; day <= daysInMonth; day++) {
      const date = new Date(month.getFullYear(), month.getMonth(), day);
      const isDisabled =
        (disableFuture && date > now) || (disablePast && date < now);
      const isSelected =
        (value.from && date.toDateString() === value.from.toDateString()) ||
        (value.to && date.toDateString() === value.to.toDateString());
      const isInRange =
        value.from &&
        value.to &&
        date > value.from &&
        date < value.to;

      days.push(
        <button
          key={day}
          onClick={() => handleDateClick(date)}
          disabled={isDisabled}
          className={cn(
            'h-10 rounded-lg text-sm font-label-sm transition-all duration-200',
            isDisabled
              ? 'text-on-surface-variant/30 cursor-not-allowed'
              : 'text-on-surface hover:bg-surface-container',
            isSelected && 'bg-secondary text-on-secondary hover:bg-secondary-fixed',
            isInRange && 'bg-secondary/20'
          )}
        >
          {day}
        </button>
      );
    }

    return days;
  };

  const displayValue =
    value.from && value.to
      ? `${formatDate(value.from)} - ${formatDate(value.to)}`
      : value.from
      ? formatDate(value.from)
      : placeholder;

  return (
    <div ref={containerRef} className={cn('relative w-full', className)}>
      {/* Input Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'w-full px-3 py-2 rounded-lg',
          'bg-surface-container-low border border-outline-variant/30',
          'text-on-surface placeholder-on-surface-variant/50',
          'focus:outline-none focus:ring-2 focus:ring-secondary/40',
          'flex items-center justify-between gap-2',
          'transition-all duration-200',
          isOpen && 'ring-2 ring-secondary/40'
        )}
      >
        <span className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-on-surface-variant" />
          <span className="truncate text-sm font-body-md">{displayValue}</span>
        </span>
        {value.from && value.to && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onChange({ from: null, to: null });
            }}
            className="text-on-surface-variant hover:text-on-surface transition-colors"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div
          className={cn(
            'absolute z-50 mt-2 rounded-lg border ghost-border',
            'bg-surface-container-low p-4 shadow-lg',
            'w-full md:w-96'
          )}
        >
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Presets */}
            <div className="space-y-2">
              <p className={cn(
                'font-label-sm text-label-sm',
                'text-on-surface-variant uppercase tracking-wider mb-2'
              )}>
                Quick Select
              </p>
              {presets.map((preset) => (
                <button
                  key={preset.label}
                  onClick={() => handlePreset(preset.getValue())}
                  className={cn(
                    'w-full px-3 py-2 rounded-lg text-sm',
                    'font-body-md text-left transition-colors',
                    'text-on-surface hover:bg-surface-container',
                    'border border-transparent hover:border-outline-variant/30'
                  )}
                >
                  {preset.label}
                </button>
              ))}
            </div>

            {/* Calendar */}
            <div className="md:col-span-2 space-y-4">
              {/* Month Navigation */}
              <div className="flex items-center justify-between">
                <button
                  onClick={() =>
                    setMonth(
                      new Date(month.getFullYear(), month.getMonth() - 1)
                    )
                  }
                  className="p-1 hover:bg-surface-container rounded transition-colors"
                >
                  <ChevronLeft className="h-4 w-4 text-on-surface" />
                </button>

                <h3 className={cn(
                  'font-headline-md text-headline-md',
                  'text-on-surface'
                )}>
                  {month.toLocaleDateString('en-NG', {
                    month: 'long',
                    year: 'numeric',
                  })}
                </h3>

                <button
                  onClick={() =>
                    setMonth(
                      new Date(month.getFullYear(), month.getMonth() + 1)
                    )
                  }
                  className="p-1 hover:bg-surface-container rounded transition-colors"
                >
                  <ChevronRight className="h-4 w-4 text-on-surface" />
                </button>
              </div>

              {/* Weekday Headers */}
              <div className="grid grid-cols-7 gap-2 mb-2">
                {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(
                  (day) => (
                    <div
                      key={day}
                      className={cn(
                        'h-8 flex items-center justify-center',
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant'
                      )}
                    >
                      {day}
                    </div>
                  )
                )}
              </div>

              {/* Calendar Days */}
              <div className="grid grid-cols-7 gap-2">
                {renderCalendar()}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 mt-4 pt-4 border-t border-outline-variant/20">
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setIsOpen(false);
                onChange({ from: null, to: null });
              }}
              className="flex-1"
            >
              Clear
            </Button>
            <Button
              size="sm"
              onClick={() => setIsOpen(false)}
              className="flex-1 bg-secondary text-on-secondary hover:bg-secondary-fixed"
              disabled={!value.from || !value.to}
            >
              Apply
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}

export default DateRangePicker;
