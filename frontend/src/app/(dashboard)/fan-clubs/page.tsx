'use client';

import { useState, useMemo } from 'react';
import { Users, Sparkles, Heart, Lock, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

type Tab = 'all' | 'joined' | 'featured';
type TierType = 'basic' | 'plus' | 'vip';

interface FanClub {
  id: string;
  name: string;
  creator: string;
  creatorAvatar?: string;
  description: string;
  memberCount: number;
  featured?: boolean;
  tiers: Array<{
    type: TierType;
    name: string;
    price: number;
    perks: string[];
  }>;
}

// Mock fan clubs data
const MOCK_FAN_CLUBS: FanClub[] = [
  {
    id: '1',
    name: 'Oluwa Beats VIP',
    creator: 'Oluwa Beats',
    description: 'Exclusive access to unreleased tracks and private sessions',
    memberCount: 1245,
    featured: true,
    tiers: [
      {
        type: 'basic',
        name: 'Supporter',
        price: 2500,
        perks: ['Early access to new beats', 'Exclusive wallpapers', 'Discord community'],
      },
      {
        type: 'plus',
        name: 'Producer',
        price: 5000,
        perks: ['All Supporter perks', 'Monthly collaboration call', 'Custom samples'],
      },
      {
        type: 'vip',
        name: 'Executive',
        price: 10000,
        perks: ['All Producer perks', 'Private beat sessions', 'Feature on social media'],
      },
    ],
  },
  {
    id: '2',
    name: 'Sound Engineer Elite',
    creator: 'Sound Engineer',
    description: 'Join the inner circle for production tips and studio sessions',
    memberCount: 856,
    featured: true,
    tiers: [
      {
        type: 'basic',
        name: 'Subscriber',
        price: 3000,
        perks: ['Weekly tutorials', 'Sample packs', 'Community access'],
      },
      {
        type: 'plus',
        name: 'Member',
        price: 6000,
        perks: ['All Subscriber perks', 'Monthly live sessions', 'Beat feedback'],
      },
      {
        type: 'vip',
        name: 'Collaborator',
        price: 12000,
        perks: ['All Member perks', 'Direct messaging', 'Project collaboration'],
      },
    ],
  },
  {
    id: '3',
    name: 'Zaria Music Studio',
    creator: 'Zaria',
    description: 'Creative collective for producers and artists',
    memberCount: 623,
    tiers: [
      {
        type: 'basic',
        name: 'Friend',
        price: 2000,
        perks: ['Access to library', 'Monthly playlist', 'Community chat'],
      },
      {
        type: 'plus',
        name: 'Collaborator',
        price: 4000,
        perks: ['All Friend perks', 'Co-creation opportunities', 'Revenue share'],
      },
      {
        type: 'vip',
        name: 'Partner',
        price: 8000,
        perks: ['All Collaborator perks', 'Exclusive events', 'Label partnership'],
      },
    ],
  },
  {
    id: '4',
    name: 'Producer Alex Collective',
    creator: 'Producer Alex',
    description: 'Learn music production from an experienced professional',
    memberCount: 1802,
    featured: true,
    tiers: [
      {
        type: 'basic',
        name: 'Student',
        price: 3500,
        perks: ['Video tutorials', 'Q&A sessions', 'Resource library'],
      },
      {
        type: 'plus',
        name: 'Producer',
        price: 7000,
        perks: ['All Student perks', 'One-on-one feedback', 'Mentorship'],
      },
      {
        type: 'vip',
        name: 'Professional',
        price: 15000,
        perks: ['All Producer perks', 'Career guidance', 'Studio sessions'],
      },
    ],
  },
];

export default function FanClubsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedClub, setSelectedClub] = useState<FanClub | null>(null);
  const [showJoinModal, setShowJoinModal] = useState(false);

  // Filter fan clubs
  const filteredClubs = useMemo(() => {
    let clubs = [...MOCK_FAN_CLUBS];

    // Tab filter
    if (activeTab === 'featured') {
      clubs = clubs.filter((c) => c.featured);
    }
    if (activeTab === 'joined') {
      // Mock: joined clubs (first 2)
      clubs = clubs.slice(0, 2);
    }

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      clubs = clubs.filter(
        (c) =>
          c.name.toLowerCase().includes(query) ||
          c.creator.toLowerCase().includes(query) ||
          c.description.toLowerCase().includes(query)
      );
    }

    return clubs;
  }, [activeTab, searchQuery]);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatNumber = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  return (
    <div className="min-h-screen bg-background pb-8">
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        {/* Header */}
        <div className="mb-stack-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className={cn(
              'p-3 rounded-lg',
              'bg-surface-container border border-outline-variant/20'
            )}>
              <Users className="h-6 w-6 text-secondary" />
            </div>
            <div>
              <h1 className={cn(
                'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
                'text-on-surface'
              )}>
                Fan Clubs
              </h1>
              <p className={cn(
                'font-body-md text-body-md',
                'text-on-surface-variant'
              )}>
                Support your favorite creators and join exclusive communities
              </p>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className={cn(
          'flex gap-2 mb-stack-lg border-b border-outline-variant/20 pb-2'
        )}>
          {(['all', 'featured', 'joined'] as const).map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={cn(
                'px-4 py-2 rounded-lg font-label-md text-label-md',
                'transition-all border border-transparent',
                activeTab === tab
                  ? 'bg-secondary text-on-secondary border-secondary'
                  : 'text-on-surface-variant hover:text-on-surface'
              )}
            >
              {tab === 'all' && 'All Clubs'}
              {tab === 'featured' && 'Featured'}
              {tab === 'joined' && 'My Clubs'}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className={cn(
          'mb-stack-lg flex items-center gap-3'
        )}>
          <Input
            type="text"
            placeholder="Search fan clubs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className={cn(
              'bg-surface-container border border-outline-variant/30',
              'text-on-surface placeholder-on-surface-variant/50'
            )}
          />
        </div>

        {/* Fan Clubs Grid */}
        {filteredClubs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-gutter">
            {filteredClubs.map((club) => (
              <div
                key={club.id}
                className={cn(
                  'rounded-lg border ghost-border overflow-hidden',
                  'bg-surface-container hover:bg-surface-container-low',
                  'transition-all duration-200'
                )}
              >
                {/* Header */}
                <div className="p-stack-md border-b border-outline-variant/20">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className={cn(
                        'font-headline-sm text-headline-sm',
                        'text-on-surface'
                      )}>
                        {club.name}
                      </h3>
                      <p className={cn(
                        'font-body-sm text-body-sm mt-1',
                        'text-on-surface-variant'
                      )}>
                        by {club.creator}
                      </p>
                    </div>
                    {club.featured && (
                      <Sparkles className="h-5 w-5 text-secondary flex-shrink-0" />
                    )}
                  </div>

                  <p className={cn(
                    'font-body-md text-body-md line-clamp-2',
                    'text-on-surface-variant'
                  )}>
                    {club.description}
                  </p>
                </div>

                {/* Members */}
                <div className="px-stack-md py-stack-sm border-b border-outline-variant/20 flex items-center gap-2">
                  <Users className="h-4 w-4 text-on-surface-variant" />
                  <span className={cn(
                    'font-body-sm text-body-sm',
                    'text-on-surface-variant'
                  )}>
                    {formatNumber(club.memberCount)} members
                  </span>
                </div>

                {/* Tiers */}
                <div className="p-stack-md space-y-3">
                  {club.tiers.map((tier) => (
                    <div
                      key={tier.type}
                      className={cn(
                        'p-2 rounded-lg border',
                        tier.type === 'vip'
                          ? 'bg-secondary/10 border-secondary/30'
                          : tier.type === 'plus'
                            ? 'bg-tertiary/10 border-tertiary/30'
                            : 'bg-surface-container-low border-outline-variant/20'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className={cn(
                            'font-label-sm text-label-sm',
                            tier.type === 'vip' ? 'text-secondary' : 'text-on-surface'
                          )}>
                            {tier.name}
                          </p>
                          <p className={cn(
                            'font-body-sm text-body-sm mt-1',
                            'text-on-surface'
                          )}>
                            {formatCurrency(tier.price)}/month
                          </p>
                        </div>
                        {tier.type === 'vip' && (
                          <Crown className="h-4 w-4 text-secondary flex-shrink-0" />
                        )}
                      </div>

                      <div className="mt-2 space-y-1">
                        {tier.perks.slice(0, 2).map((perk, i) => (
                          <p key={i} className={cn(
                            'font-body-xs text-body-xs',
                            'text-on-surface-variant'
                          )}>
                            • {perk}
                          </p>
                        ))}
                        {tier.perks.length > 2 && (
                          <p className={cn(
                            'font-body-xs text-body-xs',
                            'text-on-surface-variant'
                          )}>
                            + {tier.perks.length - 2} more
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* CTA Button */}
                <div className="p-stack-md border-t border-outline-variant/20">
                  <Button
                    onClick={() => {
                      setSelectedClub(club);
                      setShowJoinModal(true);
                    }}
                    variant="default"
                    className="w-full gap-2"
                  >
                    <Heart className="h-4 w-4" />
                    Support This Creator
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          /* Empty State */
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <Users className="h-12 w-12 text-on-surface-variant/50 mx-auto mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              No fan clubs found
            </p>
          </div>
        )}

        {/* Join Modal */}
        {showJoinModal && selectedClub && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
            <div className={cn(
              'bg-surface-container rounded-lg max-w-md w-full',
              'border ghost-border'
            )}>
              <div className="p-stack-lg">
                <div className="flex items-center justify-between mb-4">
                  <h2 className={cn(
                    'font-headline-md text-headline-md',
                    'text-on-surface'
                  )}>
                    {selectedClub.name}
                  </h2>
                  <button
                    onClick={() => setShowJoinModal(false)}
                    className={cn(
                      'p-1 rounded hover:bg-surface-container-low',
                      'text-on-surface-variant'
                    )}
                  >
                    ✕
                  </button>
                </div>

                <p className={cn(
                  'font-body-md text-body-md mb-6',
                  'text-on-surface-variant'
                )}>
                  Choose your tier:
                </p>

                <div className="space-y-3 mb-6">
                  {selectedClub.tiers.map((tier) => (
                    <button
                      key={tier.type}
                      className={cn(
                        'w-full p-3 rounded-lg border text-left transition-all',
                        'hover:border-secondary'
                      )}
                    >
                      <div className="flex items-center justify-between">
                        <div>
                          <p className={cn(
                            'font-body-md text-body-md',
                            'text-on-surface'
                          )}>
                            {tier.name}
                          </p>
                          <p className={cn(
                            'font-body-sm text-body-sm',
                            'text-secondary'
                          )}>
                            {formatCurrency(tier.price)}/month
                          </p>
                        </div>
                        <ArrowRight className="h-4 w-4 text-on-surface-variant" />
                      </div>
                    </button>
                  ))}
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setShowJoinModal(false)}
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                  <Button
                    variant="default"
                    onClick={() => {
                      setShowJoinModal(false);
                      setSelectedClub(null);
                    }}
                    className="flex-1"
                  >
                    Continue
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function Crown({ className }: { className: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="currentColor" className={className}>
      <path d="M12 2l3 6h6l-5 4 2 6-6-4-6 4 2-6-5-4h6l3-6z" />
    </svg>
  );
}
