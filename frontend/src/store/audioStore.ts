import { create } from 'zustand';
import type { Beat } from '@/types';

interface AudioState {
  currentBeat: Beat | null;
  isPlaying: boolean;
  volume: number;
  currentTime: number;
  duration: number;
  queue: Beat[];
  queueIndex: number;
  
  // Actions
  playBeat: (beat: Beat) => void;
  pauseBeat: () => void;
  togglePlayPause: () => void;
  seekTo: (time: number) => void;
  setVolume: (volume: number) => void;
  nextBeat: () => void;
  previousBeat: () => void;
  addToQueue: (beat: Beat) => void;
  removeFromQueue: (beatId: string) => void;
  clearQueue: () => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
}

export const useAudioStore = create<AudioState>((set, get) => ({
  currentBeat: null,
  isPlaying: false,
  volume: 0.8,
  currentTime: 0,
  duration: 0,
  queue: [],
  queueIndex: -1,

  playBeat: (beat) => {
    const { queue } = get();
    const existingIndex = queue.findIndex((b) => b.id === beat.id);
    
    if (existingIndex === -1) {
      // Add to queue if not exists
      set({ queue: [...queue, beat], queueIndex: queue.length });
    } else {
      set({ queueIndex: existingIndex });
    }
    
    set({ currentBeat: beat, isPlaying: true, currentTime: 0 });
  },

  pauseBeat: () => set({ isPlaying: false }),

  togglePlayPause: () => set((state) => ({ isPlaying: !state.isPlaying })),

  seekTo: (time) => set({ currentTime: time }),

  setVolume: (volume) => set({ volume: Math.max(0, Math.min(1, volume)) }),

  nextBeat: () => {
    const { queue, queueIndex } = get();
    if (queueIndex < queue.length - 1) {
      const nextIndex = queueIndex + 1;
      const nextBeat = queue[nextIndex];
      set({ currentBeat: nextBeat, queueIndex: nextIndex, currentTime: 0, isPlaying: true });
    }
  },

  previousBeat: () => {
    const { queue, queueIndex, currentTime } = get();
    
    // If more than 3 seconds in, restart current beat
    if (currentTime > 3) {
      set({ currentTime: 0 });
      return;
    }
    
    // Otherwise go to previous beat
    if (queueIndex > 0) {
      const prevIndex = queueIndex - 1;
      const prevBeat = queue[prevIndex];
      set({ currentBeat: prevBeat, queueIndex: prevIndex, currentTime: 0, isPlaying: true });
    }
  },

  addToQueue: (beat) => {
    const { queue } = get();
    const exists = queue.find((b) => b.id === beat.id);
    if (!exists) {
      set({ queue: [...queue, beat] });
    }
  },

  removeFromQueue: (beatId) => {
    const { queue, queueIndex, currentBeat } = get();
    const newQueue = queue.filter((b) => b.id !== beatId);
    
    // If removed beat is current, stop playing
    if (currentBeat?.id === beatId) {
      set({ queue: newQueue, currentBeat: null, isPlaying: false, queueIndex: -1 });
    } else {
      // Adjust queue index if needed
      const newIndex = currentBeat
        ? newQueue.findIndex((b) => b.id === currentBeat.id)
        : -1;
      set({ queue: newQueue, queueIndex: newIndex });
    }
  },

  clearQueue: () => set({ queue: [], queueIndex: -1, currentBeat: null, isPlaying: false }),

  setCurrentTime: (time) => set({ currentTime: time }),

  setDuration: (duration) => set({ duration }),
}));
