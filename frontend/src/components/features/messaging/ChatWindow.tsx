'use client';

import { useState, useEffect, useRef } from 'react';
import Image from 'next/image';
import { Send, Paperclip, MoreVertical, Loader2, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/hooks/useToast';
import { useWebSocket } from '@/hooks/useWebSocket';
import { messagingService } from '@/services/messagingService';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import type { Message } from '@/types';

interface ChatWindowProps {
  conversationId: string;
  participant: {
    id: string;
    name: string;
    avatar?: string;
    username: string;
  };
  currentUserId: string;
  onBack?: () => void;
}

export function ChatWindow({
  conversationId,
  participant,
  currentUserId,
  onBack,
}: ChatWindowProps) {
  const { toast } = useToast();
  const { send, subscribe, isConnected } = useWebSocket();
  const [inputValue, setInputValue] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const typingTimeoutRef = useRef<NodeJS.Timeout>();

  // Load messages on mount
  useEffect(() => {
    loadMessages();
  }, [conversationId]);

  // Subscribe to WebSocket events
  useEffect(() => {
    // Subscribe to new messages
    const unsubscribeMessage = subscribe('message', (data: any) => {
      if (data.conversation_id === conversationId) {
        const newMessage: Message = {
          id: data.id || Date.now().toString(),
          conversationId: data.conversation_id,
          senderId: data.sender_id,
          sender: {
            id: data.sender_id,
            email: participant.username + '@beatpush.com',
            fullName: participant.name,
            username: participant.username,
            role: 'artist',
            isVerified: false,
            followerCount: 0,
            followingCount: 0,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
          },
          content: data.content,
          status: data.is_read ? 'read' : 'delivered',
          createdAt: data.created_at || new Date().toISOString(),
        };
        setMessages((prev) => [...prev, newMessage]);
        scrollToBottom();

        // Mark as read if not sent by current user
        if (data.sender_id !== currentUserId) {
          messagingService.markAsRead(conversationId);
        }
      }
    });

    // Subscribe to typing indicators
    const unsubscribeTyping = subscribe('typing', (data: any) => {
      if (data.conversation_id === conversationId && data.user_id !== currentUserId) {
        setIsTyping(true);
        
        // Clear typing after 3 seconds
        if (typingTimeoutRef.current) {
          clearTimeout(typingTimeoutRef.current);
        }
        typingTimeoutRef.current = setTimeout(() => {
          setIsTyping(false);
        }, 3000);
      }
    });

    // Subscribe to message read receipts
    const unsubscribeRead = subscribe('message_read', (data: any) => {
      if (data.conversation_id === conversationId) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === data.message_id ? { ...msg, isRead: true } : msg
          )
        );
      }
    });

    return () => {
      unsubscribeMessage();
      unsubscribeTyping();
      unsubscribeRead();
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [conversationId, currentUserId, subscribe]);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadMessages = async () => {
    try {
      setIsLoading(true);
      const response = await messagingService.getMessages(conversationId);
      setMessages(response.messages);

      // Mark as read
      await messagingService.markAsRead(conversationId);
    } catch (error) {
      console.error('Failed to load messages:', error);
      toast({
        title: 'Failed to load messages',
        description: 'Please try refreshing the page',
        variant: 'error',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;

    const messageContent = inputValue.trim();
    setInputValue('');
    setIsSending(true);

    try {
      // Try WebSocket first
      if (isConnected()) {
        send('send_message', {
          conversation_id: conversationId,
          content: messageContent,
          timestamp: new Date().toISOString(),
        });
      } else {
        // Fallback to HTTP
        const newMessage = await messagingService.sendMessage({
          conversationId,
          content: messageContent,
        });
        setMessages((prev) => [...prev, newMessage]);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast({
        title: 'Failed to send message',
        description: 'Please try again',
        variant: 'error',
      });
      // Restore message on failure
      setInputValue(messageContent);
    } finally {
      setIsSending(false);
    }
  };

  const handleTyping = () => {
    if (isConnected()) {
      send('typing', {
        conversation_id: conversationId,
        user_id: currentUserId,
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b">
        <div className="flex items-center space-x-3">
          {/* Back Button (Mobile) */}
          {onBack && (
            <Button
              variant="ghost"
              size="icon"
              onClick={onBack}
              className="md:hidden flex-shrink-0"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
          )}
          
          <div className="relative w-10 h-10 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden">
            {participant.avatar ? (
              <Image
                src={participant.avatar}
                alt={participant.name}
                width={40}
                height={40}
                className="object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-white font-semibold text-sm">
                {participant?.name?.charAt(0)?.toUpperCase() || 'U'}
              </div>
            )}
            {/* Online indicator */}
            {isConnected() && (
              <div className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 border-2 border-background rounded-full" />
            )}
          </div>
          <div>
            <h3 className="font-semibold text-foreground">{participant.name}</h3>
            <p className="text-xs text-muted-foreground">
              {isTyping ? 'Typing...' : `@${participant.username}`}
            </p>
          </div>
        </div>

        <Button variant="ghost" size="icon">
          <MoreVertical className="w-5 h-5" />
        </Button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-muted-foreground">
            No messages yet. Start the conversation!
          </div>
        ) : (
          messages.map((message, index) => {
            const isOwn = message.senderId === currentUserId;
            const showAvatar =
              index === 0 ||
              messages[index - 1]?.senderId !== message.senderId;

            return (
              <div
                key={message.id}
                className={cn(
                  'flex items-end space-x-2',
                  isOwn && 'flex-row-reverse space-x-reverse'
                )}
              >
                {/* Avatar */}
                {showAvatar && !isOwn && (
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#667eea] to-[#764ba2] overflow-hidden flex-shrink-0">
                    {participant.avatar ? (
                      <Image
                        src={participant.avatar}
                        alt={participant.name}
                        width={32}
                        height={32}
                        className="object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-white text-xs font-semibold">
                        {participant?.name?.charAt(0)?.toUpperCase() || 'U'}
                      </div>
                    )}
                  </div>
                )}
                
                {!showAvatar && !isOwn && <div className="w-8" />}

                {/* Message Bubble */}
                <div
                  className={cn(
                    'max-w-[70%] rounded-2xl px-4 py-2',
                    isOwn
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-foreground'
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">
                    {message.content}
                  </p>
                  <p
                    className={cn(
                      'text-xs mt-1',
                      isOwn
                        ? 'text-primary-foreground/70'
                        : 'text-muted-foreground'
                    )}
                  >
                    {formatDistanceToNow(new Date(message.createdAt), {
                      addSuffix: true,
                    })}
                    {isOwn && message.status === 'read' && ' • Read'}
                  </p>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSubmit}
        className="px-6 py-4 border-t"
      >
        <div className="flex items-center space-x-2">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            className="flex-shrink-0"
          >
            <Paperclip className="w-5 h-5" />
          </Button>

          <Input
            value={inputValue}
            onChange={(e) => {
              setInputValue(e.target.value);
              handleTyping();
            }}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSubmit(e);
              }
            }}
            placeholder="Type a message..."
            className="flex-1"
            disabled={isSending}
          />

          <Button
            type="submit"
            size="icon"
            disabled={!inputValue.trim() || isSending}
            className="flex-shrink-0"
          >
            {isSending ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </Button>
        </div>
        
        {!isConnected() && (
          <p className="text-xs text-amber-600 mt-2">
            Real-time messaging unavailable. Messages will be sent via HTTP.
          </p>
        )}
      </form>
    </div>
  );
}

