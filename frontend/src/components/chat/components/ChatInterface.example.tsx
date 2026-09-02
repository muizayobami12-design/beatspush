/**
 * ChatInterface - Usage Examples
 * 
 * This file demonstrates how to use the ChatInterface component
 */

import React, { useState } from 'react';
import { ChatInterface } from './ChatInterface';
import type { PageContext } from '../types';

// ============================================================================
// Example 1: Basic Usage
// ============================================================================

export const BasicChatExample = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>
        Open Chat
      </button>

      <ChatInterface
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </div>
  );
};

// ============================================================================
// Example 2: With Page Context (Beat Upload Page)
// ============================================================================

export const BeatUploadChatExample = () => {
  const [isOpen, setIsOpen] = useState(false);

  const beatUploadContext: PageContext = {
    pageType: 'beat_upload',
    pageUrl: '/beats/upload',
    contextData: {
      genre: 'Hip Hop',
      bpm: 140,
      mood: 'energetic',
      fileName: 'my-beat.mp3',
    },
  };

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>
        Get AI Help with Beat Upload
      </button>

      <ChatInterface
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        initialContext={beatUploadContext}
      />
    </div>
  );
};

// ============================================================================
// Example 3: With Page Context (Campaign Dashboard)
// ============================================================================

export const CampaignChatExample = () => {
  const [isOpen, setIsOpen] = useState(false);

  const campaignContext: PageContext = {
    pageType: 'campaign_dashboard',
    pageUrl: '/campaigns/123',
    contextData: {
      campaignId: '123',
      campaignName: 'Summer Beats 2024',
      metrics: {
        reach: 50000,
        engagement: 2500,
        conversions: 125,
        spent: 500,
      },
      budget: 1000,
      targetAudience: 'Hip Hop fans aged 18-35',
    },
  };

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>
        Analyze Campaign Performance
      </button>

      <ChatInterface
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        initialContext={campaignContext}
      />
    </div>
  );
};

// ============================================================================
// Example 4: With Page Context (Analytics Page)
// ============================================================================

export const AnalyticsChatExample = () => {
  const [isOpen, setIsOpen] = useState(false);

  const analyticsContext: PageContext = {
    pageType: 'analytics',
    pageUrl: '/analytics',
    contextData: {
      timeRange: 'last_30_days',
      revenue: 5000,
      plays: 25000,
      engagement: 0.12,
      trends: {
        revenue: '+15%',
        plays: '+8%',
        engagement: '-2%',
      },
    },
  };

  return (
    <div>
      <button onClick={() => setIsOpen(true)}>
        Get AI Insights
      </button>

      <ChatInterface
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        initialContext={analyticsContext}
      />
    </div>
  );
};

// ============================================================================
// Example 5: Global Chat Button (Can be placed in layout)
// ============================================================================

export const GlobalChatButton = () => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <>
      {/* Fixed button in bottom-right corner */}
      <button
        className="fixed bottom-6 right-6 z-40 w-14 h-14 rounded-full bg-gradient-to-r from-purple-500 to-blue-500 hover:from-purple-600 hover:to-blue-600 shadow-lg flex items-center justify-center text-white transition-transform hover:scale-110"
        onClick={() => setIsOpen(true)}
        aria-label="Open AI Assistant"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="w-6 h-6"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      </button>

      <ChatInterface
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
      />
    </>
  );
};

// ============================================================================
// Example 6: Integration with Navigation Bar
// ============================================================================

export const NavBarWithChat = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);

  return (
    <nav className="flex items-center justify-between p-4 bg-white shadow">
      <div className="text-xl font-bold">BeatPush</div>
      
      <div className="flex items-center gap-4">
        <a href="/beats">Beats</a>
        <a href="/campaigns">Campaigns</a>
        <a href="/analytics">Analytics</a>
        
        {/* Chat trigger button */}
        <button
          onClick={() => setIsChatOpen(true)}
          className="px-4 py-2 rounded-lg bg-gradient-to-r from-purple-500 to-blue-500 text-white hover:from-purple-600 hover:to-blue-600"
        >
          AI Assistant
        </button>
      </div>

      <ChatInterface
        isOpen={isChatOpen}
        onClose={() => setIsChatOpen(false)}
      />
    </nav>
  );
};

// ============================================================================
// Example 7: Programmatic Opening with Context Update
// ============================================================================

export const DynamicContextExample = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [context, setContext] = useState<PageContext | undefined>(undefined);

  const openChatWithContext = (newContext: PageContext) => {
    setContext(newContext);
    setIsOpen(true);
  };

  return (
    <div>
      <div className="space-x-2">
        <button onClick={() => openChatWithContext({
          pageType: 'beat_upload',
          pageUrl: '/beats/upload',
          contextData: { genre: 'Hip Hop' },
        })}>
          Help with Beat Upload
        </button>

        <button onClick={() => openChatWithContext({
          pageType: 'profile_edit',
          pageUrl: '/profile',
          contextData: { existingBio: 'Producer from LA' },
        })}>
          Help with Profile
        </button>

        <button onClick={() => openChatWithContext({
          pageType: 'social_feed',
          pageUrl: '/feed',
          contextData: { contentType: 'beat_release' },
        })}>
          Generate Social Caption
        </button>
      </div>

      <ChatInterface
        isOpen={isOpen}
        onClose={() => setIsOpen(false)}
        initialContext={context}
      />
    </div>
  );
};
