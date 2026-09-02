/**
 * Analytics Page Integration
 * Provides AI chat context for analytics page
 */

'use client';

import React, { useEffect } from 'react';
import { usePageContext } from '../hooks/usePageContext';
import { useChatContext } from '../components/ChatProvider';

interface AnalyticsData {
  timeRange?: string;
  revenue?: number;
  plays?: number;
  engagement?: number;
  trends?: Record<string, any>;
  topBeats?: any[];
  growth?: Record<string, number>;
}

interface AnalyticsIntegrationProps extends AnalyticsData {
  children?: React.ReactNode;
}

export function AnalyticsIntegration({
  timeRange,
  revenue,
  plays,
  engagement,
  trends,
  topBeats,
  growth,
  children,
}: AnalyticsIntegrationProps) {
  const { updateContext } = usePageContext({
    props: {
      timeRange,
      metrics: { revenue, plays, engagement },
      trends,
      topBeats,
      growth,
    },
    autoDetect: false,
  });

  useEffect(() => {
    updateContext({
      pageType: 'analytics',
      pageUrl: window.location.pathname,
      contextData: {
        timeRange,
        revenue,
        plays,
        engagement,
        trends,
        topBeats,
        growth,
      },
    });
  }, [timeRange, revenue, plays, engagement, trends, topBeats, growth, updateContext]);

  return <>{children}</>;
}

export function useAnalyticsChat() {
  const { openChat } = useChatContext();
  
  return {
    explainTrends: () => openChat(),
    comparePerformance: () => openChat(),
    getRecommendations: () => openChat(),
    openChat,
  };
}
