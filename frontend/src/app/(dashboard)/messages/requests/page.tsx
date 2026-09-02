'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import messagingService, { Conversation } from '@/services/messagingService';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { ArrowLeft, Check, X, Inbox } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export default function MessageRequestsPage() {
  const router = useRouter();
  const [requests, setRequests] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [processingId, setProcessingId] = useState<string | null>(null);

  useEffect(() => {
    loadRequests();
  }, []);

  const loadRequests = async () => {
    try {
      setLoading(true);
      const result = await messagingService.listMessageRequests({
        page: 1,
        page_size: 50
      });
      setRequests(result.conversations);
    } catch (error) {
      console.error('Failed to load requests:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (conversationId: string) => {
    try {
      setProcessingId(conversationId);
      await messagingService.acceptMessageRequest(conversationId);
      
      // Remove from list and navigate to conversation
      setRequests(prev => prev.filter(r => r.id !== conversationId));
      router.push(`/messages?conversation=${conversationId}`);
    } catch (error) {
      console.error('Failed to accept request:', error);
      alert('Failed to accept request');
    } finally {
      setProcessingId(null);
    }
  };

  const handleDecline = async (conversationId: string) => {
    if (!window.confirm('Decline this message request?')) return;

    try {
      setProcessingId(conversationId);
      await messagingService.declineMessageRequest(conversationId);
      
      // Remove from list
      setRequests(prev => prev.filter(r => r.id !== conversationId));
    } catch (error) {
      console.error('Failed to decline request:', error);
      alert('Failed to decline request');
    } finally {
      setProcessingId(null);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading requests...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => router.back()}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold">Message Requests</h1>
            <p className="text-sm text-muted-foreground">
              {requests.length} pending {requests.length === 1 ? 'request' : 'requests'}
            </p>
          </div>
        </div>

        {/* Requests List */}
        {requests.length === 0 ? (
          <div className="text-center py-12">
            <Inbox className="h-16 w-16 text-muted-foreground mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">No message requests</h2>
            <p className="text-muted-foreground">
              When someone who doesn't follow you sends a message,
              <br />
              it will appear here as a request
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {requests.map((request) => {
              const sender = request.participants[0];
              const isProcessing = processingId === request.id;

              return (
                <div
                  key={request.id}
                  className="border rounded-lg p-6 bg-card hover:shadow-md transition-shadow"
                >
                  {/* Sender Info */}
                  <div className="flex items-start gap-4 mb-4">
                    <Avatar className="h-14 w-14 flex-shrink-0">
                      <AvatarImage src={sender?.avatar_url} />
                      <AvatarFallback>
                        {sender?.username?.slice(0, 2).toUpperCase() || 'U'}
                      </AvatarFallback>
                    </Avatar>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">
                          {sender?.full_name || sender?.username || 'Unknown User'}
                        </h3>
                        {sender?.user_type && (
                          <Badge variant="secondary" className="text-xs">
                            {sender.user_type}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-1">
                        @{sender?.username}
                      </p>
                      {request.last_activity_at && (
                        <p className="text-xs text-muted-foreground">
                          {formatDistanceToNow(new Date(request.last_activity_at), {
                            addSuffix: true
                          })}
                        </p>
                      )}
                    </div>
                  </div>

                  {/* Last Message Preview */}
                  {request.last_message && (
                    <div className="mb-4 p-3 bg-muted rounded-lg">
                      <p className="text-sm">{request.last_message.content}</p>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2">
                    <Button
                      onClick={() => handleAccept(request.id)}
                      disabled={isProcessing}
                      className="flex-1"
                    >
                      <Check className="mr-2 h-4 w-4" />
                      Accept
                    </Button>
                    <Button
                      variant="outline"
                      onClick={() => handleDecline(request.id)}
                      disabled={isProcessing}
                      className="flex-1"
                    >
                      <X className="mr-2 h-4 w-4" />
                      Decline
                    </Button>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Info Box */}
        <div className="mt-8 p-4 border rounded-lg bg-muted/50">
          <h3 className="font-semibold mb-2">About Message Requests</h3>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• Message requests come from people who don't follow you</li>
            <li>• Accept requests to allow ongoing conversations</li>
            <li>• Declined requests won't notify the sender</li>
            <li>• You can change your message filter in settings</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
