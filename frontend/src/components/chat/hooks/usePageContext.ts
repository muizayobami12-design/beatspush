/**
 * usePageContext - Hook for extracting and managing page context
 */

import { useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';
import type { PageContext } from '../types';
import { detectPageType, extractPageContext } from '../utils/contextUtils';

interface UsePageContextOptions {
  props?: Record<string, any>;
  autoDetect?: boolean;
}

export function usePageContext(options: UsePageContextOptions = {}) {
  const { props, autoDetect = true } = options;
  const pathname = usePathname();
  
  const [context, setContext] = useState<PageContext>(() => {
    if (!autoDetect) {
      return {
        pageType: 'general',
        pageUrl: '',
        contextData: {},
      };
    }

    const pageType = detectPageType(pathname || '');
    return extractPageContext(pageType, props);
  });

  // Update context when pathname or props change
  useEffect(() => {
    if (!autoDetect) return;

    const pageType = detectPageType(pathname || '');
    const newContext = extractPageContext(pageType, props);
    setContext(newContext);
  }, [pathname, props, autoDetect]);

  // Manual context update
  const updateContext = (updates: Partial<PageContext>) => {
    setContext((prev) => ({
      ...prev,
      ...updates,
      contextData: {
        ...prev.contextData,
        ...(updates.contextData || {}),
      },
    }));
  };

  // Reset context
  const resetContext = () => {
    setContext({
      pageType: 'general',
      pageUrl: pathname || '',
      contextData: {},
    });
  };

  return {
    context,
    updateContext,
    resetContext,
  };
}
