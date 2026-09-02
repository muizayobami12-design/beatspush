'use client';

import { useEffect, useState } from 'react';
import { Music2 } from 'lucide-react';
import { BeatCard } from './BeatCard';
import { BeatGridSkeleton } from './BeatCardSkeleton';
import { beatService } from '@/services/beatService';
import type { BeatFilters, Beat } from '@/types';

// Mock data as fallback
const MOCK_BEATS = [
  {
    id: '1',
    title: 'Afro Vibes',
    creatorId: 'prod1',
    creator: {
      id: 'prod1',
      email: 'producer@example.com',
      fullName: 'DJ Kizz',
      role: 'producer' as const,
      isVerified: true,
      followerCount: 1250,
      followingCount: 340,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    audioUrl: '/audio/sample-beat.mp3',
    thumbnailUrl: null, // Using fallback gradient
    genre: 'Afrobeat',
    tempo: 120,
    key: 'C minor',
    duration: 180,
    price: 5000, // ₦5,000
    tags: ['afrobeat', 'danceable', 'party'],
    playCount: 2340,
    favoriteCount: 156,
    isFavorited: false,
    isPurchased: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '2',
    title: 'Lagos Nights',
    creatorId: 'prod2',
    creator: {
      id: 'prod2',
      email: 'producer2@example.com',
      fullName: 'Beatmaker Pro',
      role: 'producer' as const,
      isVerified: true,
      followerCount: 890,
      followingCount: 210,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    audioUrl: '/audio/sample-beat-2.mp3',
    thumbnailUrl: null,
    genre: 'Hip Hop',
    tempo: 95,
    key: 'F# major',
    duration: 195,
    price: 8000, // ₦8,000
    tags: ['hiphop', 'chill', 'smooth'],
    playCount: 1580,
    favoriteCount: 98,
    isFavorited: false,
    isPurchased: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '3',
    title: 'Amapiano Wave',
    creatorId: 'prod3',
    creator: {
      id: 'prod3',
      email: 'producer3@example.com',
      fullName: 'Piano King',
      role: 'producer' as const,
      isVerified: true,
      followerCount: 3200,
      followingCount: 450,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    audioUrl: '/audio/sample-beat-3.mp3',
    thumbnailUrl: null,
    genre: 'Amapiano',
    tempo: 112,
    key: 'G major',
    duration: 210,
    price: 12000, // ₦12,000
    tags: ['amapiano', 'piano', 'dance'],
    playCount: 4520,
    favoriteCount: 312,
    isFavorited: true,
    isPurchased: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '4',
    title: 'Trap Energy',
    creatorId: 'prod4',
    creator: {
      id: 'prod4',
      email: 'producer4@example.com',
      fullName: 'Trap Master',
      role: 'producer' as const,
      isVerified: false,
      followerCount: 620,
      followingCount: 180,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    audioUrl: '/audio/sample-beat-4.mp3',
    thumbnailUrl: null,
    genre: 'Trap',
    tempo: 140,
    key: 'D minor',
    duration: 165,
    price: 6500, // ₦6,500
    tags: ['trap', 'hard', '808'],
    playCount: 980,
    favoriteCount: 67,
    isFavorited: false,
    isPurchased: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '5',
    title: 'Gospel Praise',
    creatorId: 'prod5',
    creator: {
      id: 'prod5',
      email: 'producer5@example.com',
      fullName: 'Worship Sounds',
      role: 'producer' as const,
      isVerified: true,
      followerCount: 1800,
      followingCount: 290,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    audioUrl: '/audio/sample-beat-5.mp3',
    thumbnailUrl: null,
    genre: 'Gospel',
    tempo: 80,
    key: 'A major',
    duration: 240,
    price: 4000, // ₦4,000
    tags: ['gospel', 'worship', 'uplifting'],
    playCount: 1240,
    favoriteCount: 145,
    isFavorited: false,
    isPurchased: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  {
    id: '6',
    title: 'R&B Smooth',
    creatorId: 'prod1',
    creator: {
      id: 'prod1',
      email: 'producer@example.com',
      fullName: 'DJ Kizz',
      role: 'producer' as const,
      isVerified: true,
      followerCount: 1250,
      followingCount: 340,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    audioUrl: '/audio/sample-beat-6.mp3',
    thumbnailUrl: null,
    genre: 'R&B',
    tempo: 85,
    key: 'Eb major',
    duration: 190,
    price: 7500, // ₦7,500
    tags: ['rnb', 'smooth', 'romantic'],
    playCount: 1670,
    favoriteCount: 189,
    isFavorited: false,
    isPurchased: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
];

interface BeatGridProps {
  filters: Partial<BeatFilters>;
}

export function BeatGrid({ filters }: BeatGridProps) {
  const [beats, setBeats] = useState<Beat[]>(MOCK_BEATS);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBeats = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await beatService.getBeats({
          search: filters.search,
          genre: filters.genre,
          tempoMin: filters.tempoMin,
          tempoMax: filters.tempoMax,
          priceMin: filters.priceMin,
          priceMax: filters.priceMax,
          sortBy: filters.sortBy,
        });
        setBeats(response.beats);
      } catch (err) {
        console.error('Failed to fetch beats:', err);
        setError('Failed to load beats. Using demo data.');
        // Keep mock data on error
      } finally {
        setIsLoading(false);
      }
    };

    fetchBeats();
  }, [filters]);

  // Filter beats based on filters (for mock data fallback)
  let filteredBeats = [...beats];

  // Search filter
  if (filters.search) {
    const searchLower = filters.search.toLowerCase();
    filteredBeats = filteredBeats.filter(
      (beat) =>
        beat.title.toLowerCase().includes(searchLower) ||
        beat.creator.fullName.toLowerCase().includes(searchLower) ||
        beat.tags.some((tag) => tag.toLowerCase().includes(searchLower))
    );
  }

  // Genre filter
  if (filters.genre && filters.genre.length > 0) {
    filteredBeats = filteredBeats.filter((beat) => filters.genre!.includes(beat.genre));
  }

  // Price filter
  if (filters.priceMin !== undefined) {
    filteredBeats = filteredBeats.filter((beat) => beat.price >= filters.priceMin!);
  }
  if (filters.priceMax !== undefined) {
    filteredBeats = filteredBeats.filter((beat) => beat.price <= filters.priceMax!);
  }

  // Tempo filter
  if (filters.tempoMin !== undefined) {
    filteredBeats = filteredBeats.filter((beat) => beat.tempo >= filters.tempoMin!);
  }
  if (filters.tempoMax !== undefined) {
    filteredBeats = filteredBeats.filter((beat) => beat.tempo <= filters.tempoMax!);
  }

  // Sorting
  switch (filters.sortBy) {
    case 'newest':
      filteredBeats.sort(
        (a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
      );
      break;
    case 'popular':
      filteredBeats.sort((a, b) => b.playCount - a.playCount);
      break;
    case 'price_asc':
      filteredBeats.sort((a, b) => a.price - b.price);
      break;
    case 'price_desc':
      filteredBeats.sort((a, b) => b.price - a.price);
      break;
  }

  if (isLoading) {
    return <BeatGridSkeleton count={6} />;
  }

  if (filteredBeats.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="p-4 rounded-full bg-muted mb-4">
          <Music2 className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-xl font-semibold mb-2">No beats found</h3>
        <p className="text-muted-foreground max-w-md">
          Try adjusting your filters or search terms to find more beats.
        </p>
      </div>
    );
  }

  return (
    <div>
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
          <p className="text-sm text-yellow-600 dark:text-yellow-400">{error}</p>
        </div>
      )}
      
      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-muted-foreground">
          Showing <span className="font-semibold text-foreground">{filteredBeats.length}</span>{' '}
          beat{filteredBeats.length !== 1 ? 's' : ''}
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
        {filteredBeats.map((beat) => (
          <BeatCard key={beat.id} beat={beat} />
        ))}
      </div>
    </div>
  );
}
