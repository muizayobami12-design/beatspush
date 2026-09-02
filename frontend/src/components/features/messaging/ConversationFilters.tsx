'use client';

import React from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

export type FilterType = 'all' | 'unread' | 'requests' | 'archived';

interface ConversationFiltersProps {
  activeFilter: FilterType;
  onFilterChange: (filter: FilterType) => void;
  unreadCount?: number;
  requestCount?: number;
  className?: string;
}

const FILTER_OPTIONS: Array<{
  id: FilterType;
  label: string;
  icon?: React.ReactNode;
}> = [
  { id: 'all', label: 'All' },
  { id: 'unread', label: 'Unread' },
  { id: 'requests', label: 'Requests' },
  { id: 'archived', label: 'Archived' },
];

/**
 * ConversationFilters — filter chips for conversation list.
 * Supports: All, Unread, Message Requests, Archived
 * Requirements: 8.3, 8.4, 5.2
 */
export function ConversationFilters({
  activeFilter,
  onFilterChange,
  unreadCount = 0,
  requestCount = 0,
  className,
}: ConversationFiltersProps) {
  return (
    <div className={cn('flex gap-2 overflow-x-auto pb-2', className)}>
      {FILTER_OPTIONS.map((filter) => {
        const isActive = activeFilter === filter.id;
        let badgeCount: number | undefined;

        if (filter.id === 'unread') {
          badgeCount = unreadCount;
        } else if (filter.id === 'requests') {
          badgeCount = requestCount;
        }

        return (
          <Button
            key={filter.id}
            variant={isActive ? 'default' : 'outline'}
            size="sm"
            onClick={() => onFilterChange(filter.id)}
            className="flex items-center gap-2 whitespace-nowrap"
            aria-pressed={isActive}
            aria-label={`Filter by ${filter.label}`}
          >
            {filter.label}
            {badgeCount !== undefined && badgeCount > 0 && (
              <Badge
                variant={isActive ? 'secondary' : 'default'}
                className="ml-1 h-5 w-5 flex items-center justify-center p-0 text-xs"
              >
                {badgeCount > 99 ? '99+' : badgeCount}
              </Badge>
            )}
          </Button>
        );
      })}
    </div>
  );
}

export default ConversationFilters;
