'use client';

import { Campaign } from '@/services/campaignService';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Calendar, 
  BarChart3, 
  Play, 
  Pause, 
  CheckCircle, 
  Edit, 
  Trash2,
  TrendingUp,
  Users,
  MousePointerClick
} from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';

interface CampaignCardProps {
  campaign: Campaign;
  onStart?: (id: number) => void;
  onPause?: (id: number) => void;
  onComplete?: (id: number) => void;
  onDelete?: (id: number) => void;
}

const statusColors = {
  draft: 'bg-gray-500',
  scheduled: 'bg-blue-500',
  active: 'bg-green-500',
  completed: 'bg-purple-500',
  paused: 'bg-yellow-500',
};

const statusIcons = {
  draft: Edit,
  scheduled: Calendar,
  active: Play,
  completed: CheckCircle,
  paused: Pause,
};

export function CampaignCard({ 
  campaign, 
  onStart, 
  onPause, 
  onComplete, 
  onDelete 
}: CampaignCardProps) {
  const StatusIcon = statusIcons[campaign.status];

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <CardTitle className="text-lg mb-2">{campaign.name}</CardTitle>
            <div className="flex items-center gap-2 flex-wrap">
              <Badge className={`${statusColors[campaign.status]} text-white`}>
                <StatusIcon className="h-3 w-3 mr-1" />
                {campaign.status?.charAt(0)?.toUpperCase() + (campaign.status?.slice(1) || '') || 'Unknown'}
              </Badge>
              <Badge variant="outline">
                {campaign.contentType.replace('_', ' ')}
              </Badge>
              {campaign.platforms.map((platform) => (
                <Badge key={platform} variant="secondary">
                  {platform}
                </Badge>
              ))}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        {campaign.description && (
          <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
            {campaign.description}
          </p>
        )}

        {/* Stats */}
        {campaign.stats && (
          <div className="grid grid-cols-3 gap-4 mb-4">
            <div className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-blue-500" />
              <div>
                <p className="text-xs text-muted-foreground">Reach</p>
                <p className="text-sm font-semibold">
                  {campaign.stats.reach?.toLocaleString() || 0}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-green-500" />
              <div>
                <p className="text-xs text-muted-foreground">Engagement</p>
                <p className="text-sm font-semibold">
                  {campaign.stats.engagement?.toLocaleString() || 0}
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <MousePointerClick className="h-4 w-4 text-purple-500" />
              <div>
                <p className="text-xs text-muted-foreground">Clicks</p>
                <p className="text-sm font-semibold">
                  {campaign.stats.clicks?.toLocaleString() || 0}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Scheduled Date */}
        {campaign.scheduledFor && campaign.status === 'scheduled' && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground mb-2">
            <Calendar className="h-4 w-4" />
            <span>
              Scheduled for {formatDistanceToNow(new Date(campaign.scheduledFor), { addSuffix: true })}
            </span>
          </div>
        )}

        {/* Dates */}
        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          {campaign.startedAt && (
            <span>Started {formatDistanceToNow(new Date(campaign.startedAt), { addSuffix: true })}</span>
          )}
          {campaign.completedAt && (
            <span>Completed {formatDistanceToNow(new Date(campaign.completedAt), { addSuffix: true })}</span>
          )}
          {!campaign.startedAt && !campaign.completedAt && (
            <span>Created {formatDistanceToNow(new Date(campaign.createdAt), { addSuffix: true })}</span>
          )}
        </div>
      </CardContent>

      <CardFooter className="flex justify-between gap-2">
        <Link href={`/campaigns/${campaign.id}`}>
          <Button variant="outline" size="sm">
            <BarChart3 className="h-4 w-4 mr-2" />
            View Details
          </Button>
        </Link>

        <div className="flex gap-2">
          {campaign.status === 'draft' && onStart && (
            <Button 
              size="sm" 
              onClick={() => onStart(campaign.id)}
              className="bg-green-600 hover:bg-green-700"
            >
              <Play className="h-4 w-4 mr-2" />
              Start
            </Button>
          )}

          {campaign.status === 'active' && onPause && (
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => onPause(campaign.id)}
            >
              <Pause className="h-4 w-4 mr-2" />
              Pause
            </Button>
          )}

          {campaign.status === 'paused' && onStart && (
            <Button 
              size="sm"
              onClick={() => onStart(campaign.id)}
            >
              <Play className="h-4 w-4 mr-2" />
              Resume
            </Button>
          )}

          {(campaign.status === 'active' || campaign.status === 'paused') && onComplete && (
            <Button 
              size="sm" 
              variant="outline"
              onClick={() => onComplete(campaign.id)}
            >
              <CheckCircle className="h-4 w-4 mr-2" />
              Complete
            </Button>
          )}

          {campaign.status === 'draft' && onDelete && (
            <Button 
              size="sm" 
              variant="destructive"
              onClick={() => onDelete(campaign.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </CardFooter>
    </Card>
  );
}
