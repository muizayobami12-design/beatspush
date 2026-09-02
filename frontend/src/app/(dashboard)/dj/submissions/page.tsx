'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, Play, CheckCircle2, XCircle, Clock, Music2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { djSubmissionService, type DJSubmission } from '@/services/djSubmissionService';

export default function DJSubmissionsPage() {
  const [submissions, setSubmissions] = useState<DJSubmission[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  useEffect(() => {
    fetchSubmissions();
  }, [filter]);

  const fetchSubmissions = async () => {
    setIsLoading(true);
    try {
      const response = await djSubmissionService.getSubmissionsForDJ({
        status: filter !== 'all' ? filter : undefined,
      });
      setSubmissions(response.submissions);
    } catch (error) {
      console.error('Failed to fetch submissions:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRespond = async (submissionId: string, action: 'accept' | 'reject') => {
    try {
      await djSubmissionService.respondToSubmission(submissionId, action);
      // Refresh submissions
      fetchSubmissions();
    } catch (error) {
      console.error('Failed to respond:', error);
      alert('Failed to respond to submission');
    }
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'accepted':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'rejected':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'played':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20';
      default:
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
    }
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="gap-2 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
          <h1 className="text-3xl font-bold mb-2">Track Submissions</h1>
          <p className="text-muted-foreground">
            Review and respond to artist track submissions
          </p>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Filters */}
        <div className="flex gap-2 mb-6">
          {['all', 'pending', 'accepted', 'rejected', 'played'].map((status) => (
            <Button
              key={status}
              variant={filter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(status)}
              className="capitalize"
            >
              {status}
            </Button>
          ))}
        </div>

        {/* Submissions List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : submissions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="p-4 rounded-full bg-muted mb-4">
              <Music2 className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No submissions yet</h3>
            <p className="text-muted-foreground max-w-md">
              Artists will submit their tracks here for you to review.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {submissions.map((submission) => (
              <div
                key={submission.id}
                className="bg-card rounded-lg border p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  {/* Track Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-lg font-semibold">{submission.track_title}</h3>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(
                          submission.status
                        )}`}
                      >
                        {submission.status}
                      </span>
                    </div>

                    <p className="text-sm text-muted-foreground mb-2">
                      by <span className="font-medium">{submission.artist_name}</span>
                    </p>

                    {submission.message && (
                      <p className="text-sm mb-3 p-3 rounded-lg bg-muted/50">
                        "{submission.message}"
                      </p>
                    )}

                    <div className="flex items-center gap-4 text-sm text-muted-foreground">
                      <span>Submission Fee: {formatPrice(submission.submission_price)}</span>
                      <span>•</span>
                      <span>
                        {new Date(submission.created_at).toLocaleDateString()}
                      </span>
                    </div>

                    {submission.dj_feedback && (
                      <div className="mt-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                        <p className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">
                          Your Feedback:
                        </p>
                        <p className="text-sm">{submission.dj_feedback}</p>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  {submission.status === 'pending' && (
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-2"
                        onClick={() => handleRespond(submission.id, 'accept')}
                      >
                        <CheckCircle2 className="h-4 w-4" />
                        Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-2 text-red-600 hover:text-red-600"
                        onClick={() => handleRespond(submission.id, 'reject')}
                      >
                        <XCircle className="h-4 w-4" />
                        Reject
                      </Button>
                    </div>
                  )}

                  {submission.status === 'accepted' && (
                    <Button
                      size="sm"
                      variant="outline"
                      className="gap-2"
                      onClick={() =>
                        djSubmissionService.markAsPlayed(submission.id)
                      }
                    >
                      <Play className="h-4 w-4" />
                      Mark as Played
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
