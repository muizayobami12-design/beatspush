'use client';

import React, { useState, useEffect } from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';
import { Loader2, ChevronDown } from 'lucide-react';
import { useToast } from '@/hooks/useToast';
import { BlockedUsers } from './BlockedUsers';

type MessageFilter = 'everyone' | 'followers' | 'verified' | 'none';

interface MessagingSettingsData {
  message_filter: MessageFilter;
  read_receipts_enabled: boolean;
  typing_indicators_enabled: boolean;
}

const MESSAGE_FILTER_OPTIONS: { value: MessageFilter; label: string; description: string }[] = [
  { value: 'everyone', label: 'Everyone', description: 'Anyone can send you messages' },
  { value: 'followers', label: 'Followers only', description: 'Only people you follow can message you' },
  { value: 'verified', label: 'Verified users', description: 'Only verified accounts can message you' },
  { value: 'none', label: 'No one', description: 'Disable direct messages entirely' },
];

/**
 * MessagingSettings - Privacy and notification settings for direct messages.
 * Allows users to control who can message them, read receipts, and typing indicators.
 */
export function MessagingSettings() {
  const { toast } = useToast();
  const [settings, setSettings] = useState<MessagingSettingsData>({
    message_filter: 'everyone',
    read_receipts_enabled: true,
    typing_indicators_enabled: true,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadSettings() {
      try {
        const response = await fetch('/api/v1/messaging/settings');
        if (response.ok) {
          const data = await response.json();
          setSettings(data);
        }
      } catch (error) {
        console.error('Failed to load settings:', error);
      } finally {
        setLoading(false);
      }
    }
    loadSettings();
  }, []);

  const handleSave = async () => {
    setSaving(true);
    try {
      const response = await fetch('/api/v1/messaging/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings),
      });

      if (response.ok) {
        toast({ title: 'Settings saved', variant: 'success' });
      } else {
        throw new Error('Failed to save');
      }
    } catch (error) {
      toast({ title: 'Failed to save settings', variant: 'error' });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-8 p-4">
      {/* Privacy Settings Section */}
      <div>
        <div>
          <h3 className="text-lg font-semibold mb-1">Message Privacy</h3>
          <p className="text-sm text-muted-foreground">Control who can send you direct messages.</p>
        </div>

        {/* Message Filter */}
        <div className="space-y-3 mt-6">
          <Label className="text-sm font-medium">Who can message you?</Label>
          <div className="space-y-2">
            {MESSAGE_FILTER_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => setSettings((s) => ({ ...s, message_filter: option.value }))}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  settings.message_filter === option.value
                    ? 'border-primary bg-primary/5'
                    : 'border-border hover:bg-muted/50'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium">{option.label}</p>
                    <p className="text-xs text-muted-foreground mt-0.5">{option.description}</p>
                  </div>
                  {settings.message_filter === option.value && (
                    <div className="w-2 h-2 rounded-full bg-primary" />
                  )}
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Read Receipts */}
        <div className="flex items-center justify-between mt-6">
          <div>
            <Label htmlFor="read-receipts" className="text-sm font-medium">Read receipts</Label>
            <p className="text-xs text-muted-foreground mt-0.5">
              Let others know when you've read their messages
            </p>
          </div>
          <Switch
            id="read-receipts"
            checked={settings.read_receipts_enabled}
            onCheckedChange={(checked) =>
              setSettings((s) => ({ ...s, read_receipts_enabled: checked }))
            }
          />
        </div>

        {/* Typing Indicators */}
        <div className="flex items-center justify-between mt-6">
          <div>
            <Label htmlFor="typing-indicators" className="text-sm font-medium">Typing indicators</Label>
            <p className="text-xs text-muted-foreground mt-0.5">
              Show others when you're typing a message
            </p>
          </div>
          <Switch
            id="typing-indicators"
            checked={settings.typing_indicators_enabled}
            onCheckedChange={(checked) =>
              setSettings((s) => ({ ...s, typing_indicators_enabled: checked }))
            }
          />
        </div>

        <Button onClick={handleSave} disabled={saving} className="w-full mt-6">
          {saving ? <><Loader2 className="w-4 h-4 mr-2 animate-spin" />Saving...</> : 'Save Settings'}
        </Button>
      </div>

      {/* Divider */}
      <div className="border-t" />

      {/* Blocked Users Section */}
      <BlockedUsers />
    </div>
  );
}

export default MessagingSettings;
