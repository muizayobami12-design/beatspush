'use client';

import { useState } from 'react';
import { TrendingUp, Compass, Users } from 'lucide-react';
import { CreatePost } from '@/components/features/social/CreatePost';
import { Feed } from '@/components/features/social/Feed';
import { PostDetailModal } from '@/components/features/social/PostDetailModal';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { SocialMediaIntegration } from '@/components/chat/integrations/SocialMediaIntegration';

export default function FeedPage() {
  const [feedType, setFeedType] = useState<
    'following' | 'discover' | 'trending'
  >('following');
  const [selectedPostId, setSelectedPostId] = useState<string | null>(null);

  const feedTabs = [
    {
      id: 'following' as const,
      label: 'Following',
      icon: Users,
    },
    {
      id: 'discover' as const,
      label: 'Discover',
      icon: Compass,
    },
    {
      id: 'trending' as const,
      label: 'Trending',
      icon: TrendingUp,
    },
  ];

  return (
    <SocialMediaIntegration contentType="post">
    <div className="container max-w-4xl mx-auto py-6 px-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-foreground mb-4">Feed</h1>

        {/* Feed Type Tabs */}
        <div className="flex items-center space-x-2 overflow-x-auto pb-2">
          {feedTabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <Button
                key={tab.id}
                variant={feedType === tab.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setFeedType(tab.id)}
                className={cn(
                  'flex items-center space-x-2',
                  feedType === tab.id && 'shadow-sm'
                )}
              >
                <Icon className="w-4 h-4" />
                <span>{tab.label}</span>
              </Button>
            );
          })}
        </div>
      </div>

      {/* Create Post (only show on Following feed) */}
      {feedType === 'following' && (
        <div className="mb-6">
          <CreatePost />
        </div>
      )}

      {/* Feed */}
      <Feed key={feedType} feedType={feedType} onPostClick={setSelectedPostId} />

      {/* Post Detail Modal */}
      {selectedPostId && (
        <PostDetailModal
          postId={selectedPostId}
          isOpen={!!selectedPostId}
          onClose={() => setSelectedPostId(null)}
        />
      )}
    </div>
    </SocialMediaIntegration>
  );
}
