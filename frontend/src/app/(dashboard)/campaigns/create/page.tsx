'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateCampaign } from '@/hooks/useCampaigns';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { ArrowLeft, Sparkles } from 'lucide-react';
import Link from 'next/link';

export default function CreateCampaignPage() {
  const router = useRouter();
  const createCampaign = useCreateCampaign();

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    contentType: 'promo' as any,
    platforms: [] as string[],
    scheduledFor: '',
  });

  const platforms = [
    { id: 'instagram', label: 'Instagram' },
    { id: 'twitter', label: 'Twitter/X' },
    { id: 'facebook', label: 'Facebook' },
    { id: 'tiktok', label: 'TikTok' },
  ];

  const handlePlatformToggle = (platformId: string) => {
    setFormData((prev) => ({
      ...prev,
      platforms: prev.platforms.includes(platformId)
        ? prev.platforms.filter((p) => p !== platformId)
        : [...prev.platforms, platformId],
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!formData.name || formData.platforms.length === 0) {
      alert('Please fill in campaign name and select at least one platform');
      return;
    }

    const campaignData = {
      name: formData.name,
      description: formData.description || undefined,
      contentType: formData.contentType,
      platforms: formData.platforms,
      scheduledFor: formData.scheduledFor || undefined,
    };

    createCampaign.mutate(campaignData, {
      onSuccess: (data) => {
        router.push(`/campaigns/${data.id}`);
      },
    });
  };

  return (
    <div className="container mx-auto py-8 px-4 max-w-3xl">
      {/* Header */}
      <div className="mb-8">
        <Link href="/campaigns">
          <Button variant="ghost" className="mb-4">
            <ArrowLeft className="h-4 w-4 mr-2" />
            Back to Campaigns
          </Button>
        </Link>
        <h1 className="text-3xl font-bold mb-2">Create New Campaign</h1>
        <p className="text-muted-foreground">
          Launch a promotional campaign across your social media platforms
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Basic Info */}
        <Card>
          <CardHeader>
            <CardTitle>Campaign Details</CardTitle>
            <CardDescription>Basic information about your campaign</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label htmlFor="name">Campaign Name *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="e.g., Summer Release 2026"
                required
              />
            </div>

            <div>
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Describe your campaign goals and strategy..."
                rows={3}
              />
            </div>

            <div>
              <Label htmlFor="contentType">Campaign Type</Label>
              <Select
                value={formData.contentType}
                onValueChange={(value: any) => setFormData({ ...formData, contentType: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="new_release">New Release</SelectItem>
                  <SelectItem value="promo">Promotional</SelectItem>
                  <SelectItem value="announcement">Announcement</SelectItem>
                  <SelectItem value="engagement">Engagement</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label htmlFor="scheduledFor">Schedule (Optional)</Label>
              <Input
                id="scheduledFor"
                type="datetime-local"
                value={formData.scheduledFor}
                onChange={(e) => setFormData({ ...formData, scheduledFor: e.target.value })}
              />
              <p className="text-xs text-muted-foreground mt-1">
                Leave empty to save as draft
              </p>
            </div>
          </CardContent>
        </Card>

        {/* Platform Selection */}
        <Card>
          <CardHeader>
            <CardTitle>Target Platforms *</CardTitle>
            <CardDescription>Select where you want to publish this campaign</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-4">
              {platforms.map((platform) => (
                <div key={platform.id} className="flex items-center space-x-2">
                  <Checkbox
                    id={platform.id}
                    checked={formData.platforms.includes(platform.id)}
                    onCheckedChange={() => handlePlatformToggle(platform.id)}
                  />
                  <Label htmlFor={platform.id} className="cursor-pointer">
                    {platform.label}
                  </Label>
                </div>
              ))}
            </div>
            {formData.platforms.length === 0 && (
              <p className="text-xs text-destructive mt-2">
                Please select at least one platform
              </p>
            )}
          </CardContent>
        </Card>

        {/* AI Content Generation */}
        <Card className="border-purple-500/50 bg-gradient-to-r from-purple-500/10 to-blue-500/10">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-purple-500" />
              AI Content Generation
            </CardTitle>
            <CardDescription>
              After creating your campaign, AI will help you generate platform-specific content
            </CardDescription>
          </CardHeader>
        </Card>

        {/* Actions */}
        <div className="flex justify-end gap-4">
          <Link href="/campaigns">
            <Button type="button" variant="outline">
              Cancel
            </Button>
          </Link>
          <Button 
            type="submit" 
            disabled={createCampaign.isPending || !formData.name || formData.platforms.length === 0}
          >
            {createCampaign.isPending ? 'Creating...' : 'Create Campaign'}
          </Button>
        </div>
      </form>
    </div>
  );
}
