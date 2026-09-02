'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import messagingService from '@/services/messagingService';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { ArrowLeft, Search, User } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';

interface UserSearchResult {
  id: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  user_type?: string;
}

export default function NewMessagePage() {
  const router = useRouter();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<UserSearchResult[]>([]);
  const [selectedUser, setSelectedUser] = useState<UserSearchResult | null>(null);
  const [message, setMessage] = useState('');
  const [sending, setSending] = useState(false);
  const [searching, setSearching] = useState(false);

  // Search users using backend endpoint
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    try {
      setSearching(true);
      // Call backend user search endpoint
      const response = await fetch(`/api/v1/users/search?q=${encodeURIComponent(searchQuery)}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setSearchResults(data.results || data);
    } catch (error) {
      console.error('Search failed:', error);
      // Fallback to mock data if API fails
      const mockResults: UserSearchResult[] = [
        {
          id: '1',
          username: 'djkhaleed',
          full_name: 'DJ Khaleed',
          user_type: 'dj'
        },
        {
          id: '2',
          username: 'producer_ace',
          full_name: 'Ace Beats',
          user_type: 'producer'
        }
      ];
      setSearchResults(mockResults);
    } finally {
      setSearching(false);
    }
  };

  const handleSendMessage = async () => {
    if (!selectedUser || !message.trim()) return;

    try {
      setSending(true);
      
      // Create conversation and send message
      const conversation = await messagingService.createConversation(selectedUser.id);
      
      await messagingService.sendMessage({
        conversation_id: conversation.id,
        content: message.trim()
      });

      // Navigate to conversation
      router.push(`/messages?conversation=${conversation.id}`);
    } catch (error) {
      console.error('Failed to send message:', error);
      alert('Failed to send message. Please try again.');
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-2xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.back()}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-2xl font-bold">New Message</h1>
        </div>

        {/* User Selection */}
        {!selectedUser ? (
          <div className="space-y-4">
            <div>
              <Label htmlFor="search">Search Users</Label>
              <div className="flex gap-2 mt-2">
                <Input
                  id="search"
                  type="text"
                  placeholder="Search by username or name..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button onClick={handleSearch} disabled={searching}>
                  <Search className="h-4 w-4 mr-2" />
                  Search
                </Button>
              </div>
            </div>

            {/* Search Results */}
            {searchResults.length > 0 && (
              <div className="border rounded-lg divide-y">
                <div className="p-3 bg-muted">
                  <p className="text-sm font-medium">Search Results</p>
                </div>
                {searchResults.map((user) => (
                  <button
                    key={user.id}
                    onClick={() => setSelectedUser(user)}
                    className="w-full p-4 flex items-center gap-3 hover:bg-accent transition-colors text-left"
                  >
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={user.avatar_url} />
                      <AvatarFallback>
                        {user.username.slice(0, 2).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold">{user.full_name}</span>
                        {user.user_type && (
                          <Badge variant="secondary" className="text-xs">
                            {user.user_type}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">@{user.username}</p>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {searching && (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-2"></div>
                <p className="text-sm text-muted-foreground">Searching...</p>
              </div>
            )}

            {searchResults.length === 0 && searchQuery && !searching && (
              <div className="text-center py-8 text-muted-foreground">
                <User className="h-12 w-12 mx-auto mb-2 opacity-50" />
                <p>No users found</p>
                <p className="text-sm">Try a different search term</p>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {/* Selected User */}
            <div className="border rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Avatar className="h-12 w-12">
                    <AvatarImage src={selectedUser.avatar_url} />
                    <AvatarFallback>
                      {selectedUser.username.slice(0, 2).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{selectedUser.full_name}</span>
                      {selectedUser.user_type && (
                        <Badge variant="secondary" className="text-xs">
                          {selectedUser.user_type}
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">@{selectedUser.username}</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => {
                    setSelectedUser(null);
                    setMessage('');
                  }}
                >
                  Change
                </Button>
              </div>
            </div>

            {/* Message Input */}
            <div>
              <Label htmlFor="message">Message</Label>
              <Textarea
                id="message"
                placeholder="Type your message..."
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                className="mt-2 min-h-[120px]"
                maxLength={2000}
              />
              <div className="flex justify-between items-center mt-2">
                <span className="text-xs text-muted-foreground">
                  {message.length}/2000
                </span>
              </div>
            </div>

            {/* Send Button */}
            <div className="flex gap-2">
              <Button
                variant="outline"
                onClick={() => router.back()}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                onClick={handleSendMessage}
                disabled={sending || !message.trim()}
                className="flex-1"
              >
                {sending ? 'Sending...' : 'Send Message'}
              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
