/**
 * Campaign Page Integration
 * Provides AI chat context for campaign dashboard
 */

'use client';

import React, { useEffect } from 'react';
import { usePageContext } from '../hooks/usePageContext';
import { useChatContext } from '../components/ChatProvider';

interface CampaignMetrics {
  reach?: number;
  engagement?: number;
  conversions?: number;
  spent?: number;
}

interface CampaignIntegrationProps {
  campaignId?: string;
  campaignName?: string;
  metrics?: CampaignMetrics;
  budget?: number;
  targetAudience?: string;
  duration?: string;
  children?: React.ReactNode;
}

export function CampaignIntegration({
  campaignId,
  campaignName,
  metrics,
  budget,
  targetAudience,
  duration,
  children,
}: CampaignIntegrationProps) {
  const { updateContext } = usePageContext({
    props: {
      campaign: {
        id: campaignId,
        name: campaignName,
        budget,
        targetAudience,
        duration,
      },
      metrics,
    },
    autoDetect: false,
  });

  useEffect(() => {
    updateContext({
      pageType: 'campaign_dashboard',
      pageUrl: window.location.pathname,
      contextData: {
        campaignId,
        campaignName,
        metrics,
        budget,
        targetAudience,
        duration,
      },
    });
  }, [campaignId, campaignName, metrics, budget, targetAudience, duration, updateContext]);

  return <>{children}</>;
}

export function useCampaignChat() {
  const { openChat } = useChatContext();
  
  return {
    analyzePerformance: () => openChat(),
    suggestOptimizations: () => openChat(),
    generateAdCopy: () => openChat(),
    openChat,
  };
}
