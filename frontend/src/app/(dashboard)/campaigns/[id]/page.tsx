'use client';

import { use } from 'react';
import { useCampaign, useCampaignAnalytics, useStartCampaign, usePauseCampaign, useCompleteCampaign, useDeleteCampaign } from '@/hooks/useCampaigns';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Play, Pause, CheckCircle, Trash2, TrendingUp, Users, MousePointerClick, Share2 } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDistanceToNow } from 'date-fns';

interface CampaignDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function CampaignDetailPage({ params }: CampaignDetailPageProps) {
  const { id } = use(params);
  const router = useRouter();
  const campaignId = parseInt(id);

  const { data: campaign, isLoading } = useCampaign(campaignId);
  const { data: _analytics } = useCampaignAnalytics(campaignId);
  
  const startCampaign = useStartCampaign();
  const pauseCampaign = usePauseCampaign();
  const completeCampaign = useCompleteCampaign();
  const deleteCampaign = useDeleteCampaign();

  const handleStart = () => {
    if (confirm('Start this campaign?')) {
      startCampaign.mutate(campaignId);
    }
  };

  const handlePause = () => {
    if (confirm('Pause this campaign?')) {
      pauseCampaign.mutate(campaignId);
    }
  };

  const handleComplete = () => {
    if (confirm('Mark this campaign as completed?')) {
      completeCampaign.mutate(campaignId);
    }
  };

  const handleDelete = () => {
    if (confirm('Delete this campaign? This action cannot be undone.')) {
      deleteCampaign.mutate(campaignId, {
        onSuccess: () => router.push('/campaigns'),
      });
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Skeleton className="h-10 w-32 mb-8" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (!campaign) {
    return (
      <div className="container mx-auto py-8 px-4">
        <p>Campaign not found</p>
      </div>
    );
  }

  const statusColors: Record<string, string> = {
    draft: 'bg-gray-500',
    scheduled: 'bg-blue-500',
    active: 'bg-green-500',
    completed: 'bg-purple-500',
    paused: 'bg-yellow-500',
  };

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <Link href="/campaigns">
        <Button variant="ghost" className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Campaigns
        </Button>
      </Link>

      <div className="mb-8">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold mb-2">{campaign.name}</h1>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={`${statusColors[campaign.status] || 'bg-gray-500'} text-white`}>
                {campaign.status.toUpperCase()}
              </Badge>
              <Badge variant="outline">
                {campaign.contentType.replace('_', ' ')}
              </Badge>
              {campaign.platforms?.map((platform: string) => (
                <Badge key={platform} variant="secondary">
                  {platform}
                </Badge>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2">
            {campaign.status === 'draft' && (
              <Button onClick={handleStart} className="bg-green-600 hover:bg-green-700">
                <Play className="h-4 w-4 mr-2" />
                Start
              </Button>
            )}
            {campaign.status === 'active' && (
              <>
                <Button onClick={handlePause} variant="outline">
                  <Pause className="h-4 w-4 mr-2" />
                  Pause
                </Button>
                <Button onClick={handleComplete} variant="outline">
                  <CheckCircle className="h-4 w-4 mr-2" />
                  Complete
                </Button>
              </>
            )}
            {campaign.status === 'paused' && (
              <Button onClick={handleStart}>
                <Play className="h-4 w-4 mr-2" />
                Resume
              </Button>
            )}
            {campaign.status === 'draft' && (
              <Button onClick={handleDelete} variant="destructive">
                <Trash2 className="h-4 w-4 mr-2" />
                Delete
              </Button>
            )}
          </div>
        </div>

        {campaign.description && (
          <p className="text-muted-foreground">{campaign.description}</p>
        )}
      </div>

      {/* Analytics Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Total Reach
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-blue-500" />
              <div className="text-2xl font-bold">
                {campaign.stats?.reach?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Engagement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Users className="h-5 w-5 text-green-500" />
              <div className="text-2xl font-bold">
                {campaign.stats?.engagement?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Clicks
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <MousePointerClick className="h-5 w-5 text-purple-500" />
              <div className="text-2xl font-bold">
                {campaign.stats?.clicks?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Shares
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <Share2 className="h-5 w-5 text-orange-500" />
              <div className="text-2xl font-bold">
                {campaign.stats?.shares?.toLocaleString() || 0}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Campaign Details */}
      <Card>
        <CardHeader>
          <CardTitle>Campaign Timeline</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Created</p>
              <p className="font-medium">
                {formatDistanceToNow(new Date(campaign.createdAt), { addSuffix: true })}
              </p>
            </div>
            {campaign.scheduledFor && (
              <div>
                <p className="text-muted-foreground">Scheduled For</p>
                <p className="font-medium">
                  {formatDistanceToNow(new Date(campaign.scheduledFor), { addSuffix: true })}
                </p>
              </div>
            )}
            {campaign.startedAt && (
              <div>
                <p className="text-muted-foreground">Started</p>
                <p className="font-medium">
                  {formatDistanceToNow(new Date(campaign.startedAt), { addSuffix: true })}
                </p>
              </div>
            )}
            {campaign.completedAt && (
              <div>
                <p className="text-muted-foreground">Completed</p>
                <p className="font-medium">
                  {formatDistanceToNow(new Date(campaign.completedAt), { addSuffix: true })}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Generated Content Preview (if available) */}
      {campaign.generatedContent && Object.keys(campaign.generatedContent).length > 0 && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>Generated Content</CardTitle>
            <CardDescription>AI-generated content for your platforms</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(campaign.generatedContent).map(([platform, content]) => (
                <div key={platform} className="border rounded-lg p-4">
                  <h4 className="font-semibold mb-2 capitalize">{platform}</h4>
                  <pre className="text-sm text-muted-foreground whitespace-pre-wrap">
                    {JSON.stringify(content, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
