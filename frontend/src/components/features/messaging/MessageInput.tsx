'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, Paperclip, Smile } from 'lucide-react';
import { VoiceNoteRecorder } from './VoiceNoteRecorder';

interface MessageInputProps {
  onSend: (content: string) => void;
  onTyping?: (isTyping: boolean) => void;
  onFileAttach?: (file: File) => void;
  disabled?: boolean;
  placeholder?: string;
  /** Pre-fill content (used for edit mode) */
  initialValue?: string;
}

export default function MessageInput({
  onSend,
  onTyping,
  onFileAttach,
  disabled = false,
  placeholder = 'Type a message…',
  initialValue = '',
}: MessageInputProps) {
  const [content, setContent] = useState(initialValue);
  const [isTyping, setIsTyping] = useState(false);
  const [showVoiceRecorder, setShowVoiceRecorder] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Sync initialValue when it changes (e.g. switching edit targets)
  useEffect(() => {
    setContent(initialValue);
    textareaRef.current?.focus();
  }, [initialValue]);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
    }
  }, [content]);

  const stopTyping = () => {
    if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
    if (isTyping) {
      setIsTyping(false);
      onTyping?.(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const val = e.target.value;
    setContent(val);

    if (onTyping) {
      if (val.length > 0 && !isTyping) {
        setIsTyping(true);
        onTyping(true);
      }
      if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current);
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(false);
        onTyping(false);
      }, 3000);
    }
  };

  const handleSend = () => {
    const trimmed = content.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setContent('');
    stopTyping();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && onFileAttach) {
      onFileAttach(file);
    }
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  // Cleanup
  useEffect(() => () => { if (typingTimeoutRef.current) clearTimeout(typingTimeoutRef.current); }, []);

  const charCount = content.length;
  const maxChars = 2000;
  const isOverLimit = charCount > maxChars;

  if (showVoiceRecorder) {
    return (
      <VoiceNoteRecorder
        onRecordingComplete={(file) => {
          onFileAttach?.(file);
          setShowVoiceRecorder(false);
        }}
        onCancel={() => setShowVoiceRecorder(false)}
        disabled={disabled}
      />
    );
  }

  return (
    <div className="space-y-1">
      {/* Char counter */}
      {charCount > 0 && (
        <div className="flex justify-end">
          <span className={`text-xs ${isOverLimit ? 'text-destructive' : 'text-muted-foreground'}`}>
            {charCount}/{maxChars}
          </span>
        </div>
      )}

      <div className="flex items-end gap-2">
        {/* File attachment */}
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*,audio/*,application/pdf,.doc,.docx"
          className="hidden"
          onChange={handleFileChange}
        />
        <Button
          variant="ghost"
          size="icon"
          disabled={disabled}
          title="Attach file"
          className="flex-shrink-0"
          onClick={() => fileInputRef.current?.click()}
          type="button"
        >
          <Paperclip className="h-5 w-5" />
        </Button>

        {/* Textarea */}
        <div className="flex-1 relative">
          <Textarea
            ref={textareaRef}
            value={content}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            className="min-h-[44px] max-h-[120px] resize-none pr-10"
            rows={1}
            aria-label="Message input"
          />
          <Button
            variant="ghost"
            size="icon"
            disabled={disabled}
            title="Add emoji"
            className="absolute right-1 bottom-1 h-8 w-8"
            type="button"
          >
            <Smile className="h-4 w-4" />
          </Button>
        </div>

        {/* Voice note */}
        <Button
          variant="ghost"
          size="icon"
          disabled={disabled}
          title="Voice note"
          className="flex-shrink-0"
          onClick={() => setShowVoiceRecorder(true)}
          type="button"
          aria-label="Record voice note"
        >
          🎤
        </Button>

        {/* Send */}
        <Button
          onClick={handleSend}
          disabled={disabled || !content.trim() || isOverLimit}
          size="icon"
          className="flex-shrink-0"
          type="button"
          aria-label="Send message"
        >
          <Send className="h-5 w-5" />
        </Button>
      </div>
    </div>
  );
}
