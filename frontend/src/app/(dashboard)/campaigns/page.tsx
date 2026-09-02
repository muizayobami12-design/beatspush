'use client';

import { useState, useMemo } from 'react';
import { Zap, Play, Pause, BarChart3, TrendingUp, Calendar, Users, Download, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { DateRangePicker } from '@/components/ui/date-range-picker';
import { cn } from '@/lib/utils';

type CampaignStatus = 'active' | 'paused' | 'completed' | 'draft';

interface Campaign {
  id: string;
  title: string;
  beatTitle: string;
  status: CampaignStatus;
  startDate: Date;
  endDate: Date;
  budget: number;
  spent: number;
  clicks: number;
  conversions: number;
  roi: number;
  createdAt: Date;
}

// Mock campaigns data
const MOCK_CAMPAIGNS: Campaign[] = [
  {
    id: '1',
    title: 'Summer Vibes Campaign',
    beatTitle: 'Lagos Nights',
    status: 'active',
    startDate: new Date(Date.now() - 10 * 24 * 60 * 60000),
    endDate: new Date(Date.now() + 20 * 24 * 60 * 60000),
    budget: 100000,
    spent: 65000,
    clicks: 2451,
    conversions: 187,
    roi: 245,
    createdAt: new Date(Date.now() - 15 * 24 * 60 * 60000),
  },
  {
    id: '2',
    title: 'Midnight Voyage Promotion',
    beatTitle: 'Midnight Voyage',
    status: 'active',
    startDate: new Date(Date.now() - 5 * 24 * 60 * 60000),
    endDate: new Date(Date.now() + 25 * 24 * 60 * 60000),
    budget: 150000,
    spent: 42500,
    clicks: 1876,
    conversions: 156,
    roi: 368,
    createdAt: new Date(Date.now() - 8 * 24 * 60 * 60000),
  },
  {
    id: '3',
    title: 'Heritage Producer Push',
    beatTitle: 'Heritage',
    status: 'paused',
    startDate: new Date(Date.now() - 30 * 24 * 60 * 60000),
    endDate: new Date(Date.now() + 10 * 24 * 60 * 60000),
    budget: 80000,
    spent: 80000,
    clicks: 3245,
    conversions: 412,
    roi: 512,
    createdAt: new Date(Date.now() - 40 * 24 * 60 * 60000),
  },
  {
    id: '4',
    title: 'Afrosynth Wave Launch',
    beatTitle: 'Afrosynth Wave',
    status: 'completed',
    startDate: new Date(Date.now() - 60 * 24 * 60 * 60000),
    endDate: new Date(Date.now() - 10 * 24 * 60 * 60000),
    budget: 120000,
    spent: 120000,
    clicks: 5620,
    conversions: 687,
    roi: 572,
    createdAt: new Date(Date.now() - 75 * 24 * 60 * 60000),
  },
  {
    id: '5',
    title: 'New Year Beats',
    beatTitle: 'Summer Anthems',
    status: 'draft',
    startDate: new Date(Date.now() + 30 * 24 * 60 * 60000),
    endDate: new Date(Date.now() + 90 * 24 * 60 * 60000),
    budget: 200000,
    spent: 0,
    clicks: 0,
    conversions: 0,
    roi: 0,
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60000),
  },
];

const STATUS_COLORS: Record<CampaignStatus, string> = {
  active: 'bg-secondary/20 text-secondary border-secondary/30',
  paused: 'bg-tertiary/20 text-tertiary border-tertiary/30',
  completed: 'bg-secondary-fixed/20 text-secondary-fixed border-secondary-fixed/30',
  draft: 'bg-on-surface-variant/20 text-on-surface-variant border-on-surface-variant/30',
};

export default function CampaignsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<CampaignStatus | 'all'>('all');
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date } | null>(null);

  // Filter campaigns
  const filteredCampaigns = useMemo(() => {
    let campaigns = [...MOCK_CAMPAIGNS];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      campaigns = campaigns.filter(
        (c) =>
          c.title.toLowerCase().includes(query) ||
          c.beatTitle.toLowerCase().includes(query)
      );
    }

    // Status filter
    if (selectedStatus !== 'all') {
      campaigns = campaigns.filter((c) => c.status === selectedStatus);
    }

    // Date range filter
    if (dateRange) {
      campaigns = campaigns.filter((c) => {
        const startTime = c.startDate.getTime();
        const endTime = c.endDate.getTime();
        const rangeStart = dateRange.start.getTime();
        const rangeEnd = dateRange.end.getTime();
        return startTime <= rangeEnd && endTime >= rangeStart;
      });
    }

    return campaigns.sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime());
  }, [searchQuery, selectedStatus, dateRange]);

  // Calculate stats
  const stats = useMemo(() => ({
    active: MOCK_CAMPAIGNS.filter((c) => c.status === 'active').length,
    totalSpent: MOCK_CAMPAIGNS.reduce((sum, c) => sum + c.spent, 0),
    totalClicks: MOCK_CAMPAIGNS.reduce((sum, c) => sum + c.clicks, 0),
    avgROI: Math.round(
      MOCK_CAMPAIGNS.filter((c) => c.roi > 0).reduce((sum, c) => sum + c.roi, 0) /
      MOCK_CAMPAIGNS.filter((c) => c.roi > 0).length
    ),
  }), []);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-NG', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    }).format(date);
  };

  return (
    <div className="min-h-screen bg-background pb-8">
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        {/* Header */}
        <div className="mb-stack-lg flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={cn(
              'p-3 rounded-lg',
              'bg-surface-container border border-outline-variant/20'
            )}>
              <Zap className="h-6 w-6 text-secondary" />
            </div>
            <div>
              <h1 className={cn(
                'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
                'text-on-surface'
              )}>
                Campaigns
              </h1>
              <p className={cn(
                'font-body-md text-body-md',
                'text-on-surface-variant'
              )}>
                Manage your promotional campaigns
              </p>
            </div>
          </div>

          <Button className="gap-2">
            <Plus className="h-4 w-4" />
            <span className="hidden md:inline">New Campaign</span>
          </Button>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-gutter mb-stack-lg">
          {[
            { label: 'Active Campaigns', value: stats.active, icon: Play, color: 'text-secondary' },
            { label: 'Total Spent', value: formatCurrency(stats.totalSpent), icon: Zap, color: 'text-tertiary' },
            { label: 'Total Clicks', value: stats.totalClicks.toLocaleString(), icon: Users, color: 'text-clay' },
            { label: 'Avg ROI', value: `${stats.avgROI}%`, icon: TrendingUp, color: 'text-secondary-fixed' },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div
                key={i}
                className={cn(
                  'rounded-lg border ghost-border p-stack-md',
                  'bg-surface-container'
                )}
              >
                <div className="flex items-center justify-between mb-2">
                  <p className={cn(
                    'font-label-sm text-label-sm uppercase tracking-wider',
                    'text-on-surface-variant'
                  )}>
                    {stat.label}
                  </p>
                  <Icon className={cn('h-4 w-4', stat.color)} />
                </div>
                <p className={cn(
                  'font-headline-md text-headline-md',
                  stat.color
                )}>
                  {stat.value}
                </p>
              </div>
            );
          })}
        </div>

        {/* Filters */}
        <div className={cn(
          'rounded-lg border ghost-border p-stack-md mb-stack-lg',
          'bg-surface-container-low space-y-4'
        )}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            {/* Search */}
            <div className="md:col-span-2">
              <label className={cn(
                'font-label-sm text-label-sm block mb-2',
                'text-on-surface-variant uppercase tracking-wider'
              )}>
                Search
              </label>
              <Input
                type="text"
                placeholder="Search campaigns..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className={cn(
                  'bg-surface-container border border-outline-variant/30',
                  'text-on-surface placeholder-on-surface-variant/50'
                )}
              />
            </div>

            {/* Status */}
            <div>
              <label className={cn(
                'font-label-sm text-label-sm block mb-2',
                'text-on-surface-variant uppercase tracking-wider'
              )}>
                Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as CampaignStatus | 'all')}
                className={cn(
                  'w-full px-3 py-2 rounded-lg',
                  'bg-surface-container border border-outline-variant/30',
                  'text-on-surface font-body-md'
                )}
              >
                <option value="all">All Status</option>
                <option value="active">Active</option>
                <option value="paused">Paused</option>
                <option value="completed">Completed</option>
                <option value="draft">Draft</option>
              </select>
            </div>
          </div>

          {/* Date Range */}
          <div>
            <label className={cn(
              'font-label-sm text-label-sm block mb-2',
              'text-on-surface-variant uppercase tracking-wider'
            )}>
              Date Range
            </label>
            <DateRangePicker
              onDateRangeChange={(range) => setDateRange(range)}
            />
          </div>
        </div>

        {/* Campaigns Table */}
        {filteredCampaigns.length > 0 ? (
          <div className={cn(
            'rounded-lg border ghost-border overflow-hidden',
            'bg-surface-container'
          )}>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-outline-variant/20 bg-surface-container-low">
                    <th className="px-stack-md py-stack-sm text-left">
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Campaign
                      </p>
                    </th>
                    <th className="px-stack-md py-stack-sm text-left">
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Duration
                      </p>
                    </th>
                    <th className="px-stack-md py-stack-sm text-right">
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Budget
                      </p>
                    </th>
                    <th className="px-stack-md py-stack-sm text-right">
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Clicks
                      </p>
                    </th>
                    <th className="px-stack-md py-stack-sm text-right">
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        ROI
                      </p>
                    </th>
                    <th className="px-stack-md py-stack-sm text-center">
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Status
                      </p>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {filteredCampaigns.map((campaign, idx) => (
                    <tr
                      key={campaign.id}
                      className={cn(
                        idx !== filteredCampaigns.length - 1 && 'border-b border-outline-variant/20'
                      )}
                    >
                      <td className="px-stack-md py-stack-md">
                        <div>
                          <p className={cn(
                            'font-body-md text-body-md',
                            'text-on-surface'
                          )}>
                            {campaign.title}
                          </p>
                          <p className={cn(
                            'font-body-sm text-body-sm',
                            'text-on-surface-variant'
                          )}>
                            {campaign.beatTitle}
                          </p>
                        </div>
                      </td>
                      <td className="px-stack-md py-stack-md">
                        <p className={cn(
                          'font-body-sm text-body-sm',
                          'text-on-surface-variant'
                        )}>
                          {formatDate(campaign.startDate)} - {formatDate(campaign.endDate)}
                        </p>
                      </td>
                      <td className="px-stack-md py-stack-md text-right">
                        <p className={cn(
                          'font-body-md text-body-md',
                          'text-on-surface'
                        )}>
                          {formatCurrency(campaign.budget)}
                        </p>
                        <p className={cn(
                          'font-body-sm text-body-sm',
                          'text-on-surface-variant'
                        )}>
                          Spent: {formatCurrency(campaign.spent)}
                        </p>
                      </td>
                      <td className="px-stack-md py-stack-md text-right">
                        <p className={cn(
                          'font-body-md text-body-md',
                          'text-on-surface'
                        )}>
                          {campaign.clicks.toLocaleString()}
                        </p>
                        <p className={cn(
                          'font-body-sm text-body-sm',
                          'text-on-surface-variant'
                        )}>
                          {campaign.conversions} conversions
                        </p>
                      </td>
                      <td className="px-stack-md py-stack-md text-right">
                        <p className={cn(
                          'font-label-md text-label-md',
                          campaign.roi > 0 ? 'text-secondary' : 'text-on-surface-variant'
                        )}>
                          {campaign.roi}%
                        </p>
                      </td>
                      <td className="px-stack-md py-stack-md text-center">
                        <div className={cn(
                          'inline-flex items-center gap-1 px-2 py-1 rounded-full',
                          'font-label-xs text-label-xs border',
                          STATUS_COLORS[campaign.status]
                        )}>
                          {campaign.status === 'active' && <Play className="h-3 w-3" />}
                          {campaign.status === 'paused' && <Pause className="h-3 w-3" />}
                          {campaign.status.charAt(0).toUpperCase() + campaign.status.slice(1)}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          /* Empty State */
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <BarChart3 className="h-12 w-12 text-on-surface-variant/50 mx-auto mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              No campaigns found
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
