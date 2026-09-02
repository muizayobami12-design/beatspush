'use client';

import { useState } from 'react';
import { Heart, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { tipService } from '@/services/tipService';
import { useAuthStore } from '@/store/authStore';

interface TipButtonProps {
  toUserId: string;
  toUserName: string;
  variant?: 'default' | 'outline' | 'ghost';
  size?: 'default' | 'sm' | 'lg' | 'icon';
  showLabel?: boolean;
  contentType?: 'beat' | 'track' | 'mix' | 'profile';
  contentId?: string;
}

const QUICK_AMOUNTS = [100, 500, 1000, 2000, 5000];

export function TipButton({
  toUserId,
  toUserName,
  variant = 'outline',
  size = 'default',
  showLabel = true,
  contentType,
  contentId,
}: TipButtonProps) {
  const { user } = useAuthStore();
  const [showModal, setShowModal] = useState(false);
  const [selectedAmount, setSelectedAmount] = useState<number | null>(500);
  const [customAmount, setCustomAmount] = useState('');
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [success, setSuccess] = useState(false);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const handleSendTip = async () => {
    const amount = customAmount ? parseInt(customAmount) : selectedAmount;
    if (!amount || amount < 100) {
      alert('Minimum tip amount is ₦100');
      return;
    }

    setIsSending(true);
    try {
      await tipService.sendTip({
        to_user_id: toUserId,
        amount,
        message: message || undefined,
        content_type: contentType,
        content_id: contentId,
      });
      
      setSuccess(true);
      setTimeout(() => {
        setShowModal(false);
        setSuccess(false);
        setSelectedAmount(500);
        setCustomAmount('');
        setMessage('');
      }, 2000);
    } catch (error) {
      console.error('Failed to send tip:', error);
      alert('Failed to send tip. Please try again.');
    } finally {
      setIsSending(false);
    }
  };

  if (!user) {
    return null; // Don't show tip button if not logged in
  }

  if (user.id === toUserId) {
    return null; // Don't show tip button for own content
  }

  return (
    <>
      {/* Tip Button */}
      <Button
        variant={variant}
        size={size}
        onClick={() => setShowModal(true)}
        className="gap-2"
      >
        <Heart className="h-4 w-4" />
        {showLabel && 'Tip'}
      </Button>

      {/* Tip Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div className="bg-card rounded-lg border max-w-md w-full p-6 relative">
            {/* Close Button */}
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 p-1 rounded-full hover:bg-muted transition-colors"
            >
              <X className="h-5 w-5" />
            </button>

            {success ? (
              /* Success State */
              <div className="text-center py-8">
                <div className="mb-4 flex justify-center">
                  <div className="p-3 rounded-full bg-green-500/10">
                    <Heart className="h-12 w-12 text-green-500 fill-current" />
                  </div>
                </div>
                <h3 className="text-2xl font-bold mb-2">Tip Sent!</h3>
                <p className="text-muted-foreground">
                  Your tip has been sent to {toUserName}
                </p>
              </div>
            ) : (
              /* Tip Form */
              <>
                <div className="mb-6">
                  <h3 className="text-2xl font-bold mb-2">Send a Tip</h3>
                  <p className="text-muted-foreground">
                    Support {toUserName} with a tip
                  </p>
                </div>

                {/* Quick Amounts */}
                <div className="mb-6">
                  <label className="block text-sm font-medium mb-3">Select Amount</label>
                  <div className="grid grid-cols-3 gap-2">
                    {QUICK_AMOUNTS.map((amount) => (
                      <button
                        key={amount}
                        onClick={() => {
                          setSelectedAmount(amount);
                          setCustomAmount('');
                        }}
                        className={`px-4 py-3 rounded-lg border-2 font-semibold transition-colors ${
                          selectedAmount === amount && !customAmount
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border hover:border-primary/50'
                        }`}
                      >
                        {formatPrice(amount)}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Custom Amount */}
                <div className="mb-6">
                  <label className="block text-sm font-medium mb-2">Custom Amount (₦)</label>
                  <Input
                    type="number"
                    min="100"
                    step="50"
                    placeholder="Enter custom amount..."
                    value={customAmount}
                    onChange={(e) => {
                      setCustomAmount(e.target.value);
                      setSelectedAmount(null);
                    }}
                  />
                  <p className="text-xs text-muted-foreground mt-1">Minimum: ₦100</p>
                </div>

                {/* Message */}
                <div className="mb-6">
                  <label className="block text-sm font-medium mb-2">
                    Message (Optional)
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Add a message..."
                    rows={3}
                    maxLength={200}
                    className="w-full px-3 py-2 rounded-md border border-input bg-background focus:outline-none focus:ring-2 focus:ring-ring resize-none"
                  />
                  <p className="text-xs text-muted-foreground mt-1">
                    {message.length}/200 characters
                  </p>
                </div>

                {/* Send Button */}
                <div className="space-y-3">
                  <Button
                    size="lg"
                    className="w-full"
                    onClick={handleSendTip}
                    disabled={isSending || (!selectedAmount && !customAmount)}
                  >
                    {isSending ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                        Sending...
                      </>
                    ) : (
                      <>
                        Send {formatPrice(customAmount ? parseInt(customAmount) : selectedAmount || 0)}
                      </>
                    )}
                  </Button>
                  <p className="text-xs text-center text-muted-foreground">
                    Demo mode - No real payment will be processed
                  </p>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}
