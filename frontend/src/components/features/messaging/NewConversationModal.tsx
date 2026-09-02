'use client';

import React, { useState } from 'react';
import { Search, Loader2, X, UserRound } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Modal } from '@/components/ui/Modal';
import { useCreateConversation } from '@/hooks/useConversations';
import { apiClient } from '@/lib/api/client';

interface UserResult {
  id: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  role?: string;
}

interface NewConversationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConversationCreated: (conversationId: string) => void;
}

export function NewConversationModal({
  isOpen,
  onClose,
  onConversationCreated,
}: NewConversationModalProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<UserResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [selectedUser, setSelectedUser] = useState<UserResult | null>(null);
  const [searchError, setSearchError] = useState<string | null>(null);

  const createConversation = useCreateConversation();

  const handleSearch = async () => {
    const q = query.trim();
    if (!q) return;

    setIsSearching(true);
    setSearchError(null);
    setResults([]);

    try {
      // Try exact username lookup via profiles endpoint
      const response = await apiClient.get<UserResult>(`/profiles/${encodeURIComponent(q)}`);
      setResults([response.data]);
    } catch {
      try {
        // Fallback: search by username prefix if profiles supports ?search
        const response = await apiClient.get<{ users: UserResult[] }>('/users/search', {
          params: { q, limit: 10 },
        });
        setResults(response.data.users ?? []);
      } catch {
        setSearchError('User not found. Try entering an exact username.');
      }
    } finally {
      setIsSearching(false);
    }
  };

  const handleCreate = async () => {
    if (!selectedUser) return;
    try {
      // mutateAsync expects a plain recipientId string
      const conversation = await createConversation.mutateAsync(selectedUser.id);
      onConversationCreated(conversation.id);
      handleClose();
    } catch {
      // error toast handled in the hook
    }
  };

  const handleClose = () => {
    setQuery('');
    setResults([]);
    setSelectedUser(null);
    setSearchError(null);
    onClose();
  };

  const initials = (name: string) =>
    name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="New Conversation">
      <div className="space-y-4">
        {selectedUser ? (
          /* ── Selected user chip ── */
          <div className="flex items-center justify-between p-3 bg-accent rounded-lg">
            <div className="flex items-center gap-3">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center text-white text-sm font-semibold overflow-hidden flex-shrink-0">
                {selectedUser.avatar_url ? (
                  // eslint-disable-next-line @next/next/no-img-element
                  <img src={selectedUser.avatar_url} alt={selectedUser.full_name} className="w-full h-full object-cover" />
                ) : (
                  initials(selectedUser.full_name || selectedUser.username)
                )}
              </div>
              <div>
                <p className="font-medium text-sm">{selectedUser.full_name}</p>
                <p className="text-xs text-muted-foreground">@{selectedUser.username}</p>
              </div>
            </div>
            <Button size="icon" variant="ghost" onClick={() => setSelectedUser(null)} aria-label="Remove selected user">
              <X className="h-4 w-4" />
            </Button>
          </div>
        ) : (
          /* ── Search ── */
          <div className="space-y-2">
            <label className="text-sm font-medium">Find a user</label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
                <Input
                  type="text"
                  placeholder="Enter username..."
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="pl-9"
                  autoFocus
                />
              </div>
              <Button onClick={handleSearch} disabled={isSearching || !query.trim()}>
                {isSearching ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Search'}
              </Button>
            </div>

            {/* Results */}
            {searchError && (
              <p className="text-sm text-muted-foreground text-center py-4">{searchError}</p>
            )}
            {results.length > 0 && (
              <div className="border rounded-lg divide-y max-h-56 overflow-y-auto">
                {results.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => setSelectedUser(user)}
                    className="w-full p-3 flex items-center gap-3 hover:bg-accent transition-colors text-left"
                  >
                    <div className="h-9 w-9 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center text-white text-xs font-semibold flex-shrink-0 overflow-hidden">
                      {user.avatar_url ? (
                        // eslint-disable-next-line @next/next/no-img-element
                        <img src={user.avatar_url} alt={user.full_name} className="w-full h-full object-cover" />
                      ) : (
                        initials(user.full_name || user.username)
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-sm truncate">{user.full_name}</p>
                      <p className="text-xs text-muted-foreground">@{user.username} {user.role ? `· ${user.role}` : ''}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}
            {!isSearching && !searchError && results.length === 0 && query && (
              <div className="flex flex-col items-center py-6 text-muted-foreground">
                <UserRound className="h-8 w-8 mb-2 opacity-40" />
                <p className="text-sm">No results — press Search to look up</p>
              </div>
            )}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="outline" onClick={handleClose}>Cancel</Button>
          <Button
            onClick={handleCreate}
            disabled={!selectedUser || createConversation.isPending}
          >
            {createConversation.isPending ? (
              <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Starting...</>
            ) : (
              'Start Conversation'
            )}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default NewConversationModal;
