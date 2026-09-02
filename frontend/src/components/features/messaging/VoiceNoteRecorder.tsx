'use client';

import { useState, useRef, useEffect } from 'react';
import { Mic, Square, Send, X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface VoiceNoteRecorderProps {
  onRecordingComplete: (file: File) => void;
  onCancel: () => void;
  disabled?: boolean;
}

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${s.toString().padStart(2, '0')}`;
}

/**
 * VoiceNoteRecorder — captures audio via MediaRecorder API.
 * Shows a recording timer with animated indicator.
 * On stop, produces a .webm File and calls onRecordingComplete.
 * Task 20.3
 */
export function VoiceNoteRecorder({ onRecordingComplete, onCancel, disabled }: VoiceNoteRecorderProps) {
  const [phase, setPhase] = useState<'idle' | 'recording' | 'processing'>('idle');
  const [elapsed, setElapsed] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopTimer();
      streamRef.current?.getTracks().forEach((t) => t.stop());
    };
  }, []);

  const stopTimer = () => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = null;
    }
  };

  const startRecording = async () => {
    setError(null);
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
        ? 'audio/webm;codecs=opus'
        : 'audio/webm';

      const recorder = new MediaRecorder(stream, { mimeType });
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: mimeType });
        const file = new File([blob], `voice-note-${Date.now()}.webm`, { type: mimeType });
        setPhase('idle');
        onRecordingComplete(file);
      };

      recorder.start(200); // collect chunks every 200ms
      setPhase('recording');
      setElapsed(0);

      timerRef.current = setInterval(() => setElapsed((n) => n + 1), 1000);
    } catch (err) {
      setError('Microphone access denied. Please allow microphone permissions.');
    }
  };

  const stopRecording = () => {
    stopTimer();
    setPhase('processing');
    mediaRecorderRef.current?.stop();
    streamRef.current?.getTracks().forEach((t) => t.stop());
  };

  const cancel = () => {
    stopTimer();
    mediaRecorderRef.current?.stream.getTracks().forEach((t) => t.stop());
    mediaRecorderRef.current = null;
    streamRef.current = null;
    setPhase('idle');
    setElapsed(0);
    onCancel();
  };

  if (error) {
    return (
      <div className="flex items-center gap-2 text-sm text-destructive">
        <span>{error}</span>
        <Button variant="ghost" size="sm" onClick={() => setError(null)}>Dismiss</Button>
      </div>
    );
  }

  if (phase === 'idle') {
    return (
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={startRecording}
        disabled={disabled}
        title="Record voice note"
        aria-label="Record voice note"
      >
        <Mic className="h-5 w-5" />
      </Button>
    );
  }

  if (phase === 'processing') {
    return (
      <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-muted text-sm">
        <Loader2 className="h-4 w-4 animate-spin" />
        <span>Processing...</span>
      </div>
    );
  }

  // recording phase
  return (
    <div className="flex items-center gap-3 px-3 py-1 rounded-full bg-destructive/10 border border-destructive/20">
      {/* Pulse indicator */}
      <span className="relative flex h-3 w-3">
        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-destructive opacity-75" />
        <span className="relative inline-flex h-3 w-3 rounded-full bg-destructive" />
      </span>
      <span className="text-sm font-mono text-destructive min-w-[3rem]">{formatTime(elapsed)}</span>

      {/* Cancel */}
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="h-7 w-7"
        onClick={cancel}
        aria-label="Cancel recording"
      >
        <X className="h-4 w-4" />
      </Button>

      {/* Send */}
      <Button
        type="button"
        size="icon"
        className="h-7 w-7"
        onClick={stopRecording}
        aria-label="Stop and send voice note"
      >
        <Send className="h-4 w-4" />
      </Button>
    </div>
  );
}

export default VoiceNoteRecorder;
