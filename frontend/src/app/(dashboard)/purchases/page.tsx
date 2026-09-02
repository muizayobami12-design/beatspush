'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Download, Music, Clock, CheckCircle, XCircle, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import type { Transaction } from '@/lib/payment/paystack';

export default function PurchasesPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading] = useState(false);

  // Mock data - will be replaced with real API call
  const transactions: Transaction[] = [
    {
      id: '1',
      reference: 'BP-1234567890-123456',
      amount: 29.99,
      currency: 'USD',
      status: 'success',
      beatId: 'beat-1',
      beatTitle: 'Sunset Vibes',
      createdAt: '2026-08-01T10:30:00Z',
      paidAt: '2026-08-01T10:31:00Z',
    },
    {
      id: '2',
      reference: 'BP-1234567891-123457',
      amount: 49.99,
      currency: 'USD',
      status: 'success',
      beatId: 'beat-2',
      beatTitle: 'Midnight Flow',
      createdAt: '2026-07-28T14:20:00Z',
      paidAt: '2026-07-28T14:21:00Z',
    },
    {
      id: '3',
      reference: 'BP-1234567892-123458',
      amount: 19.99,
      currency: 'USD',
      status: 'failed',
      beatId: 'beat-3',
      beatTitle: 'Summer Breeze',
      createdAt: '2026-07-25T09:15:00Z',
    },
  ];

  // Filter transactions
  const filteredTransactions = transactions.filter((transaction) =>
    transaction.beatTitle?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    transaction.reference.toLowerCase().includes(searchQuery.toLowerCase())
  );

  // Stats
  const totalSpent = transactions
    .filter((t) => t.status === 'success')
    .reduce((sum, t) => sum + t.amount, 0);
  
  const successfulPurchases = transactions.filter((t) => t.status === 'success').length;

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      default:
        return <Clock className="w-5 h-5 text-muted-foreground" />;
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'success':
        return <span className="text-green-500">Completed</span>;
      case 'failed':
        return <span className="text-red-500">Failed</span>;
      case 'pending':
        return <span className="text-yellow-500">Pending</span>;
      case 'abandoned':
        return <span className="text-muted-foreground">Cancelled</span>;
      default:
        return <span className="text-muted-foreground">{status}</span>;
    }
  };

  if (isLoading) {
    return (
      <div className="container max-w-6xl py-8 space-y-6">
        <Skeleton className="h-10 w-64" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
          <Skeleton className="h-32" />
        </div>
        <Skeleton className="h-96" />
      </div>
    );
  }

  return (
    <div className="container max-w-6xl py-8 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">My Purchases</h1>
        <p className="text-muted-foreground mt-2">
          View and download your purchased beats
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card border rounded-lg p-6">
          <p className="text-sm text-muted-foreground mb-2">Total Spent</p>
          <p className="text-3xl font-bold">${totalSpent.toFixed(2)}</p>
        </div>
        
        <div className="bg-card border rounded-lg p-6">
          <p className="text-sm text-muted-foreground mb-2">Beats Purchased</p>
          <p className="text-3xl font-bold">{successfulPurchases}</p>
        </div>
        
        <div className="bg-card border rounded-lg p-6">
          <p className="text-sm text-muted-foreground mb-2">Total Transactions</p>
          <p className="text-3xl font-bold">{transactions.length}</p>
        </div>
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
        <Input
          placeholder="Search by beat title or reference..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-10"
        />
      </div>

      {/* Transactions List */}
      <div className="space-y-4">
        {filteredTransactions.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <Music className="w-16 h-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">
              {searchQuery ? 'No transactions found' : 'No purchases yet'}
            </h3>
            <p className="text-muted-foreground mb-6">
              {searchQuery
                ? 'Try a different search term'
                : 'Start by exploring our beat marketplace'}
            </p>
            {!searchQuery && (
              <Link href="/beats">
                <Button>Browse Beats</Button>
              </Link>
            )}
          </div>
        ) : (
          filteredTransactions.map((transaction) => (
            <div
              key={transaction.id}
              className="bg-card border rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex flex-col md:flex-row md:items-center gap-4">
                {/* Beat Info */}
                <div className="flex items-center gap-4 flex-1">
                  <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-[#667eea] to-[#764ba2] flex items-center justify-center flex-shrink-0">
                    <Music className="w-6 h-6 text-white" />
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <h3 className="font-semibold truncate">{transaction.beatTitle}</h3>
                    <p className="text-sm text-muted-foreground">
                      {formatDate(transaction.createdAt)}
                    </p>
                  </div>
                </div>

                {/* Amount */}
                <div className="text-left md:text-right">
                  <p className="font-bold text-lg">
                    ${transaction.amount.toFixed(2)}
                  </p>
                  <p className="text-sm text-muted-foreground">{transaction.currency}</p>
                </div>

                {/* Status */}
                <div className="flex items-center gap-2">
                  {getStatusIcon(transaction.status)}
                  {getStatusText(transaction.status)}
                </div>

                {/* Actions */}
                <div className="flex gap-2">
                  {transaction.status === 'success' && (
                    <>
                      <Button size="sm" variant="outline">
                        <Download className="w-4 h-4 mr-2" />
                        Download
                      </Button>
                      <Link href={`/beats/${transaction.beatId}`}>
                        <Button size="sm" variant="ghost">
                          View
                        </Button>
                      </Link>
                    </>
                  )}
                  
                  {transaction.status === 'failed' && (
                    <Button size="sm" variant="outline">
                      Retry
                    </Button>
                  )}
                </div>
              </div>

              {/* Reference (collapsible) */}
              <div className="mt-4 pt-4 border-t">
                <p className="text-xs text-muted-foreground">
                  Reference: <code className="bg-muted px-2 py-1 rounded">{transaction.reference}</code>
                </p>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
