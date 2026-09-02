'use client';

import { useEffect, useRef, useState } from 'react';
import { Play, Pause, SkipBack, SkipForward, Volume2, VolumeX, X, Music2 } from 'lucide-react';
import { useAudioStore } from '@/store/audioStore';
import { Button } from '@/components/ui/button';
import Link from 'next/link';

export function AudioPlayer() {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isMuted, setIsMuted] = useState(false);
  
  const {
    currentBeat,
    isPlaying,
    volume,
    currentTime,
    duration,
    togglePlayPause,
    seekTo,
    setVolume,
    nextBeat,
    previousBeat,
    setCurrentTime,
    setDuration,
    pauseBeat,
  } = useAudioStore();

  // Sync audio element with store
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.play().catch((error) => {
        console.error('Failed to play audio:', error);
        pauseBeat();
      });
    } else {
      audio.pause();
    }
  }, [isPlaying, pauseBeat]);

  // Update current beat audio source
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !currentBeat) return;

    audio.src = currentBeat.audioUrl;
    audio.load();
    
    if (isPlaying) {
      audio.play().catch((error) => {
        console.error('Failed to play audio:', error);
        pauseBeat();
      });
    }
  }, [currentBeat, isPlaying, pauseBeat]);

  // Set volume
  useEffect(() => {
    const audio = audioRef.current;
    if (audio) {
      audio.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  // Handle time update
  const handleTimeUpdate = () => {
    const audio = audioRef.current;
    if (audio) {
      setCurrentTime(audio.currentTime);
    }
  };

  // Handle duration loaded
  const handleLoadedMetadata = () => {
    const audio = audioRef.current;
    if (audio) {
      setDuration(audio.duration);
    }
  };

  // Handle ended
  const handleEnded = () => {
    nextBeat();
  };

  // Handle progress bar click
  const handleProgressClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const audio = audioRef.current;
    if (!audio || !duration) return;

    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;
    
    audio.currentTime = newTime;
    seekTo(newTime);
  };

  // Format time
  const formatTime = (seconds: number) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Handle volume change
  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    setIsMuted(false);
  };

  const toggleMute = () => {
    setIsMuted(!isMuted);
  };

  // Don't render if no beat is loaded
  if (!currentBeat) return null;

  const progress = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <>
      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
      />

      {/* Player UI */}
      <div className="fixed bottom-0 left-0 right-0 z-50 bg-card border-t shadow-lg">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center gap-4">
            {/* Beat Info */}
            <div className="flex items-center gap-3 flex-1 min-w-0">
              <Link href={`/beats/${currentBeat.id}`} className="flex-shrink-0">
                <div className="w-14 h-14 rounded-md bg-gradient-to-br from-primary/20 to-primary/5 flex items-center justify-center overflow-hidden">
                  {currentBeat.thumbnailUrl ? (
                    <img
                      src={currentBeat.thumbnailUrl}
                      alt={currentBeat.title}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <Music2 className="h-6 w-6 text-muted-foreground" />
                  )}
                </div>
              </Link>
              
              <div className="flex-1 min-w-0">
                <Link href={`/beats/${currentBeat.id}`}>
                  <h4 className="font-semibold text-sm truncate hover:text-primary transition-colors">
                    {currentBeat.title}
                  </h4>
                </Link>
                <p className="text-xs text-muted-foreground truncate">
                  {currentBeat.creator.fullName}
                </p>
              </div>
            </div>

            {/* Controls */}
            <div className="flex flex-col items-center gap-2 flex-1 max-w-2xl">
              <div className="flex items-center gap-2">
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={previousBeat}
                  className="h-8 w-8"
                >
                  <SkipBack className="h-4 w-4" />
                </Button>

                <Button
                  size="icon"
                  onClick={togglePlayPause}
                  className="h-10 w-10 rounded-full"
                >
                  {isPlaying ? (
                    <Pause className="h-5 w-5" fill="currentColor" />
                  ) : (
                    <Play className="h-5 w-5" fill="currentColor" />
                  )}
                </Button>

                <Button
                  size="icon"
                  variant="ghost"
                  onClick={nextBeat}
                  className="h-8 w-8"
                >
                  <SkipForward className="h-4 w-4" />
                </Button>
              </div>

              {/* Progress Bar */}
              <div className="flex items-center gap-2 w-full">
                <span className="text-xs text-muted-foreground tabular-nums w-10 text-right">
                  {formatTime(currentTime)}
                </span>
                <div
                  className="flex-1 h-1 bg-secondary rounded-full cursor-pointer group"
                  onClick={handleProgressClick}
                >
                  <div
                    className="h-full bg-primary rounded-full transition-all group-hover:bg-primary/80 relative"
                    style={{ width: `${progress}%` }}
                  >
                    <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 bg-primary rounded-full opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
                <span className="text-xs text-muted-foreground tabular-nums w-10">
                  {formatTime(duration)}
                </span>
              </div>
            </div>

            {/* Volume & Close */}
            <div className="flex items-center gap-3 flex-1 justify-end">
              <div className="hidden md:flex items-center gap-2">
                <Button
                  size="icon"
                  variant="ghost"
                  onClick={toggleMute}
                  className="h-8 w-8"
                >
                  {isMuted || volume === 0 ? (
                    <VolumeX className="h-4 w-4" />
                  ) : (
                    <Volume2 className="h-4 w-4" />
                  )}
                </Button>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.01"
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="w-24 h-1 bg-secondary rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
                />
              </div>

              <Button
                size="icon"
                variant="ghost"
                onClick={pauseBeat}
                className="h-8 w-8"
              >
                <X className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Spacer to prevent content from being hidden behind player */}
      <div className="h-20" />
    </>
  );
}
