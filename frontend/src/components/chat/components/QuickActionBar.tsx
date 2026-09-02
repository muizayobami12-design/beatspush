/**
 * QuickActionBar - Horizontal scrollable bar of quick action buttons
 * Displays context-appropriate actions based on current page
 */

'use client';

import React from 'react';
import { QuickActionButton } from './QuickActionButton';
import { QUICK_ACTIONS, CONTEXT_EXTRACTORS } from '../constants';
import type { PageContext, QuickActionType } from '../types';

interface QuickActionBarProps {
  context?: PageContext;
  onActionClick: (actionId: QuickActionType) => void;
  disabled?: boolean;
}

export function QuickActionBar({ context, onActionClick, disabled = false }: QuickActionBarProps) {
  // Determine which actions to show based on context
  const getAvailableActions = () => {
    if (!context) {
      // Show general actions when no context
      return QUICK_ACTIONS.filter((action) => 
        action.availableOn.includes('general')
      ).slice(0, 4);
    }

    // Get actions for current page type
    const pageType = context.pageType;
    const contextDef = CONTEXT_EXTRACTORS[pageType];
    
    if (!contextDef) {
      return [];
    }

    // Filter actions that are available on this page
    return QUICK_ACTIONS.filter((action) => 
      contextDef.quickActions.includes(action.id)
    );
  };

  const availableActions = getAvailableActions();

  if (availableActions.length === 0) {
    return null;
  }

  return (
    <div className="px-4 py-3 border-t border-white/20 bg-white/5">
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {availableActions.map((action) => (
          <QuickActionButton
            key={action.id}
            label={action.label}
            icon={action.icon}
            action={action.id}
            context={context || { pageType: 'general', pageUrl: '', contextData: {} }}
            disabled={disabled}
            onClick={() => onActionClick(action.id)}
          />
        ))}
      </div>
    </div>
  );
}
