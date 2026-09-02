'use client';

import { useState, useEffect } from 'react';
import { Search, Radio, TrendingUp, Clock, CheckCircle2 } from 'lucide-react';
import { useSearchParams } from 'next/navigation';
import { Input } from '@/components/ui/input';
import { djSubmissionService, type DJ } from '@/services/djSubmissionService';
import { DJCard } from '@/components/features/djs/DJCard';

const GENRES = ['All', 'Afrobeat', 'Hip Hop', 'R&B', 'Amapiano', 'Gospel', 'Dancehall'];

export default function DJsPage() {
  const searchParams = useSearchParams();
  const trackId = searchParams.get('track');
  
  const [djs, setDjs] = useState<DJ[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('All');

  useEffect(() => {
    fetchDJs();
  }, [selectedGenre]);

  const fetchDJs = async () => {
    setIsLoading(true);
    try {
      const response = await djSubmissionService.getDJs({
        genre: selectedGenre !== 'All' ? selectedGenre : undefined,
      });
      setDjs(response.djs);
    } catch (error) {
      console.error('Failed to fetch DJs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredDJs = djs.filter((dj) =>
    searchQuery
      ? dj.full_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        dj.username.toLowerCase().includes(searchQuery.toLowerCase())
      : true
  );

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="mb-4">
            <h1 className="text-3xl font-bold mb-2">DJ Directory</h1>
            <p className="text-muted-foreground">
              Submit your tracks to top DJs and get your music heard
            </p>
            {trackId && (
              <div className="mt-3 p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                <p className="text-sm text-blue-600 dark:text-blue-400">
                  Select a DJ to submit your track
                </p>
              </div>
            )}
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search DJs..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 h-12"
            />
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Genre Filter */}
        <div className="mb-8">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide mb-3">
            Genre Specialty
          </h2>
          <div className="flex flex-wrap gap-2">
            {GENRES.map((genre) => (
              <button
                key={genre}
                onClick={() => setSelectedGenre(genre)}
                className={`px-4 py-2 rounded-full font-medium transition-colors ${
                  selectedGenre === genre
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-muted hover:bg-muted/80'
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>

        {/* Stats Banner */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-card rounded-lg border p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-primary/10">
                <Radio className="h-5 w-5 text-primary" />
              </div>
              <div>
                <p className="text-2xl font-bold">{djs.length}</p>
                <p className="text-sm text-muted-foreground">Active DJs</p>
              </div>
            </div>
          </div>
          <div className="bg-card rounded-lg border p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-green-500/10">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">78%</p>
                <p className="text-sm text-muted-foreground">Avg Response Rate</p>
              </div>
            </div>
          </div>
          <div className="bg-card rounded-lg border p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-blue-500/10">
                <Clock className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">24h</p>
                <p className="text-sm text-muted-foreground">Avg Response Time</p>
              </div>
            </div>
          </div>
        </div>

        {/* DJs Grid */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
            <p className="text-muted-foreground">Loading DJs...</p>
          </div>
        ) : filteredDJs.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="p-4 rounded-full bg-muted mb-4">
              <Radio className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No DJs found</h3>
            <p className="text-muted-foreground max-w-md">
              Try adjusting your search or genre filter.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredDJs.map((dj) => (
              <DJCard key={dj.id} dj={dj} trackId={trackId} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
