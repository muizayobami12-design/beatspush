'use client';

import { useState } from 'react';
import { Share2, Facebook, Twitter, MessageCircle, Link as LinkIcon, Copy, Check } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import socialService from '@/services/socialService';
import { cn } from '@/lib/utils';

interface ShareButtonProps {
  contentType: 'beat' | 'track' | 'mix';
  contentId: string;
  title: string;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'outline' | 'ghost';
  showText?: boolean;
  className?: string;
}

export default function ShareButton({
  contentType,
  contentId,
  title,
  size = 'md',
  variant = 'outline',
  showText = false,
  className,
}: ShareButtonProps) {
  const [open, setOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const shareUrls = socialService.getShareUrls({
    content_type: contentType,
    content_id: contentId,
    title,
  });

  const handleShare = async (platform: 'facebook' | 'twitter' | 'whatsapp' | 'link') => {
    // Track share
    try {
      await socialService.trackShare({
        content_type: contentType,
        content_id: contentId,
        platform,
      });
    } catch (error) {
      console.error('Failed to track share:', error);
    }

    // Open share URL
    if (platform === 'link') {
      return; // Handled by copy button
    }

    const url = shareUrls[platform];
    window.open(url, '_blank', 'width=600,height=400');
    setOpen(false);
  };

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(shareUrls.link);
      setCopied(true);
      await socialService.trackShare({
        content_type: contentType,
        content_id: contentId,
        platform: 'link',
      });

      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (error) {
      console.error('Failed to copy link:', error);
      alert('Failed to copy link');
    }
  };

  const buttonSize = size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'default';
  const iconSize = size === 'sm' ? 'h-4 w-4' : size === 'lg' ? 'h-6 w-6' : 'h-5 w-5';

  return (
    <>
      <Button
        variant={variant}
        size={buttonSize}
        onClick={() => setOpen(true)}
        className={cn('gap-2', className)}
      >
        <Share2 className={iconSize} />
        {showText && <span>Share</span>}
      </Button>

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Share</DialogTitle>
          </DialogHeader>

          <div className="space-y-4">
            {/* Share buttons */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              {/* Facebook */}
              <button
                onClick={() => handleShare('facebook')}
                className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors"
              >
                <div className="h-12 w-12 rounded-full bg-blue-600 flex items-center justify-center">
                  <Facebook className="h-6 w-6 text-white" />
                </div>
                <span className="text-xs font-medium">Facebook</span>
              </button>

              {/* Twitter */}
              <button
                onClick={() => handleShare('twitter')}
                className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors"
              >
                <div className="h-12 w-12 rounded-full bg-sky-500 flex items-center justify-center">
                  <Twitter className="h-6 w-6 text-white" />
                </div>
                <span className="text-xs font-medium">Twitter</span>
              </button>

              {/* WhatsApp */}
              <button
                onClick={() => handleShare('whatsapp')}
                className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors"
              >
                <div className="h-12 w-12 rounded-full bg-green-600 flex items-center justify-center">
                  <MessageCircle className="h-6 w-6 text-white" />
                </div>
                <span className="text-xs font-medium">WhatsApp</span>
              </button>

              {/* Copy Link */}
              <button
                onClick={handleCopyLink}
                className="flex flex-col items-center gap-2 p-4 rounded-lg border hover:bg-accent transition-colors"
              >
                <div className={cn(
                  "h-12 w-12 rounded-full flex items-center justify-center transition-colors",
                  copied ? "bg-green-600" : "bg-gray-600"
                )}>
                  {copied ? (
                    <Check className="h-6 w-6 text-white" />
                  ) : (
                    <LinkIcon className="h-6 w-6 text-white" />
                  )}
                </div>
                <span className="text-xs font-medium">
                  {copied ? 'Copied!' : 'Copy Link'}
                </span>
              </button>
            </div>

            {/* Link input */}
            <div className="space-y-2">
              <label className="text-sm font-medium">Or copy link</label>
              <div className="flex gap-2">
                <Input
                  value={shareUrls.link}
                  readOnly
                  className="flex-1"
                  onClick={(e) => (e.target as HTMLInputElement).select()}
                />
                <Button
                  variant="outline"
                  size="icon"
                  onClick={handleCopyLink}
                  className={cn(copied && 'bg-green-500 hover:bg-green-600 text-white')}
                >
                  {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}
