'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Modal } from '@/components/ui/Modal';
import { Loader2 } from 'lucide-react';
import messagingService from '@/services/messagingService';
import { useToast } from '@/hooks/useToast';

interface BlockUserModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId: string;
  userName: string;
  /** Called after a successful block so parent can hide the conversation */
  onBlocked: () => void;
}

/**
 * BlockUserModal — confirms and processes blocking a user. Task 22.3
 */
export function BlockUserModal({ isOpen, onClose, userId, userName, onBlocked }: BlockUserModalProps) {
  const { toast } = useToast();
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);

  const handleBlock = async () => {
    setLoading(true);
    try {
      await messagingService.blockUser(userId, reason.trim() || undefined);
      toast({ title: `${userName} has been blocked`, variant: 'success' });
      onBlocked();
      onClose();
    } catch {
      toast({ title: 'Failed to block user', variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Block ${userName}?`}>
      <div className="space-y-4">
        <p className="text-sm text-muted-foreground">
          Blocking will hide your conversation and prevent {userName} from messaging you.
          They won't be notified.
        </p>

        <div>
          <label className="text-sm font-medium mb-1 block">Reason (optional)</label>
          <Textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Harassment, spam, etc."
            maxLength={500}
            rows={3}
          />
          <p className="text-xs text-muted-foreground mt-1">{reason.length}/500</p>
        </div>

        <div className="flex gap-2 justify-end">
          <Button variant="outline" onClick={onClose} disabled={loading}>Cancel</Button>
          <Button variant="destructive" onClick={handleBlock} disabled={loading}>
            {loading ? <><Loader2 className="h-4 w-4 mr-2 animate-spin" />Blocking...</> : 'Block User'}
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default BlockUserModal;
