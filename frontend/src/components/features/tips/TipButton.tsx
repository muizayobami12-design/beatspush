'use client';

import { useState } from 'react';
import { Heart, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useToast } from '@/hooks/useToast';

interface TipButtonProps {
  recipientId: string;
  recipientName: string;
  contentType: 'beat' | 'track' | 'profile' | 'livestream';
  contentId?: string;
  onTipSuccess?: (amount: number) => void;
}

const TIP_AMOUNTS = [500, 1000, 2500, 5000, 10000];

export function TipButton({
  recipientId,
  recipientName,
  contentType,
  contentId,
  onTipSuccess,
}: TipButtonProps) {
  const { toast } = useToast();
  const [isOpen, setIsOpen] = useState(false);
  const [selectedAmount, setSelectedAmount] = useState<number | null>(null);
  const [customAmount, setCustomAmount] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleTip = async () => {
    if (!selectedAmount && !customAmount) {
      toast({
        title: 'Error',
        description: 'Please select or enter a tip amount',
        variant: 'destructive',
      });
      return;
    }

    const amount = customAmount ? parseInt(customAmount) : selectedAmount;

    if (amount < 100) {
      toast({
        title: 'Error',
        description: 'Minimum tip amount is ₦100',
        variant: 'destructive',
      });
      return;
    }

    setIsLoading(true);

    try {
      // API call to create tip
      const response = await fetch('/api/v1/tips', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          recipient_id: recipientId,
          amount,
          content_type: contentType,
          content_id: contentId,
          message: message || null,
        }),
      });

      if (!response.ok) throw new Error('Failed to send tip');

      const data = await response.json();

      toast({
        title: 'Success',
        description: `Tipped ₦${amount.toLocaleString()} to ${recipientName}`,
      });

      onTipSuccess?.(amount);
      setIsOpen(false);
      setSelectedAmount(null);
      setCustomAmount('');
      setMessage('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to send tip. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <Button
        variant="outline"
        size="sm"
        className="gap-2"
        onClick={() => setIsOpen(true)}
      >
        <Heart className="w-4 h-4 fill-current text-red-500" />
        Tip
      </Button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
          <div className="bg-card rounded-lg border border-border max-w-sm w-full">
            <div className="p-6 border-b border-border">
              <h2 className="text-xl font-bold text-white">Send a Tip</h2>
              <p className="text-gray-400 text-sm mt-1">
                Support {recipientName} with a tip
              </p>
            </div>

            <div className="p-6 space-y-4">
              {/* Quick Amount Buttons */}
              <div>
                <label className="block text-sm font-medium text-white mb-3">
                  Quick amounts
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {TIP_AMOUNTS.map((amount) => (
                    <button
                      key={amount}
                      onClick={() => {
                        setSelectedAmount(amount);
                        setCustomAmount('');
                      }}
                      className={`p-3 rounded-lg border-2 transition text-sm font-medium ${
                        selectedAmount === amount
                          ? 'bg-purple-600 border-purple-500 text-white'
                          : 'bg-gray-800 border-gray-700 text-gray-300 hover:border-purple-500'
                      }`}
                    >
                      ₦{(amount / 1000).toFixed(1)}k
                    </button>
                  ))}
                </div>
              </div>

              {/* Custom Amount */}
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Or enter custom amount
                </label>
                <div className="flex items-center gap-2">
                  <span className="text-white font-medium">₦</span>
                  <input
                    type="number"
                    value={customAmount}
                    onChange={(e) => {
                      setCustomAmount(e.target.value);
                      setSelectedAmount(null);
                    }}
                    placeholder="100 - 100,000"
                    min="100"
                    max="100000"
                    className="flex-1 px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>
              </div>

              {/* Message */}
              <div>
                <label className="block text-sm font-medium text-white mb-2">
                  Add a message (optional)
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Let them know why you're tipping!"
                  maxLength={200}
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500 resize-none"
                />
                <p className="text-xs text-gray-500 mt-1">{message.length}/200</p>
              </div>
            </div>

            <div className="flex gap-2 p-6 border-t border-border">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => {
                  setIsOpen(false);
                  setSelectedAmount(null);
                  setCustomAmount('');
                  setMessage('');
                }}
              >
                Cancel
              </Button>
              <Button
                className="flex-1 bg-purple-600 hover:bg-purple-700 gap-2"
                onClick={handleTip}
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Heart className="w-4 h-4 fill-current" />
                    Send Tip
                  </>
                )}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
