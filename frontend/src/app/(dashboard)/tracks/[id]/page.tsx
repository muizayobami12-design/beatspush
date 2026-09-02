'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { notFound } from 'next/navigation';
import { ArrowLeft, Play, Pause, Download, Clock, Crown, TrendingUp } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { trackService, type Track } from '@/services/trackService';
import { useAudioStore } from '@/store/audioStore';
import { TipButton } from '@/components/shared/TipButton';
import LikeButton from '@/components/features/social/LikeButton';
import ShareButton from '@/components/features/social/ShareButton';
import CommentsSection from '@/components/features/social/CommentsSection';
import FollowButton from '@/components/features/social/FollowButton';

export default function TrackDetailPage() {
  const params = useParams();
  const trackId = params.id as string;
  
  const [track, setTrack] = useState<Track | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [notFoundError, setNotFoundError] = useState(false);
  
  const { currentTrack, isPlaying, play, pause } = useAudioStore();
  const isThisPlaying = currentTrack?.id === trackId && isPlaying;

  useEffect(() => {
    fetchTrack();
  }, [trackId]);

  const fetchTrack = async () => {
    setIsLoading(true);
    try {
      const data = await trackService.getTrackById(trackId);
      if (!data) {
        setNotFoundError(true);
      } else {
        setTrack(data);
      }
    } catch (error) {
      console.error('Failed to fetch track:', error);
      setNotFoundError(true);
    } finally {
      setIsLoading(false);
    }
  };

  // Properly handle 404 for missing tracks
  if (notFoundError && !isLoading) {
    notFound();
  }

  const handlePlayPause = async () => {
    if (!track) return;

    if (isThisPlaying) {
      pause();
    } else {
      play({
        id: track.id,
        title: track.title,
        artist: track.artist_name,
        audioUrl: track.audio_url,
        coverUrl: track.cover_art_url,
        duration: track.duration,
      });
      
      await trackService.playTrack(track.id);
    }
  };

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

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

  if (!track) {
    notFound();
  }

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="bg-gradient-to-b from-primary/20 to-background">
        <div className="container mx-auto px-4 py-6">
          <Link href="/tracks">
            <Button variant="ghost" size="sm" className="gap-2 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to Tracks
            </Button>
          </Link>

          <div className="flex flex-col md:flex-row gap-8 items-start md:items-center">
            {/* Cover Art */}
            <div className="w-64 h-64 rounded-lg overflow-hidden bg-gradient-to-br from-primary/30 to-primary/10 flex-shrink-0 shadow-2xl">
              {track.cover_art_url ? (
                <img
                  src={track.cover_art_url}
                  alt={track.title}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Play className="h-24 w-24 text-muted-foreground opacity-30" />
                </div>
              )}
            </div>

            {/* Track Info */}
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-3">
                <span className="px-3 py-1 rounded-full bg-primary/20 text-primary text-sm font-semibold">
                  TRACK
                </span>
                {track.is_premium && (
                  <Crown className="h-5 w-5 text-yellow-500" />
                )}
              </div>
              
              <h1 className="text-4xl md:text-5xl font-bold mb-4">{track.title}</h1>
              
              <p className="text-xl text-muted-foreground mb-6">
                by {track.artist_name}
              </p>

              {/* Stats */}
              <div className="flex items-center gap-6 text-sm mb-8">
                <span className="flex items-center gap-1">
                  <Play className="h-4 w-4" />
                  {track.play_count.toLocaleString()} plays
                </span>
                <span className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  {formatDuration(track.duration)}
                </span>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap items-center gap-3">
                <Button
                  size="lg"
                  onClick={handlePlayPause}
                  className="gap-2"
                >
                  {isThisPlaying ? (
                    <>
                      <Pause className="h-5 w-5" fill="currentColor" />
                      Pause
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5" fill="currentColor" />
                      Play
                    </>
                  )}
                </Button>

                <LikeButton
                  contentType="track"
                  contentId={track.id}
                  initialLikes={track.like_count}
                  size="lg"
                  showCount={true}
                />

                <FollowButton
                  userId={track.artist_user_id}
                  userName={track.artist_name}
                  size="lg"
                />

                <TipButton
                  toUserId={track.artist_user_id}
                  toUserName={track.artist_name}
                  variant="outline"
                  size="lg"
                  contentType="track"
                  contentId={track.id}
                />

                <ShareButton
                  contentType="track"
                  contentId={track.id}
                  title={track.title}
                  size="lg"
                  variant="ghost"
                  showText={false}
                />

                {track.is_premium && !track.is_purchased && track.price && (
                  <Button size="lg" variant="default" className="ml-auto gap-2">
                    <Download className="h-5 w-5" />
                    Buy {formatPrice(track.price)}
                  </Button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl">
          {/* Details */}
          <div className="bg-card rounded-lg border p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Track Details</h2>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">Genre</p>
                <p className="font-semibold">{track.genre}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Duration</p>
                <p className="font-semibold">{formatDuration(track.duration)}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">Released</p>
                <p className="font-semibold">
                  {new Date(track.created_at).toLocaleDateString()}
                </p>
              </div>
              {track.is_premium && track.price && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">Price</p>
                  <p className="font-semibold text-primary">{formatPrice(track.price)}</p>
                </div>
              )}
            </div>
          </div>

          {/* Submit to DJ */}
          <div className="bg-card rounded-lg border p-6 mb-6">
            <h2 className="text-xl font-semibold mb-2">Submit to DJs</h2>
            <p className="text-muted-foreground mb-4">
              Get this track heard by top DJs in Nigeria
            </p>
            <Link href={`/djs?track=${track.id}`}>
              <Button variant="outline" className="gap-2">
                <TrendingUp className="h-4 w-4" />
                Find DJs to Submit
              </Button>
            </Link>
          </div>

          {/* Comments Section */}
          <CommentsSection
            contentType="track"
            contentId={track.id}
            className="bg-card rounded-lg border p-6"
          />
        </div>
      </div>
    </div>
  );
}
