'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Modal } from '@/components/ui/Modal';
import { Loader2 } from 'lucide-react';
import messagingService from '@/services/messagingService';
import { useToast } from '@/hooks/useToast';

interface ReportMessageModalProps {
  isOpen: boolean;
  onClose: () => void;
  messageId: string;
}

const REASONS = [
  { value: 'spam', label: 'Spam' },
  { value: 'harassment', label: 'Harassment or bullying' },
  { value: 'inappropriate', label: 'Inappropriate content' },
  { value: 'other', label: 'Other' },
] as const;

type Reason = (typeof REASONS)[number]['value'];

/**
 * ReportMessageModal — lets users report a specific message. Task 22.3
 */
export function ReportMessageModal({ isOpen, onClose, messageId }: ReportMessageModalProps) {
  const { toast } = useToast();
  const [reason, setReason] = useState<Reason>('spam');
  const [details, setDetails] = useState('');
  const [loading, setLoading] = useState(false);

  const handleReport = async () => {
    setLoading(true);
    try {
      await messagingService.reportMessage(messageId, {
        reason,
        details: details.trim() || undefined,
      });
      toast({ title: 'Message reported. Thank you.', variant: 'success' });
      onClose();
    } catch {
      toast({ title: 'Failed to submit report', variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Report Message">
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Reports are reviewed privately. The sender won't be notified that you reported them.
        </p>

        <div className="space-y-2">
          <label className="text-sm font-medium block">Reason</label>
          {REASONS.map((r) => (
            <button
              key={r.value}
              type="button"
              onClick={() => setReason(r.value)}
              className={`w-full text-left px-3 py-2 rounded-lg border text-sm transition-colors ${
                reason === r.value
                  ? 'border-primary bg-primary/5 font-medium'
                  : 'border-border hover:bg-muted/50'
              }`}
            >
              {r.label}
            </button>
          ))}
        </div>

        <div>
          <label className="text-sm font-medium mb-1 block">Additional details (optional)</label>
          <Textarea
            value={details}
            onChange={(e) => setDetails(e.target.value)}
            placeholder="Describe what happened..."
            maxLength={500}
            rows={3}
          />
          <p className="text-xs text-muted-foreground mt-1">{details.length}/500</p>
        </div>

        <div className="flex gap-2 justify-end">
          <Button variant="outline" onClick={onClose} disabled={loading}>Cancel</Button>
          <Button onClick={handleReport} disabled={loading}>
            {loading ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Submitting...</> : 'Submit Report'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default ReportMessageModal;
