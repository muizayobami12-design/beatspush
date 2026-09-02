'use client';

import { useState, useRef } from 'react';
import { Search, X, ChevronUp, ChevronDown } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';
import type { Message } from '@/services/messagingService';

interface MessageSearchProps {
  messages: Message[];
  /** Called when a match is focused so the parent can scroll to it */
  onFocusMessage: (messageId: string) => void;
  onClose: () => void;
}

/**
 * MessageSearch — searches within the loaded message list (task 23.2).
 * Highlights matching messages and lets the user navigate prev/next.
 */
export function MessageSearch({ messages, onFocusMessage, onClose }: MessageSearchProps) {
  const [query, setQuery] = useState('');
  const [matchIndex, setMatchIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const lq = query.trim().toLowerCase();
  const matches = lq
    ? messages.filter((m) => !m.deleted_at && m.content.toLowerCase().includes(lq))
    : [];

  const navigate = (dir: 1 | -1) => {
    if (matches.length === 0) return;
    const next = (matchIndex + dir + matches.length) % matches.length;
    setMatchIndex(next);
    onFocusMessage(matches[next].id);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setMatchIndex(0);
    if (e.target.value.trim()) {
      const first = messages.find(
        (m) => !m.deleted_at && m.content.toLowerCase().includes(e.target.value.trim().toLowerCase())
      );
      if (first) onFocusMessage(first.id);
    }
  };

  return (
    <div className="flex items-center gap-2 px-4 py-2 border-b bg-muted/30">
      <Search className="h-4 w-4 text-muted-foreground flex-shrink-0" />
      <Input
        ref={inputRef}
        autoFocus
        value={query}
        onChange={handleChange}
        placeholder="Search messages…"
        className="h-8 border-0 bg-transparent focus-visible:ring-0 p-0 text-sm"
        aria-label="Search messages"
      />
      {query && (
        <span className="text-xs text-muted-foreground flex-shrink-0">
          {matches.length > 0 ? `${matchIndex + 1}/${matches.length}` : '0 results'}
        </span>
      )}
      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => navigate(-1)} disabled={matches.length === 0} aria-label="Previous match">
        <ChevronUp className="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => navigate(1)} disabled={matches.length === 0} aria-label="Next match">
        <ChevronDown className="h-4 w-4" />
      </Button>
      <Button variant="ghost" size="icon" className="h-7 w-7" onClick={onClose} aria-label="Close search">
        <X className="h-4 w-4" />
      </Button>
    </div>
  );
}

export default MessageSearch;
