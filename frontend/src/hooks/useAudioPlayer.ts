import { useState, useEffect, useRef, useCallback } from 'react';
import { WaveSurfer, createWaveSurfer, destroyWaveSurfer, loadAudio } from '@/lib/audio/wavesurfer';

export interface AudioPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isLoading: boolean;
  error: string | null;
}

export interface AudioPlayerControls {
  play: () => void;
  pause: () => void;
  stop: () => void;
  seek: (time: number) => void;
  setVolume: (volume: number) => void;
  toggle: () => void;
}

export interface UseAudioPlayerOptions {
  autoPlay?: boolean;
  volume?: number;
  onEnd?: () => void;
  onError?: (error: string) => void;
}

export function useAudioPlayer(
  containerRef: React.RefObject<HTMLElement>,
  options: UseAudioPlayerOptions = {}
) {
  const { autoPlay = false, volume: initialVolume = 0.8, onEnd, onError } = options;

  const wavesurferRef = useRef<WaveSurfer | null>(null);
  const [state, setState] = useState<AudioPlayerState>({
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    volume: initialVolume,
    isLoading: false,
    error: null,
  });

  // Initialize WaveSurfer
  useEffect(() => {
    if (!containerRef.current) return;

    const wavesurfer = createWaveSurfer({
      container: containerRef.current,
    });

    wavesurfer.setVolume(initialVolume);
    wavesurferRef.current = wavesurfer;

    // Event listeners
    wavesurfer.on('ready', () => {
      setState((prev) => ({
        ...prev,
        duration: wavesurfer.getDuration(),
        isLoading: false,
      }));

      if (autoPlay) {
        wavesurfer.play();
      }
    });

    wavesurfer.on('play', () => {
      setState((prev) => ({ ...prev, isPlaying: true }));
    });

    wavesurfer.on('pause', () => {
      setState((prev) => ({ ...prev, isPlaying: false }));
    });

    wavesurfer.on('finish', () => {
      setState((prev) => ({ ...prev, isPlaying: false, currentTime: 0 }));
      onEnd?.();
    });

    wavesurfer.on('audioprocess', () => {
      setState((prev) => ({
        ...prev,
        currentTime: wavesurfer.getCurrentTime(),
      }));
    });

    wavesurfer.on('error', (error) => {
      const errorMessage = error instanceof Error ? error.message : 'Audio playback error';
      setState((prev) => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
      }));
      onError?.(errorMessage);
    });

    return () => {
      destroyWaveSurfer(wavesurfer);
    };
  }, [containerRef, initialVolume, autoPlay, onEnd, onError]);

  // Load audio file
  const load = useCallback(async (url: string) => {
    if (!wavesurferRef.current) return;

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      await loadAudio(wavesurferRef.current, url);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to load audio';
      setState((prev) => ({
        ...prev,
        error: errorMessage,
        isLoading: false,
      }));
      onError?.(errorMessage);
    }
  }, [onError]);

  // Play
  const play = useCallback(() => {
    wavesurferRef.current?.play();
  }, []);

  // Pause
  const pause = useCallback(() => {
    wavesurferRef.current?.pause();
  }, []);

  // Stop
  const stop = useCallback(() => {
    wavesurferRef.current?.stop();
    setState((prev) => ({ ...prev, currentTime: 0, isPlaying: false }));
  }, []);

  // Seek to time
  const seek = useCallback((time: number) => {
    if (!wavesurferRef.current) return;
    const duration = wavesurferRef.current.getDuration();
    const progress = time / duration;
    wavesurferRef.current.seekTo(progress);
  }, []);

  // Set volume (0-1)
  const setVolume = useCallback((volume: number) => {
    const clampedVolume = Math.max(0, Math.min(1, volume));
    wavesurferRef.current?.setVolume(clampedVolume);
    setState((prev) => ({ ...prev, volume: clampedVolume }));
  }, []);

  // Toggle play/pause
  const toggle = useCallback(() => {
    if (state.isPlaying) {
      pause();
    } else {
      play();
    }
  }, [state.isPlaying, play, pause]);

  const controls: AudioPlayerControls = {
    play,
    pause,
    stop,
    seek,
    setVolume,
    toggle,
  };

  return {
    ...state,
    ...controls,
    load,
    wavesurfer: wavesurferRef.current,
  };
}
