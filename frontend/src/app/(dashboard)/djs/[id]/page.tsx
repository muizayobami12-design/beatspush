'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { notFound } from 'next/navigation';
import { ArrowLeft, Radio, Users, TrendingUp, Clock, CheckCircle2, Send } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { djSubmissionService, type DJ } from '@/services/djSubmissionService';
import { TipButton } from '@/components/shared/TipButton';

export default function DJProfilePage() {
  const params = useParams();
  const djId = params.id as string;
  
  const [dj, setDj] = useState<DJ | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notFoundError, setNotFoundError] = useState(false);

  useEffect(() => {
    fetchDJ();
  }, [djId]);

  const fetchDJ = async () => {
    setIsLoading(true);
    try {
      const data = await djSubmissionService.getDJById(djId);
      if (!data) {
        setNotFoundError(true);
      } else {
        setDj(data);
      }
    } catch (error) {
      console.error('Failed to fetch DJ:', error);
      setNotFoundError(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Properly handle 404 for missing DJs
  if (notFoundError && !isLoading) {
    notFound();
  }

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!dj) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="bg-gradient-to-b from-primary/20 to-background">
        <div className="container mx-auto px-4 py-6">
          <Link href="/djs">
            <Button variant="ghost" size="sm" className="gap-2 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to DJs
            </Button>
          </Link>

          <div className="flex flex-col md:flex-row gap-8 items-start md:items-center">
            {/* Avatar */}
            <div className="w-48 h-48 rounded-full overflow-hidden bg-gradient-to-br from-primary/30 to-primary/10 flex-shrink-0 shadow-2xl border-4 border-background">
              {dj.avatar_url ? (
                <img
                  src={dj.avatar_url}
                  alt={dj.full_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Radio className="h-20 w-20 text-muted-foreground opacity-30" />
                </div>
              )}
            </div>

            {/* DJ Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <span className="px-3 py-1 rounded-full bg-primary/20 text-primary text-sm font-semibold flex items-center gap-1">
                  <Radio className="h-3 w-3" />
                  DJ
                </span>
                {dj.is_verified && (
                  <CheckCircle2 className="h-5 w-5 text-blue-500" />
                )}
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold mb-2">{dj.full_name}</h1>
              <p className="text-xl text-muted-foreground mb-6">@{dj.username}</p>

              {dj.bio && (
                <p className="text-muted-foreground mb-6 max-w-2xl">{dj.bio}</p>
              )}

              {/* Stats */}
              <div className="flex items-center gap-6 text-sm mb-8">
                <span className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  {dj.follower_count.toLocaleString()} followers
                </span>
                <span className="flex items-center gap-1">
                  <TrendingUp className="h-4 w-4" />
                  {Math.round(dj.acceptance_rate * 100)}% acceptance
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {dj.avg_response_time_hours}h response
                </span>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap items-center gap-3">
                {dj.accepts_submissions ? (
                  <Link href={`/djs/${dj.id}/submit`}>
                    <Button size="lg" className="gap-2">
                      <Send className="h-5 w-5" />
                      Submit Track - {formatPrice(dj.submission_price)}
                    </Button>
                  </Link>
                ) : (
                  <Button size="lg" disabled>
                    Not Accepting Submissions
                  </Button>
                )}

                <TipButton
                  toUserId={dj.id}
                  toUserName={dj.full_name}
                  variant="outline"
                  size="lg"
                  contentType="profile"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl">
          {/* Genres */}
          <div className="bg-card rounded-lg border p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Genre Specialties</h2>
            <div className="flex flex-wrap gap-2">
              {dj.genres.map((genre) => (
                <span
                  key={genre}
                  className="px-4 py-2 rounded-lg bg-primary/10 text-primary font-medium"
                >
                  {genre}
                </span>
              ))}
            </div>
          </div>

          {/* Submission Details */}
          <div className="bg-card rounded-lg border p-6">
            <h2 className="text-xl font-semibold mb-4">Submission Details</h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center pb-4 border-b">
                <span className="text-muted-foreground">Submission Fee</span>
                <span className="text-xl font-bold text-primary">
                  {formatPrice(dj.submission_price)}
                </span>
              </div>
              <div className="flex justify-between items-center pb-4 border-b">
                <span className="text-muted-foreground">Average Response Time</span>
                <span className="font-semibold">{dj.avg_response_time_hours} hours</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-muted-foreground">Acceptance Rate</span>
                <span className="font-semibold">{Math.round(dj.acceptance_rate * 100)}%</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
