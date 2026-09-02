/**
 * CopyButton - Copy message content to clipboard
 */

import React, { useState } from 'react';
import { Copy, Check } from 'lucide-react';
import type { CopyButtonProps } from '../types';
import { Button } from '@/components/ui/button';

export const CopyButton: React.FC<CopyButtonProps> = ({ content, onCopy }) => {
  const [copied, setCopied] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCopy = async () => {
    try {
      // Convert markdown to plain text (basic conversion)
      const plainText = content
        .replace(/\*\*(.*?)\*\*/g, '$1') // Bold
        .replace(/\*(.*?)\*/g, '$1')     // Italic
        .replace(/`(.*?)`/g, '$1')       // Code
        .replace(/\[(.*?)\]\(.*?\)/g, '$1'); // Links

      await navigator.clipboard.writeText(plainText);
      setCopied(true);
      setError(null);
      onCopy?.();

      // Reset after 2 seconds
      setTimeout(() => {
        setCopied(false);
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
      setError('Failed to copy');
      setTimeout(() => {
        setError(null);
      }, 2000);
    }
  };

  return (
    <div className="relative">
      <Button
        variant="ghost"
        size="icon"
        className="min-w-[44px] min-h-[44px] w-11 h-11 opacity-0 group-hover:opacity-100 transition-opacity"
        onClick={handleCopy}
        title={error || (copied ? 'Copied!' : 'Copy to clipboard')}
        aria-label={copied ? 'Copied to clipboard' : 'Copy to clipboard'}
      >
        {copied ? (
          <Check className="h-4 w-4 text-green-500" />
        ) : (
          <Copy className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
};

export default CopyButton;
