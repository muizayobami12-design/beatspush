'use client';

import { useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import {
  Link2,
  Plus,
  Copy,
  Download,
  Trash2,
  QrCode,
  TrendingUp,
  MapPin,
  Globe,
  Calendar,
  Eye,
  MousePointerClick,
  Share2,
  Filter,
  Search,
  Edit,
  ExternalLink,
} from 'lucide-react';
import { useToast } from '@/hooks/useToast';
// Temporarily removed qrcode.react import - will fix later

interface PromoLink {
  id: string;
  title: string;
  url: string;
  shortCode: string;
  contentType: 'beat' | 'track' | 'profile' | 'playlist';
  contentId: string;
  contentTitle: string;
  clicks: number;
  views: number;
  ctr: number; // Click-through rate
  createdAt: string;
  expiresAt?: string;
  tags: string[];
  geoData: Record<string, number>; // Country -> count
  isActive: boolean;
}

interface PromoAnalytics {
  totalLinks: number;
  totalClicks: number;
  totalViews: number;
  averageCTR: number;
  topLink: PromoLink | null;
  geoBreakdown: Array<{ country: string; clicks: number; percentage: number }>;
}

const MOCK_PROMO_LINKS: PromoLink[] = [
  {
    id: '1',
    title: 'Summer Vibes Promotion',
    url: 'https://beatspush.app/r/summer-vibes',
    shortCode: 'summer-vibes',
    contentType: 'beat',
    contentId: 'beat-1',
    contentTitle: 'Summer Vibes',
    clicks: 1250,
    views: 8500,
    ctr: 14.7,
    createdAt: new Date(Date.now() - 30 * 86400000).toISOString(),
    tags: ['summer', 'trending', 'featured'],
    geoData: { NG: 850, GH: 200, KE: 150, ZA: 50 },
    isActive: true,
  },
  {
    id: '2',
    title: 'DJ Collaboration Link',
    url: 'https://beatspush.app/r/dj-collab',
    shortCode: 'dj-collab',
    contentType: 'profile',
    contentId: 'user-1',
    contentTitle: 'My Artist Profile',
    clicks: 890,
    views: 5200,
    ctr: 17.1,
    createdAt: new Date(Date.now() - 15 * 86400000).toISOString(),
    tags: ['collaboration', 'dj'],
    geoData: { NG: 600, GH: 150, KE: 100, US: 40 },
    isActive: true,
  },
  {
    id: '3',
    title: 'New Track Release',
    url: 'https://beatspush.app/r/new-track',
    shortCode: 'new-track',
    contentType: 'track',
    contentId: 'track-1',
    contentTitle: 'Midnight Flow',
    clicks: 450,
    views: 2100,
    ctr: 21.4,
    createdAt: new Date(Date.now() - 7 * 86400000).toISOString(),
    tags: ['new-release', 'hiphop'],
    geoData: { NG: 250, GH: 120, KE: 70, CA: 10 },
    isActive: true,
  },
  {
    id: '4',
    title: 'Playlist Showcase',
    url: 'https://beatspush.app/r/playlist-2024',
    shortCode: 'playlist-2024',
    contentType: 'playlist',
    contentId: 'playlist-1',
    contentTitle: '2024 Hits Collection',
    clicks: 120,
    views: 800,
    ctr: 15.0,
    createdAt: new Date(Date.now() - 60 * 86400000).toISOString(),
    tags: ['playlist', 'collection'],
    geoData: { NG: 600, GH: 150, ZA: 50 },
    isActive: false,
  },
];

const calculateAnalytics = (links: PromoLink[]): PromoAnalytics => {
  const activeLinks = links.filter((l) => l.isActive);
  const totalClicks = activeLinks.reduce((sum, l) => sum + l.clicks, 0);
  const totalViews = activeLinks.reduce((sum, l) => sum + l.views, 0);

  const geoAggregate: Record<string, number> = {};
  activeLinks.forEach((link) => {
    Object.entries(link.geoData).forEach(([country, count]) => {
      geoAggregate[country] = (geoAggregate[country] || 0) + count;
    });
  });

  const geoBreakdown = Object.entries(geoAggregate)
    .map(([country, clicks]) => ({
      country,
      clicks,
      percentage: totalClicks > 0 ? (clicks / totalClicks) * 100 : 0,
    }))
    .sort((a, b) => b.clicks - a.clicks);

  return {
    totalLinks: links.length,
    totalClicks,
    totalViews,
    averageCTR: totalViews > 0 ? (totalClicks / totalViews) * 100 : 0,
    topLink: activeLinks.reduce((top, link) => (link.clicks > (top?.clicks || 0) ? link : top), activeLinks[0] || null),
    geoBreakdown,
  };
};

export default function PromoLinksPage() {
  const { toast } = useToast();
  const [links, setLinks] = useState<PromoLink[]>(MOCK_PROMO_LINKS);
  const [activeTab, setActiveTab] = useState<'overview' | 'manage' | 'create'>('overview');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showQRModal, setShowQRModal] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedContent, setSelectedContent] = useState('');

  const [formData, setFormData] = useState({
    title: '',
    contentType: 'beat' as const,
    contentId: '',
    contentTitle: '',
    tags: '',
  });

  const analytics = useMemo(() => calculateAnalytics(links), [links]);

  const filteredLinks = useMemo(() => {
    return links.filter(
      (link) =>
        link.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        link.contentTitle.toLowerCase().includes(searchQuery.toLowerCase()) ||
        link.shortCode.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }, [links, searchQuery]);

  const handleCreateLink = async () => {
    if (!formData.title || !formData.contentId) {
      toast({
        title: 'Error',
        description: 'Please fill in all required fields',
        variant: 'destructive',
      });
      return;
    }

    try {
      const newLink: PromoLink = {
        id: `promo-${Date.now()}`,
        title: formData.title,
        url: `https://beatspush.app/r/${formData.title.toLowerCase().replace(/\s+/g, '-')}`,
        shortCode: formData.title.toLowerCase().replace(/\s+/g, '-'),
        contentType: formData.contentType,
        contentId: formData.contentId,
        contentTitle: formData.contentTitle,
        clicks: 0,
        views: 0,
        ctr: 0,
        createdAt: new Date().toISOString(),
        tags: formData.tags
          .split(',')
          .map((t) => t.trim())
          .filter((t) => t),
        geoData: {},
        isActive: true,
      };

      setLinks((prev) => [newLink, ...prev]);
      toast({
        title: 'Success',
        description: 'Promo link created successfully',
      });

      setFormData({
        title: '',
        contentType: 'beat',
        contentId: '',
        contentTitle: '',
        tags: '',
      });
      setShowCreateModal(false);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to create promo link',
        variant: 'destructive',
      });
    }
  };

  const handleCopyLink = (url: string) => {
    navigator.clipboard.writeText(url);
    toast({
      title: 'Success',
      description: 'Link copied to clipboard',
    });
  };

  const handleDeleteLink = (id: string) => {
    setLinks((prev) => prev.filter((l) => l.id !== id));
    toast({
      title: 'Success',
      description: 'Promo link deleted',
    });
  };

  const handleToggleActive = (id: string) => {
    setLinks((prev) =>
      prev.map((l) => (l.id === id ? { ...l, isActive: !l.isActive } : l))
    );
  };

  const handleDownloadQR = (link: PromoLink) => {
    const qrElement = document.getElementById(`qr-${link.id}`);
    if (qrElement) {
      const url = (qrElement.querySelector('canvas') as HTMLCanvasElement).toDataURL('image/png');
      const a = document.createElement('a');
      a.href = url;
      a.download = `${link.shortCode}-qr.png`;
      a.click();
      toast({
        title: 'Success',
        description: 'QR code downloaded',
      });
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Link2 className="w-8 h-8 text-purple-500" />
              <h1 className="text-4xl font-bold text-white">Promo Links</h1>
            </div>
            <Button
              onClick={() => setShowCreateModal(true)}
              className="gap-2 bg-purple-600 hover:bg-purple-700"
            >
              <Plus className="w-4 h-4" />
              Create Link
            </Button>
          </div>
          <p className="text-gray-400 mt-2">Create and manage shareable links with QR codes</p>
        </div>

        {/* Analytics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-card rounded-lg border border-border p-6">
            <p className="text-gray-400 text-sm font-medium">Active Links</p>
            <p className="text-3xl font-bold text-white mt-2">
              {links.filter((l) => l.isActive).length}
            </p>
          </div>

          <div className="bg-card rounded-lg border border-border p-6">
            <p className="text-gray-400 text-sm font-medium">Total Clicks</p>
            <p className="text-3xl font-bold text-white mt-2">{analytics.totalClicks.toLocaleString()}</p>
          </div>

          <div className="bg-card rounded-lg border border-border p-6">
            <p className="text-gray-400 text-sm font-medium">Total Views</p>
            <p className="text-3xl font-bold text-white mt-2">{analytics.totalViews.toLocaleString()}</p>
          </div>

          <div className="bg-card rounded-lg border border-border p-6">
            <p className="text-gray-400 text-sm font-medium">Avg. CTR</p>
            <p className="text-3xl font-bold text-white mt-2">{analytics.averageCTR.toFixed(1)}%</p>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)} className="space-y-6">
          <TabsList className="grid w-full grid-cols-3 bg-gray-800 border border-gray-700">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="manage" className="flex items-center gap-2">
              <Link2 className="w-4 h-4" />
              Manage Links
            </TabsTrigger>
            <TabsTrigger value="create" className="flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Create
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {analytics.topLink && (
              <div className="bg-card rounded-lg border border-border p-6">
                <h3 className="text-lg font-bold text-white mb-4">Top Performing Link</h3>
                <div className="p-4 bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-lg border border-purple-500/30">
                  <p className="text-white font-semibold">{analytics.topLink.title}</p>
                  <p className="text-gray-400 text-sm mt-1">{analytics.topLink.contentTitle}</p>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div>
                      <p className="text-gray-400 text-xs">Clicks</p>
                      <p className="text-2xl font-bold text-purple-400">
                        {analytics.topLink.clicks.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Views</p>
                      <p className="text-2xl font-bold text-purple-400">
                        {analytics.topLink.views.toLocaleString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">CTR</p>
                      <p className="text-2xl font-bold text-purple-400">{analytics.topLink.ctr.toFixed(1)}%</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <MapPin className="w-5 h-5 text-purple-500" />
                Geographic Breakdown
              </h3>
              <div className="space-y-3">
                {analytics.geoBreakdown.slice(0, 5).map((item, idx) => (
                  <div key={idx} className="flex items-center justify-between">
                    <div className="flex items-center gap-3 flex-1">
                      <p className="text-white font-medium w-16">{item.country}</p>
                      <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                          style={{ width: `${item.percentage}%` }}
                        />
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-white font-semibold">{item.clicks}</p>
                      <p className="text-gray-400 text-xs">{item.percentage.toFixed(1)}%</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Manage Links Tab */}
          <TabsContent value="manage" className="space-y-4">
            <div className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-center gap-2">
                <Search className="w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search links..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 bg-transparent border-0 text-white placeholder-gray-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="space-y-3">
              {filteredLinks.map((link) => (
                <div key={link.id} className="bg-card rounded-lg border border-border p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h4 className="text-white font-semibold">{link.title}</h4>
                      <p className="text-gray-400 text-sm mt-1">{link.contentTitle}</p>
                    </div>
                    <span
                      className={`px-3 py-1 rounded-full text-xs font-medium ${
                        link.isActive
                          ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                          : 'bg-red-500/20 text-red-400 border border-red-500/30'
                      }`}
                    >
                      {link.isActive ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  <div className="flex items-center gap-2 mb-4">
                    <code className="flex-1 px-3 py-2 bg-gray-800 rounded border border-gray-700 text-gray-300 text-sm truncate">
                      {link.shortCode}
                    </code>
                    <button
                      onClick={() => handleCopyLink(link.url)}
                      className="p-2 hover:bg-gray-700 rounded transition text-gray-400 hover:text-white"
                      title="Copy link"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-gray-400 text-xs">Clicks</p>
                      <p className="text-lg font-bold text-white">{link.clicks}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Views</p>
                      <p className="text-lg font-bold text-white">{link.views}</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">CTR</p>
                      <p className="text-lg font-bold text-white">{link.ctr.toFixed(1)}%</p>
                    </div>
                    <div>
                      <p className="text-gray-400 text-xs">Created</p>
                      <p className="text-lg font-bold text-white">
                        {new Date(link.createdAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      className="gap-2"
                      onClick={() => setShowQRModal(link.id)}
                    >
                      <QrCode className="w-4 h-4" />
                      QR Code
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="gap-2"
                      onClick={() => handleToggleActive(link.id)}
                    >
                      {link.isActive ? 'Deactivate' : 'Activate'}
                    </Button>
                    <Button
                      size="sm"
                      variant="outline"
                      className="gap-2 text-red-400 hover:text-red-300"
                      onClick={() => handleDeleteLink(link.id)}
                    >
                      <Trash2 className="w-4 h-4" />
                      Delete
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Create Tab */}
          <TabsContent value="create" className="space-y-6">
            <div className="bg-card rounded-lg border border-border p-6">
              <h3 className="text-lg font-bold text-white mb-4">Create New Promo Link</h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Link Title
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData((prev) => ({ ...prev, title: e.target.value }))}
                    placeholder="e.g., Summer Vibes Promotion"
                    className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Content Type
                    </label>
                    <select
                      value={formData.contentType}
                      onChange={(e) =>
                        setFormData((prev) => ({
                          ...prev,
                          contentType: e.target.value as any,
                        }))
                      }
                      className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-purple-500"
                    >
                      <option value="beat">Beat</option>
                      <option value="track">Track</option>
                      <option value="profile">Profile</option>
                      <option value="playlist">Playlist</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white mb-2">
                      Content ID
                    </label>
                    <input
                      type="text"
                      value={formData.contentId}
                      onChange={(e) =>
                        setFormData((prev) => ({ ...prev, contentId: e.target.value }))
                      }
                      placeholder="ID or reference"
                      className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Content Title
                  </label>
                  <input
                    type="text"
                    value={formData.contentTitle}
                    onChange={(e) =>
                      setFormData((prev) => ({ ...prev, contentTitle: e.target.value }))
                    }
                    placeholder="Name of the content"
                    className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Tags (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={formData.tags}
                    onChange={(e) => setFormData((prev) => ({ ...prev, tags: e.target.value }))}
                    placeholder="e.g., trending, featured, summer"
                    className="w-full px-4 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <Button variant="outline" className="flex-1">
                  Cancel
                </Button>
                <Button
                  onClick={handleCreateLink}
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                >
                  Create Link
                </Button>
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {/* QR Code Modal */}
        {showQRModal && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
            <div className="bg-card rounded-lg border border-border max-w-md w-full">
              <div className="p-6 border-b border-border">
                <h3 className="text-xl font-bold text-white">
                  {links.find((l) => l.id === showQRModal)?.title}
                </h3>
              </div>

              <div className="p-6 flex flex-col items-center gap-4">
                {links.find((l) => l.id === showQRModal) && (
                  <div
                    id={`qr-${showQRModal}`}
                    className="p-4 bg-white rounded-lg w-64 h-64 flex items-center justify-center"
                  >
                    <div className="text-center text-gray-600">
                      <QrCode className="w-16 h-16 mx-auto mb-2 text-gray-400" />
                      <p className="text-sm">QR Code feature coming soon</p>
                    </div>
                  </div>
                )}

                <p className="text-gray-400 text-sm text-center">
                  {links.find((l) => l.id === showQRModal)?.url}
                </p>
              </div>

              <div className="flex gap-2 p-6 border-t border-border">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowQRModal(null)}
                >
                  Close
                </Button>
                <Button
                  onClick={() => {
                    handleDownloadQR(links.find((l) => l.id === showQRModal)!);
                    setShowQRModal(null);
                  }}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 gap-2"
                >
                  <Download className="w-4 h-4" />
                  Download QR
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
