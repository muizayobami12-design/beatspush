'use client';

import { useState, useEffect } from 'react';
import { Music, Search, Plus, TrendingUp, Clock, Heart } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { trackService, type Track } from '@/services/trackService';
import { useAuthStore } from '@/store/authStore';
import { TrackCard } from '@/components/features/tracks/TrackCard';

const GENRES = ['All', 'Afrobeat', 'Hip Hop', 'R&B', 'Amapiano', 'Gospel', 'Pop', 'Dancehall'];

export default function TracksPage() {
  const { user } = useAuthStore();
  const [tracks, setTracks] = useState<Track[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedGenre, setSelectedGenre] = useState('All');

  useEffect(() => {
    fetchTracks();
  }, [selectedGenre]);

  const fetchTracks = async () => {
    setIsLoading(true);
    try {
      const response = await trackService.getTracks({
        genre: selectedGenre !== 'All' ? selectedGenre : undefined,
      });
      setTracks(response.tracks);
    } catch (error) {
      console.error('Failed to fetch tracks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredTracks = tracks.filter((track) =>
    searchQuery
      ? track.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        track.artist_name.toLowerCase().includes(searchQuery.toLowerCase())
      : true
  );

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold mb-2">Songs & Tracks</h1>
              <p className="text-muted-foreground">
                Discover and stream music from talented artists
              </p>
            </div>
            {(user?.role === 'artist' || user?.role === 'dj') && (
              <Link href="/tracks/upload">
                <Button size="lg" className="gap-2">
                  <Plus className="h-5 w-5" />
                  {user?.role === 'dj' ? 'Upload Mix' : 'Upload Track'}
                </Button>
              </Link>
            )}
          </div>

          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
            <Input
              type="text"
              placeholder="Search tracks or artists..."
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
            Genre
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

        {/* Tracks Grid */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mb-4"></div>
            <p className="text-muted-foreground">Loading tracks...</p>
          </div>
        ) : filteredTracks.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="p-4 rounded-full bg-muted mb-4">
              <Music className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No tracks found</h3>
            <p className="text-muted-foreground max-w-md">
              Try adjusting your search or genre filter.
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filteredTracks.map((track) => (
              <TrackCard key={track.id} track={track} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
