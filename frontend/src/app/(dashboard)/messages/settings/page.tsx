'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import messagingService, { MessageSettings, BlockedUser } from '@/services/messagingService';
import { Button } from '@/components/ui/button';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { ArrowLeft, Shield, Bell, Eye, UserX } from 'lucide-react';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatDistanceToNow } from 'date-fns';

export default function MessagingSettingsPage() {
  const router = useRouter();
  const [settings, setSettings] = useState<MessageSettings | null>(null);
  const [blockedUsers, setBlockedUsers] = useState<BlockedUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSettings();
    loadBlockedUsers();
  }, []);

  const loadSettings = async () => {
    try {
      const result = await messagingService.getSettings();
      console.log('Settings loaded:', result);
      setSettings(result);
      setError(null);
    } catch (error: any) {
      console.error('Failed to load settings:', error);
      console.error('Error response:', error.response?.data);
      console.error('Error status:', error.response?.status);
      
      const errorMsg = error.response?.data?.detail || error.message || 'Failed to load settings';
      setError(`Settings Error: ${errorMsg}. Using defaults.`);
      
      // Set default settings if API fails
      setSettings({
        id: 'temp',
        user_id: 'temp',
        message_filter: 'everyone',
        read_receipts_enabled: true,
        typing_indicators_enabled: true
      });
    }
  };

  const loadBlockedUsers = async () => {
    try {
      const result = await messagingService.getBlockedUsers({ page: 1, page_size: 50 });
      console.log('Blocked users loaded:', result);
      setBlockedUsers(result.blocked_users);
    } catch (error: any) {
      console.error('Failed to load blocked users:', error);
      console.error('Error response:', error.response?.data);
      setBlockedUsers([]); // Set empty array if API fails
    } finally {
      setLoading(false);
    }
  };

  const handleUpdateSettings = async (updates: Partial<MessageSettings>) => {
    if (!settings) return;

    try {
      setSaving(true);
      const newSettings = await messagingService.updateSettings(updates);
      setSettings(newSettings);
    } catch (error) {
      console.error('Failed to update settings:', error);
      alert('Failed to update settings');
    } finally {
      setSaving(false);
    }
  };

  const handleUnblock = async (userId: string) => {
    if (!window.confirm('Unblock this user?')) return;

    try {
      await messagingService.unblockUser(userId);
      setBlockedUsers(prev => prev.filter(u => u.blocked_user.id !== userId));
    } catch (error) {
      console.error('Failed to unblock user:', error);
      alert('Failed to unblock user');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">Loading settings...</p>
        </div>
      </div>
    );
  }

  if (!settings) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <p className="text-destructive">Failed to load settings</p>
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
          <h1 className="text-2xl font-bold">Messaging Settings</h1>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-yellow-500/10 border border-yellow-500/20 rounded-lg">
            <p className="text-sm text-yellow-600 dark:text-yellow-400">{error}</p>
            <p className="text-xs text-muted-foreground mt-1">
              The backend messaging API may not be fully set up. Settings will work once the backend is configured.
            </p>
          </div>
        )}

        <div className="space-y-6">
          {/* Privacy Settings */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="h-5 w-5" />
              <h2 className="text-lg font-semibold">Privacy</h2>
            </div>

            <div className="space-y-6">
              {/* Message Filter */}
              <div>
                <Label className="text-base mb-3 block">Who can message you</Label>
                <RadioGroup
                  value={settings.message_filter}
                  onValueChange={(value) =>
                    handleUpdateSettings({
                      message_filter: value as 'everyone' | 'followers' | 'verified' | 'none'
                    })
                  }
                  disabled={saving}
                  className="space-y-3"
                >
                  <div className="flex items-center space-x-3">
                    <RadioGroupItem value="everyone" id="everyone" />
                    <Label htmlFor="everyone" className="font-normal cursor-pointer">
                      <div>
                        <p className="font-medium">Everyone</p>
                        <p className="text-sm text-muted-foreground">
                          Anyone can send you messages
                        </p>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3">
                    <RadioGroupItem value="followers" id="followers" />
                    <Label htmlFor="followers" className="font-normal cursor-pointer">
                      <div>
                        <p className="font-medium">Followers only</p>
                        <p className="text-sm text-muted-foreground">
                          Only people you follow can message you
                        </p>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3">
                    <RadioGroupItem value="verified" id="verified" />
                    <Label htmlFor="verified" className="font-normal cursor-pointer">
                      <div>
                        <p className="font-medium">Verified users only</p>
                        <p className="text-sm text-muted-foreground">
                          Only verified users can message you
                        </p>
                      </div>
                    </Label>
                  </div>
                  <div className="flex items-center space-x-3">
                    <RadioGroupItem value="none" id="none" />
                    <Label htmlFor="none" className="font-normal cursor-pointer">
                      <div>
                        <p className="font-medium">No one</p>
                        <p className="text-sm text-muted-foreground">
                          Disable all incoming messages
                        </p>
                      </div>
                    </Label>
                  </div>
                </RadioGroup>
              </div>
            </div>
          </div>

          {/* Notification Settings */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="flex items-center gap-2 mb-4">
              <Bell className="h-5 w-5" />
              <h2 className="text-lg font-semibold">Notifications</h2>
            </div>

            <div className="space-y-4">
              {/* Read Receipts */}
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <Label htmlFor="read-receipts" className="text-base cursor-pointer">
                    Read receipts
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Let others know when you've read their messages
                  </p>
                </div>
                <Switch
                  id="read-receipts"
                  checked={settings.read_receipts_enabled}
                  onCheckedChange={(checked) =>
                    handleUpdateSettings({ read_receipts_enabled: checked })
                  }
                  disabled={saving}
                />
              </div>

              {/* Typing Indicators */}
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <Label htmlFor="typing-indicators" className="text-base cursor-pointer">
                    Typing indicators
                  </Label>
                  <p className="text-sm text-muted-foreground">
                    Show others when you're typing
                  </p>
                </div>
                <Switch
                  id="typing-indicators"
                  checked={settings.typing_indicators_enabled}
                  onCheckedChange={(checked) =>
                    handleUpdateSettings({ typing_indicators_enabled: checked })
                  }
                  disabled={saving}
                />
              </div>
            </div>
          </div>

          {/* Blocked Users */}
          <div className="border rounded-lg p-6 bg-card">
            <div className="flex items-center gap-2 mb-4">
              <UserX className="h-5 w-5" />
              <h2 className="text-lg font-semibold">Blocked Users</h2>
            </div>

            {blockedUsers.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                You haven't blocked anyone yet
              </p>
            ) : (
              <div className="space-y-3">
                {blockedUsers.map((blocked) => (
                  <div
                    key={blocked.id}
                    className="flex items-center justify-between p-3 border rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar className="h-10 w-10">
                        <AvatarImage src={blocked.blocked_user.avatar_url} />
                        <AvatarFallback>
                          {blocked.blocked_user.username.slice(0, 2).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{blocked.blocked_user.full_name}</p>
                        <p className="text-sm text-muted-foreground">
                          @{blocked.blocked_user.username}
                        </p>
                        {blocked.blocked_at && (
                          <p className="text-xs text-muted-foreground">
                            Blocked {formatDistanceToNow(new Date(blocked.blocked_at), { addSuffix: true })}
                          </p>
                        )}
                      </div>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleUnblock(blocked.blocked_user.id)}
                    >
                      Unblock
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Save Indicator */}
          {saving && (
            <div className="text-center text-sm text-muted-foreground">
              Saving changes...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
