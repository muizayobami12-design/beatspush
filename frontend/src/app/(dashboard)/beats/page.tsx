'use client';

import { useState, useMemo } from 'react';
import { Plus, Music, Search, Play, MoreVertical, Trash2, Archive, Eye, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Pagination } from '@/components/ui/pagination';
import { usePagination } from '@/hooks/usePagination';
import { useArtistBeats, useDeleteBeat } from '@/hooks/useBeatQueries';
import { useApiError } from '@/hooks/useApiError';
import { useAuthStore } from '@/store/authStore';
import { cn } from '@/lib/utils';

type SortOption = 'recent' | 'popular' | 'earning';

export default function BeatsPage() {
  const { user } = useAuthStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<'all' | 'published' | 'draft' | 'archived'>('all');
  const [sortBy, setSortBy] = useState<SortOption>('recent');
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const { handleError } = useApiError();

  const pagination = usePagination({
    initialPage: 1,
    initialPageSize: 10,
  });

  // Fetch artist's beats from API
  const {
    data: beatsResponse,
    isLoading,
    error,
  } = useArtistBeats(
    user?.id || '',
    pagination.currentPage,
    pagination.pageSize,
    {
      status: statusFilter !== 'all' ? (statusFilter as any) : undefined,
      sort_by: sortBy as any,
    },
    !!user?.id // Only enable if user ID exists
  );

  // Delete beat mutation
  const deleteBeatMutation = useDeleteBeat();

  // Handle errors
  if (error) {
    handleError(error, { customMessage: 'Failed to load your beats. Please try again.' });
  }

  const beats = beatsResponse?.beats || [];
  const filteredBeats = useMemo(() => {
    let filtered = beats;

    // Search filter
    if (searchQuery) {
      filtered = filtered.filter(beat =>
        beat.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        beat.genre.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    return filtered;
  }, [beats, searchQuery]);

  const handleDeleteBeat = async (beatId: string) => {
    if (!confirm('Are you sure you want to delete this beat? This action cannot be undone.')) {
      return;
    }

    try {
      setDeletingId(beatId);
      await deleteBeatMutation.mutateAsync(beatId);
    } catch (err) {
      handleError(err as Error, { customMessage: 'Failed to delete beat. Please try again.' });
    } finally {
      setDeletingId(null);
    }
  };

  // Empty state - no user
  if (!user) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              Please log in to view your beats
            </p>
          </div>
        </div>
      </div>
    );
  }

  // Empty state - no beats
  if (!isLoading && beats.length === 0) {
    return (
      <div className="min-h-screen bg-background">
        <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
          {/* Header */}
          <div className="flex items-center justify-between mb-stack-lg">
            <div>
              <h1 className={cn(
                'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
                'text-on-surface'
              )}>
                My Beats
              </h1>
              <p className={cn(
                'font-body-md text-body-md',
                'text-on-surface-variant mt-2'
              )}>
                Upload and manage your music collection
              </p>
            </div>
            <Link href="/beats/upload">
              <Button className={cn(
                'gap-2',
                'bg-secondary text-on-secondary hover:bg-secondary-fixed'
              )}>
                <Plus className="h-5 w-5" />
                <span className="hidden sm:inline">Upload Beat</span>
                <span className="sm:hidden">Upload</span>
              </Button>
            </Link>
          </div>

          {/* Empty State */}
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <div className={cn(
              'p-6 rounded-lg mb-6 inline-flex',
              'bg-surface-container'
            )}>
              <Music className="h-12 w-12 text-on-surface-variant" />
            </div>
            <h2 className={cn(
              'font-headline-md text-headline-md',
              'text-on-surface mb-2'
            )}>
              No Beats Yet
            </h2>
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant mb-6 max-w-sm mx-auto'
            )}>
              Upload your first beat to start sharing your music with the world
            </p>
            <Link href="/beats/upload">
              <Button className={cn(
                'gap-2 inline-flex',
                'bg-secondary text-on-secondary hover:bg-secondary-fixed'
              )}>
                <Plus className="h-5 w-5" />
                Upload Your First Beat
              </Button>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-8">
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        {/* Header */}
        <div className="flex items-center justify-between mb-stack-lg flex-col md:flex-row gap-4">
          <div>
            <h1 className={cn(
              'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
              'text-on-surface'
            )}>
              My Beats
            </h1>
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant mt-2'
            )}>
              {isLoading ? 'Loading...' : `${filteredBeats.length} beat${filteredBeats.length !== 1 ? 's' : ''}`}
            </p>
          </div>
          <Link href="/beats/upload">
            <Button className={cn(
              'gap-2',
              'bg-secondary text-on-secondary hover:bg-secondary-fixed'
            )}>
              <Plus className="h-5 w-5" />
              <span className="hidden sm:inline">Upload Beat</span>
              <span className="sm:hidden">Upload</span>
            </Button>
          </Link>
        </div>

        {/* Controls */}
        <div className={cn(
          'rounded-lg border ghost-border p-stack-md mb-stack-md',
          'bg-surface-container-low space-y-4'
        )}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Search */}
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-on-surface-variant" />
              <Input
                type="text"
                placeholder="Search beats..."
                value={searchQuery}
                onChange={(e) => {
                  setSearchQuery(e.target.value);
                  pagination.setCurrentPage(1);
                }}
                className={cn(
                  'pl-10',
                  'bg-surface-container border border-outline-variant/30',
                  'text-on-surface placeholder-on-surface-variant/50',
                  'focus:outline-none focus:ring-2 focus:ring-secondary/40'
                )}
              />
            </div>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value as SortOption);
                pagination.setCurrentPage(1);
              }}
              className={cn(
                'px-3 py-2 rounded-lg',
                'bg-surface-container border border-outline-variant/30',
                'text-on-surface font-body-md',
                'focus:outline-none focus:ring-2 focus:ring-secondary/40'
              )}
            >
              <option value="recent">Most Recent</option>
              <option value="popular">Most Popular</option>
              <option value="earning">Highest Earning</option>
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex gap-2 flex-wrap">
            {(['all', 'published', 'draft', 'archived'] as const).map((status) => (
              <button
                key={status}
                onClick={() => {
                  setStatusFilter(status);
                  pagination.setCurrentPage(1);
                }}
                className={cn(
                  'px-4 py-2 rounded-lg font-label-sm text-label-sm',
                  'border transition-all duration-200',
                  statusFilter === status
                    ? 'bg-secondary text-on-secondary border-secondary'
                    : 'bg-surface-container border-outline-variant/30 text-on-surface hover:border-outline-variant/60'
                )}
              >
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Beats Grid */}
        {isLoading ? (
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low flex flex-col items-center justify-center min-h-64'
          )}>
            <Loader2 className="h-8 w-8 text-secondary animate-spin mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              Loading your beats...
            </p>
          </div>
        ) : filteredBeats.length > 0 ? (
          <>
            <div className="space-y-gutter mb-stack-lg">
              {filteredBeats.map((beat) => (
                <div
                  key={beat.id}
                  className={cn(
                    'rounded-lg border ghost-border p-stack-md',
                    'bg-surface-container-low hover:bg-surface-container',
                    'transition-all duration-200 group'
                  )}
                >
                  <div className="flex gap-stack-md items-center">
                    {/* Cover */}
                    <div className={cn(
                      'w-16 h-16 rounded-lg flex-shrink-0',
                      'bg-gradient-to-br from-secondary/20 to-tertiary/20',
                      'border border-outline-variant/20',
                      'flex items-center justify-center'
                    )}>
                      <Music className="h-8 w-8 text-on-surface-variant/50" />
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className={cn(
                          'font-body-md font-semibold',
                          'text-on-surface truncate'
                        )}>
                          {beat.title}
                        </h3>
                        <span className={cn(
                          'px-2 py-1 rounded text-xs font-label-sm',
                          beat.status === 'published'
                            ? 'bg-secondary/20 text-secondary'
                            : beat.status === 'draft'
                            ? 'bg-on-surface-variant/20 text-on-surface-variant'
                            : 'bg-destructive/20 text-destructive'
                        )}>
                          {beat.status.charAt(0).toUpperCase() + beat.status.slice(1)}
                        </span>
                      </div>

                      <div className="flex items-center gap-3 text-xs font-label-sm text-on-surface-variant mb-2">
                        <span>{beat.genre}</span>
                        {beat.bpm && (
                          <>
                            <span>•</span>
                            <span>{beat.bpm} BPM</span>
                          </>
                        )}
                        {beat.key && (
                          <>
                            <span>•</span>
                            <span>{beat.key}</span>
                          </>
                        )}
                      </div>

                      <div className="flex items-center gap-4 text-xs font-label-sm">
                        <div className="flex items-center gap-1">
                          <Eye className="h-3 w-3" />
                          <span className="text-on-surface-variant">{beat.plays.toLocaleString()} plays</span>
                        </div>
                        {beat.downloads > 0 && (
                          <div className="flex items-center gap-1">
                            <span className="text-secondary font-medium">{beat.downloads} downloads</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex items-center gap-2">
                      {beat.status === 'published' && (
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-secondary hover:bg-secondary/10"
                        >
                          <Play className="h-4 w-4" />
                        </Button>
                      )}
                      <button
                        onClick={() => handleDeleteBeat(beat.id)}
                        disabled={deletingId === beat.id}
                        className="p-2 hover:bg-surface-container rounded transition-colors text-destructive hover:text-destructive-dim disabled:opacity-50"
                      >
                        {deletingId === beat.id ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <Trash2 className="h-4 w-4" />
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination - only show if there are more pages */}
            {beatsResponse && beatsResponse.total_pages > 1 && (
              <Pagination
                currentPage={pagination.currentPage}
                totalItems={beatsResponse.total}
                pageSize={pagination.pageSize}
                onPageChange={pagination.setCurrentPage}
              />
            )}
          </>
        ) : (
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <Music className="h-12 w-12 text-on-surface-variant/50 mx-auto mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              {searchQuery ? 'No beats match your search' : 'No beats found. Upload your first beat!'}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
