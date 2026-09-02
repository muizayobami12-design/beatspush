'use client';

import { useParams } from 'next/navigation';
import { notFound } from 'next/navigation';
import { ArrowLeft, Play, Pause, Heart, ShoppingCart, CheckCircle2, Music2, Clock, Loader2, Download, FileAudio, FileText, Award, History, X } from 'lucide-react';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { useAudioStore } from '@/store/audioStore';
import { useCartStore } from '@/store/cartStore';
import { TipButton } from '@/components/shared/TipButton';
import LikeButton from '@/components/features/social/LikeButton';
import ShareButton from '@/components/features/social/ShareButton';
import CommentsSection from '@/components/features/social/CommentsSection';
import FollowButton from '@/components/features/social/FollowButton';
import { toast } from 'sonner';
import apiClient from '@/lib/apiClient';

// Mock beat data (same as in BeatGrid)
const MOCK_BEATS = [
  {
    id: '1',
    title: 'Afro Vibes',
    creatorId: 'prod1',
    creator: {
      id: 'prod1',
      email: 'producer@example.com',
      fullName: 'DJ Kizz',
      role: 'producer' as const,
      isVerified: true,
      followerCount: 1250,
      followingCount: 340,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    },
    audioUrl: '/audio/sample-beat.mp3',
    thumbnailUrl: null,
    genre: 'Afrobeat',
    tempo: 120,
    key: 'C minor',
    duration: 180,
    price: 5000,
    tags: ['afrobeat', 'danceable', 'party'],
    playCount: 2340,
    favoriteCount: 156,
    isFavorited: false,
    isPurchased: false,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
  },
  // Add other beats here for "Similar Beats" section
];

interface PurchaseHistory {
  id: string;
  beatId: string;
  beatTitle: string;
  licenseType: 'lease' | 'exclusive';
  price: number;
  purchasedAt: string;
  downloadUrl: string;
  certificateUrl: string;
  files: Array<{
    name: string;
    format: string; // 'mp3', 'wav', 'stems'
    size: string;
    url: string;
  }>;
}

interface LicenseCertificate {
  id: string;
  beatId: string;
  beatTitle: string;
  buyerId: string;
  buyerName: string;
  producerId: string;
  producerName: string;
  licenseType: 'lease' | 'exclusive';
  issuedAt: string;
  expiresAt?: string;
  licenseNumber: string;
  terms: string[];
}

const MOCK_PURCHASE_HISTORY: PurchaseHistory[] = [
  {
    id: 'purch-1',
    beatId: '1',
    beatTitle: 'Afro Vibes',
    licenseType: 'lease',
    price: 5000,
    purchasedAt: new Date(Date.now() - 30 * 86400000).toISOString(),
    downloadUrl: '/downloads/afro-vibes-lease.zip',
    certificateUrl: '/certificates/afro-vibes-cert-1.pdf',
    files: [
      {
        name: 'Afro Vibes - MP3 (Tagged)',
        format: 'mp3',
        size: '8.5 MB',
        url: '/downloads/afro-vibes-tagged.mp3',
      },
      {
        name: 'Afro Vibes - WAV (Tagged)',
        format: 'wav',
        size: '35.2 MB',
        url: '/downloads/afro-vibes-tagged.wav',
      },
      {
        name: 'Afro Vibes - MP3 (Untagged)',
        format: 'mp3',
        size: '8.5 MB',
        url: '/downloads/afro-vibes-untagged.mp3',
      },
      {
        name: 'Afro Vibes - WAV (Untagged)',
        format: 'wav',
        size: '35.2 MB',
        url: '/downloads/afro-vibes-untagged.wav',
      },
    ],
  },
];

const MOCK_LICENSE_CERTIFICATE: LicenseCertificate = {
  id: 'cert-1',
  beatId: '1',
  beatTitle: 'Afro Vibes',
  buyerId: 'user-1',
  buyerName: 'Artist Name',
  producerId: 'prod1',
  producerName: 'DJ Kizz',
  licenseType: 'lease',
  issuedAt: new Date(Date.now() - 30 * 86400000).toISOString(),
  expiresAt: new Date(Date.now() + 365 * 86400000).toISOString(),
  licenseNumber: 'LIC-2024-001234',
  terms: [
    'Up to 10,000 streams',
    'Up to 5,000 audio sales',
    '1 music video allowed',
    'Radio broadcasting allowed',
    'Non-exclusive license',
  ],
};

export default function BeatDetailPage() {
  const params = useParams();
  const beatId = params.id as string;
  
  // Find beat by ID
  const beat = MOCK_BEATS.find((b) => b.id === beatId);

  // Properly handle 404 for missing beats
  if (!beat) {
    notFound();
  }
  
  const [selectedLicense, setSelectedLicense] = useState<'lease' | 'exclusive'>('lease');
  const [similarBeats, setSimilarBeats] = useState<any[]>([]);
  const [isLoadingSimilar, setIsLoadingSimilar] = useState(true);
  const [purchaseHistory, setPurchaseHistory] = useState<PurchaseHistory[]>(MOCK_PURCHASE_HISTORY);
  const [showDownloadModal, setShowDownloadModal] = useState(false);
  const [showCertificateModal, setShowCertificateModal] = useState(false);
  const [selectedPurchase, setSelectedPurchase] = useState<PurchaseHistory | null>(null);
  const [isDownloading, setIsDownloading] = useState<string | null>(null);
  
  const { currentBeat, isPlaying, playBeat, pauseBeat } = useAudioStore();
  const { addToCart } = useCartStore();
  
  const isCurrentBeat = currentBeat?.id === beat.id;
  const isThisPlaying = isCurrentBeat && isPlaying;

  // Load similar beats on mount
  useEffect(() => {
    const loadSimilarBeats = async () => {
      try {
        setIsLoadingSimilar(true);
        const response = await apiClient.get(
          `/api/v1/recommendations/similar/${beatId}?limit=6`
        );
        
        if (response.data.success && response.data.similar) {
          setSimilarBeats(response.data.similar);
        }
      } catch (error) {
        console.error('Failed to load similar beats:', error);
        // Fallback to mock data
        setSimilarBeats(MOCK_BEATS.slice(1, 4));
      } finally {
        setIsLoadingSimilar(false);
      }
    };

    loadSimilarBeats();
  }, [beatId]);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const handlePlayPause = () => {
    if (isThisPlaying) {
      pauseBeat();
    } else {
      playBeat(beat);
    }
  };

  const handleAddToCart = () => {
    addToCart(beat, selectedLicense);
    toast.success(`Added "${beat.title}" (${selectedLicense}) to cart`, {
      action: {
        label: 'View Cart',
        onClick: () => window.location.href = '/cart',
      },
    });
  };

  const exclusivePrice = beat.price * 3; // 3x lease price for exclusive

  const handleDownloadFile = async (fileUrl: string, fileName: string) => {
    setIsDownloading(fileUrl);
    try {
      const response = await fetch(fileUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast.success(`Downloaded ${fileName}`);
    } catch (error) {
      toast.error('Failed to download file');
    } finally {
      setIsDownloading(null);
    }
  };

  const handleOpenPurchaseHistory = () => {
    if (purchaseHistory.length > 0) {
      setSelectedPurchase(purchaseHistory[0]);
      setShowDownloadModal(true);
    } else {
      toast.error('No purchase history found');
    }
  };

  const handleDownloadCertificate = async () => {
    try {
      // In a real app, this would generate a PDF
      const element = document.getElementById('certificate-content');
      if (element) {
        const printWindow = window.open('', '', 'width=800,height=600');
        if (printWindow) {
          printWindow.document.write(element.innerHTML);
          printWindow.document.close();
          printWindow.print();
        }
      }
      toast.success('Certificate downloaded');
    } catch (error) {
      toast.error('Failed to download certificate');
    }
  };

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Back Button */}
      <div className="border-b bg-card/50">
        <div className="container mx-auto px-4 py-4">
          <Link href="/beats">
            <Button variant="ghost" size="sm" className="gap-2">
              <ArrowLeft className="h-4 w-4" />
              Back to Marketplace
            </Button>
          </Link>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Beat Header */}
            <div className="flex items-start gap-6">
              {/* Cover Art */}
              <div className="relative w-48 h-48 flex-shrink-0 rounded-lg overflow-hidden bg-gradient-to-br from-primary/20 to-primary/5 group">
                {beat.thumbnailUrl ? (
                  <img
                    src={beat.thumbnailUrl}
                    alt={beat.title}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center">
                    <Music2 className="h-20 w-20 text-muted-foreground opacity-50" />
                  </div>
                )}
                
                {/* Play Overlay */}
                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Button
                    size="lg"
                    onClick={handlePlayPause}
                    className="rounded-full h-16 w-16 p-0"
                  >
                    {isThisPlaying ? (
                      <Pause className="h-8 w-8" fill="currentColor" />
                    ) : (
                      <Play className="h-8 w-8" fill="currentColor" />
                    )}
                  </Button>
                </div>
              </div>

              {/* Beat Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4 mb-4">
                  <div className="flex-1 min-w-0">
                    <h1 className="text-4xl font-bold mb-2">{beat.title}</h1>
                    <Link
                      href={`/profile/${beat.creator.id}`}
                      className="flex items-center gap-2 text-lg text-muted-foreground hover:text-primary transition-colors"
                    >
                      <span>by {beat.creator.fullName}</span>
                      {beat.creator.isVerified && (
                        <CheckCircle2 className="h-4 w-4 text-blue-500" />
                      )}
                    </Link>
                  </div>

                  <div className="flex gap-2">
                    <LikeButton
                      contentType="beat"
                      contentId={beat.id}
                      initialLikes={beat.favoriteCount}
                      initialIsLiked={beat.isFavorited}
                      size="md"
                      showCount={false}
                    />
                    <ShareButton
                      contentType="beat"
                      contentId={beat.id}
                      title={beat.title}
                      size="md"
                      variant="outline"
                    />
                  </div>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-6 text-sm text-muted-foreground mb-4">
                  <span className="flex items-center gap-1">
                    <Play className="h-4 w-4" />
                    {beat.playCount.toLocaleString()} plays
                  </span>
                  <span className="flex items-center gap-1">
                    <Heart className="h-4 w-4" />
                    {beat.favoriteCount} favorites
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" />
                    {Math.floor(beat.duration / 60)}:{(beat.duration % 60).toString().padStart(2, '0')}
                  </span>
                </div>

                {/* Technical Details */}
                <div className="flex flex-wrap gap-2">
                  <span className="px-3 py-1.5 rounded-full bg-primary/10 text-primary font-medium text-sm">
                    {beat.genre}
                  </span>
                  <span className="px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm">
                    {beat.tempo} BPM
                  </span>
                  <span className="px-3 py-1.5 rounded-full bg-secondary text-secondary-foreground text-sm">
                    {beat.key}
                  </span>
                </div>
              </div>
            </div>

            {/* Tags */}
            {beat.tags && beat.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {beat.tags.map((tag) => (
                  <span
                    key={tag}
                    className="px-3 py-1 rounded-md bg-muted text-muted-foreground text-sm"
                  >
                    #{tag}
                  </span>
                ))}
              </div>
            )}

            {/* Description */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-3">About This Beat</h2>
              <p className="text-muted-foreground leading-relaxed">
                High-quality {beat.genre} instrumental perfect for your next project. Professional
                mixing and mastering included. Tagged preview available for streaming, untagged
                version delivered upon purchase.
              </p>
            </div>

            {/* License Information */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">License Options</h2>
              
              <div className="space-y-4">
                {/* Lease License */}
                <div
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedLicense === 'lease'
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => setSelectedLicense('lease')}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-lg">Lease License</h3>
                    <span className="text-2xl font-bold text-primary">
                      {formatPrice(beat.price)}
                    </span>
                  </div>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>✓ Up to 10,000 streams</li>
                    <li>✓ Up to 5,000 audio sales</li>
                    <li>✓ 1 music video allowed</li>
                    <li>✓ Radio broadcasting allowed</li>
                    <li>✓ Untagged MP3 & WAV files</li>
                  </ul>
                </div>

                {/* Exclusive License */}
                <div
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedLicense === 'exclusive'
                      ? 'border-primary bg-primary/5'
                      : 'border-border hover:border-primary/50'
                  }`}
                  onClick={() => setSelectedLicense('exclusive')}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-lg">Exclusive License</h3>
                      <span className="px-2 py-0.5 rounded-md bg-yellow-500/10 text-yellow-600 dark:text-yellow-500 text-xs font-medium">
                        PREMIUM
                      </span>
                    </div>
                    <span className="text-2xl font-bold text-primary">
                      {formatPrice(exclusivePrice)}
                    </span>
                  </div>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>✓ Unlimited streams & sales</li>
                    <li>✓ Unlimited music videos</li>
                    <li>✓ Full ownership rights</li>
                    <li>✓ Beat removed from marketplace</li>
                    <li>✓ Trackstems included</li>
                  </ul>
                </div>
              </div>
            </div>

            {/* Producer Info */}
            <div className="bg-card rounded-lg border p-6">
              <h2 className="text-xl font-semibold mb-4">About the Producer</h2>
              <div className="flex items-center gap-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-primary to-primary/50 flex items-center justify-center text-white text-2xl font-bold">
                  {beat.creator.fullName.charAt(0)}
                </div>
                <div className="flex-1">
                  <Link href={`/profile/${beat.creator.id}`}>
                    <h3 className="font-semibold text-lg hover:text-primary transition-colors flex items-center gap-2">
                      {beat.creator.fullName}
                      {beat.creator.isVerified && (
                        <CheckCircle2 className="h-4 w-4 text-blue-500" />
                      )}
                    </h3>
                  </Link>
                  <p className="text-sm text-muted-foreground">
                    {beat.creator.followerCount.toLocaleString()} followers
                  </p>
                </div>
                <div className="flex gap-2">
                  <FollowButton
                    userId={beat.creator.id}
                    userName={beat.creator.fullName}
                    size="md"
                  />
                  <TipButton
                    toUserId={beat.creator.id}
                    toUserName={beat.creator.fullName}
                    variant="outline"
                    showLabel={true}
                    contentType="beat"
                    contentId={beat.id}
                  />
                </div>
              </div>
            </div>

            {/* Purchase History & Downloads */}
            {purchaseHistory.length > 0 && (
              <div className="bg-card rounded-lg border p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Download className="h-5 w-5 text-purple-500" />
                  Your Purchases
                </h2>

                <div className="space-y-3">
                  {purchaseHistory.map((purchase) => (
                    <div key={purchase.id} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <p className="text-white font-medium">{purchase.beatTitle}</p>
                          <p className="text-sm text-gray-400">
                            {purchase.licenseType.charAt(0).toUpperCase() + purchase.licenseType.slice(1)} License
                          </p>
                          <p className="text-xs text-gray-500 mt-1">
                            Purchased: {new Date(purchase.purchasedAt).toLocaleDateString()}
                          </p>
                        </div>
                        <span className="text-lg font-bold text-purple-400">
                          ₦{purchase.price.toLocaleString()}
                        </span>
                      </div>

                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          className="gap-2 text-xs flex-1"
                          onClick={() => {
                            setSelectedPurchase(purchase);
                            setShowDownloadModal(true);
                          }}
                        >
                          <Download className="w-4 h-4" />
                          Download Files
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="gap-2 text-xs flex-1"
                          onClick={() => {
                            setSelectedPurchase(purchase);
                            setShowCertificateModal(true);
                          }}
                        >
                          <Award className="w-4 h-4" />
                          View Certificate
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Comments Section */}
            <CommentsSection
              contentType="beat"
              contentId={beat.id}
              className="bg-card rounded-lg border p-6"
            />
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Purchase Card */}
            <div className="bg-card rounded-lg border p-6 sticky top-4">
              <div className="mb-6">
                <p className="text-sm text-muted-foreground mb-2">
                  {selectedLicense === 'lease' ? 'Lease' : 'Exclusive'} License
                </p>
                <p className="text-4xl font-bold text-primary">
                  {formatPrice(
                    selectedLicense === 'lease' ? beat.price : exclusivePrice
                  )}
                </p>
              </div>

              <div className="space-y-3">
                <Button
                  size="lg"
                  className="w-full gap-2"
                  onClick={handleAddToCart}
                >
                  <ShoppingCart className="h-5 w-5" />
                  Add to Cart
                </Button>
                
                <Button
                  size="lg"
                  variant="outline"
                  className="w-full gap-2"
                  onClick={handlePlayPause}
                >
                  {isThisPlaying ? (
                    <>
                      <Pause className="h-5 w-5" />
                      Pause Preview
                    </>
                  ) : (
                    <>
                      <Play className="h-5 w-5" />
                      Play Preview
                    </>
                  )}
                </Button>
              </div>

              <div className="mt-6 pt-6 border-t space-y-2 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span>Instant delivery</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span>High-quality files</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="h-4 w-4 text-green-500" />
                  <span>License certificate included</span>
                </div>
              </div>
            </div>

            {/* Similar Beats */}
            <div>
              <h3 className="font-semibold text-lg mb-4">Similar Beats</h3>
              
              {isLoadingSimilar ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="w-6 h-6 text-primary animate-spin" />
                </div>
              ) : similarBeats.length > 0 ? (
                <div className="space-y-4">
                  {similarBeats.map((similarBeat) => (
                    <Link key={similarBeat.id} href={`/beats/${similarBeat.id}`}>
                      <div className="flex gap-3 p-3 rounded-lg hover:bg-accent transition-colors">
                        <div className="w-16 h-16 rounded-md bg-gradient-to-br from-primary/20 to-primary/5 flex-shrink-0">
                          <div className="w-full h-full flex items-center justify-center">
                            <Music2 className="h-6 w-6 text-muted-foreground" />
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm truncate">
                            {similarBeat.title}
                          </h4>
                          <p className="text-xs text-muted-foreground truncate">
                            {similarBeat.genre} • {similarBeat.bpm || '?'} BPM
                          </p>
                          <p className="text-sm font-semibold text-primary mt-1">
                            {formatPrice(similarBeat.price)}
                          </p>
                        </div>
                      </div>
                    </Link>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p className="text-sm">No similar beats found</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Download Modal */}
      {showDownloadModal && selectedPurchase && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-card rounded-lg border border-border max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-border sticky top-0 bg-card flex items-center justify-between">
              <h3 className="text-xl font-bold text-white flex items-center gap-2">
                <Download className="w-5 h-5 text-purple-500" />
                Download Files: {selectedPurchase.beatTitle}
              </h3>
              <button
                onClick={() => setShowDownloadModal(false)}
                className="text-gray-400 hover:text-white transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="p-6 space-y-4">
              <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
                <p className="text-blue-200 text-sm">
                  ✓ License: {selectedPurchase.licenseType === 'lease' ? 'Lease' : 'Exclusive'}
                </p>
                <p className="text-blue-200 text-sm">
                  ✓ Purchased: {new Date(selectedPurchase.purchasedAt).toLocaleDateString()}
                </p>
              </div>

              <div>
                <h4 className="font-semibold text-white mb-3">Available Files</h4>
                <div className="space-y-2">
                  {selectedPurchase.files.map((file, idx) => (
                    <div
                      key={idx}
                      className="p-4 bg-gray-800/50 rounded-lg border border-gray-700 flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <FileAudio className="w-5 h-5 text-purple-400" />
                        <div className="flex-1">
                          <p className="text-white font-medium text-sm">{file.name}</p>
                          <p className="text-gray-400 text-xs">{file.size} • {file.format.toUpperCase()}</p>
                        </div>
                      </div>
                      <Button
                        size="sm"
                        className="gap-2 bg-purple-600 hover:bg-purple-700"
                        onClick={() => handleDownloadFile(file.url, file.name)}
                        disabled={isDownloading === file.url}
                      >
                        {isDownloading === file.url ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" />
                            Downloading...
                          </>
                        ) : (
                          <>
                            <Download className="w-4 h-4" />
                            Download
                          </>
                        )}
                      </Button>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-lg p-4">
                <h4 className="font-semibold text-white mb-2">License Info</h4>
                <ul className="text-sm text-gray-300 space-y-1">
                  {selectedPurchase.licenseType === 'lease' ? (
                    <>
                      <li>✓ Up to 10,000 streams</li>
                      <li>✓ Up to 5,000 audio sales</li>
                      <li>✓ 1 music video allowed</li>
                      <li>✓ Radio broadcasting allowed</li>
                    </>
                  ) : (
                    <>
                      <li>✓ Unlimited streams & sales</li>
                      <li>✓ Unlimited music videos</li>
                      <li>✓ Full ownership rights</li>
                      <li>✓ Beat removed from marketplace</li>
                    </>
                  )}
                </ul>
              </div>
            </div>

            <div className="flex gap-2 p-6 border-t border-border sticky bottom-0 bg-card">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowDownloadModal(false)}
              >
                Close
              </Button>
              <Button
                className="flex-1 bg-purple-600 hover:bg-purple-700 gap-2"
                onClick={() => {
                  setSelectedPurchase(selectedPurchase);
                  setShowCertificateModal(true);
                }}
              >
                <Award className="w-4 h-4" />
                View Certificate
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* License Certificate Modal */}
      {showCertificateModal && selectedPurchase && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b flex items-center justify-between sticky top-0 bg-white">
              <h3 className="text-xl font-bold text-gray-900 flex items-center gap-2">
                <Award className="w-5 h-5 text-purple-600" />
                License Certificate
              </h3>
              <button
                onClick={() => setShowCertificateModal(false)}
                className="text-gray-400 hover:text-gray-600 transition"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div id="certificate-content" className="p-12 bg-gray-50">
              <div className="border-4 border-purple-600 rounded-lg p-8 bg-white">
                {/* Certificate Header */}
                <div className="text-center mb-8 pb-8 border-b-2 border-purple-600">
                  <div className="flex justify-center mb-4">
                    <Award className="w-12 h-12 text-purple-600" />
                  </div>
                  <h1 className="text-4xl font-bold text-gray-900 mb-2">
                    LICENSE CERTIFICATE
                  </h1>
                  <p className="text-gray-600">BeatsPush Music Production License</p>
                </div>

                {/* Certificate Content */}
                <div className="space-y-6 mb-8">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">BEAT TITLE</p>
                    <p className="text-2xl font-bold text-gray-900">{selectedPurchase.beatTitle}</p>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">LICENSEE</p>
                      <p className="text-lg font-semibold text-gray-900">Artist Name</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">PRODUCER</p>
                      <p className="text-lg font-semibold text-gray-900">DJ Kizz</p>
                    </div>
                  </div>

                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">LICENSE TYPE</p>
                      <p className="text-lg font-bold text-purple-600 uppercase">
                        {selectedPurchase.licenseType}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">ISSUED DATE</p>
                      <p className="text-lg font-semibold text-gray-900">
                        {new Date(selectedPurchase.purchasedAt).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">LICENSE NUMBER</p>
                      <p className="text-lg font-mono text-gray-900">LIC-2024-001234</p>
                    </div>
                  </div>

                  <div>
                    <p className="text-sm text-gray-600 mb-2">LICENSE TERMS</p>
                    <ul className="space-y-1 text-gray-700">
                      {selectedPurchase.licenseType === 'lease' ? (
                        <>
                          <li>• Up to 10,000 streams on all platforms</li>
                          <li>• Up to 5,000 audio sales</li>
                          <li>• 1 music video allowed</li>
                          <li>• Radio broadcasting allowed</li>
                          <li>• Non-exclusive license</li>
                          <li>• All file formats (MP3, WAV, Stems)</li>
                        </>
                      ) : (
                        <>
                          <li>• Unlimited streams on all platforms</li>
                          <li>• Unlimited sales and distribution</li>
                          <li>• Unlimited music videos</li>
                          <li>• Exclusive ownership of the beat</li>
                          <li>• Beat will be removed from marketplace</li>
                          <li>• All file formats including stems</li>
                        </>
                      )}
                    </ul>
                  </div>
                </div>

                {/* Footer */}
                <div className="border-t-2 border-purple-600 pt-6 mt-8 text-center text-xs text-gray-600">
                  <p>This certificate serves as proof of purchase and valid license terms.</p>
                  <p>For support, contact: support@beatspush.com</p>
                </div>
              </div>
            </div>

            <div className="flex gap-2 p-6 border-t sticky bottom-0 bg-white">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => setShowCertificateModal(false)}
              >
                Close
              </Button>
              <Button
                className="flex-1 gap-2 bg-purple-600 hover:bg-purple-700 text-white"
                onClick={handleDownloadCertificate}
              >
                <Download className="w-4 h-4" />
                Download as PDF
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
