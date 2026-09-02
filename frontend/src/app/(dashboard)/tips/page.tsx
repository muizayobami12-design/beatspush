'use client';

import { useState, useMemo } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import {
  Heart,
  TrendingUp,
  Wallet,
  Send,
  Download,
  Calendar,
  User,
  ArrowUpRight,
  Filter,
  Search,
  Clock,
  CheckCircle2,
  AlertCircle,
} from 'lucide-react';
import { useToast } from '@/hooks/useToast';

interface TipTransaction {
  id: string;
  senderId: string;
  senderName: string;
  senderAvatar?: string;
  amount: number;
  message?: string;
  contentType: 'beat' | 'track' | 'profile' | 'livestream';
  contentTitle: string;
  timestamp: string;
}

interface TipperRank {
  rank: number;
  senderId: string;
  name: string;
  avatar?: string;
  totalTips: number;
  tipCount: number;
  lastTip: string;
}

interface WithdrawalRequest {
  id: string;
  amount: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  bankName: string;
  accountNumber: string;
  requestedAt: string;
  completedAt?: string;
}

const MOCK_TIP_TRANSACTIONS: TipTransaction[] = [
  {
    id: '1',
    senderId: 'user-1',
    senderName: 'DJ Thunder',
    amount: 10000,
    message: 'Fire beat! 🔥',
    contentType: 'beat',
    contentTitle: 'Summer Vibes',
    timestamp: '2024-02-15T14:30:00Z',
  },
  {
    id: '2',
    senderId: 'user-2',
    senderName: 'Producer Alex',
    amount: 5000,
    contentType: 'track',
    contentTitle: 'Midnight Flow',
    timestamp: '2024-02-15T10:15:00Z',
  },
  {
    id: '3',
    senderId: 'user-3',
    senderName: 'Music Fan',
    amount: 2500,
    message: 'Love your style!',
    contentType: 'profile',
    contentTitle: 'Profile Support',
    timestamp: '2024-02-14T22:45:00Z',
  },
  {
    id: '4',
    senderId: 'user-4',
    senderName: 'Live Stream Watcher',
    amount: 15000,
    contentType: 'livestream',
    contentTitle: 'Live Session',
    timestamp: '2024-02-14T19:20:00Z',
  },
  {
    id: '5',
    senderId: 'user-5',
    senderName: 'Collector',
    amount: 3000,
    message: 'Keep it up!',
    contentType: 'beat',
    contentTitle: 'Boom Bap Classic',
    timestamp: '2024-02-13T16:00:00Z',
  },
];

const MOCK_TOP_TIPPERS: TipperRank[] = [
  {
    rank: 1,
    senderId: 'user-1',
    name: 'DJ Thunder',
    totalTips: 125000,
    tipCount: 12,
    lastTip: '2024-02-15T14:30:00Z',
  },
  {
    rank: 2,
    senderId: 'user-2',
    name: 'Producer Alex',
    totalTips: 98000,
    tipCount: 15,
    lastTip: '2024-02-15T10:15:00Z',
  },
  {
    rank: 3,
    senderId: 'user-3',
    name: 'Music Fan',
    totalTips: 67500,
    tipCount: 8,
    lastTip: '2024-02-14T22:45:00Z',
  },
  {
    rank: 4,
    senderId: 'user-4',
    name: 'Live Stream Watcher',
    totalTips: 45000,
    tipCount: 5,
    lastTip: '2024-02-14T19:20:00Z',
  },
  {
    rank: 5,
    senderId: 'user-5',
    name: 'Collector',
    totalTips: 32500,
    tipCount: 9,
    lastTip: '2024-02-13T16:00:00Z',
  },
];

const MOCK_WITHDRAWALS: WithdrawalRequest[] = [
  {
    id: 'w-1',
    amount: 250000,
    status: 'completed',
    bankName: 'GTBank',
    accountNumber: '****5678',
    requestedAt: '2024-02-10T08:00:00Z',
    completedAt: '2024-02-11T14:30:00Z',
  },
  {
    id: 'w-2',
    amount: 150000,
    status: 'processing',
    bankName: 'First Bank',
    accountNumber: '****1234',
    requestedAt: '2024-02-15T10:00:00Z',
  },
  {
    id: 'w-3',
    amount: 500000,
    status: 'pending',
    bankName: 'Access Bank',
    accountNumber: '****9999',
    requestedAt: '2024-02-15T16:00:00Z',
  },
];

export default function TipsPage() {
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<'overview' | 'transactions' | 'leaderboard' | 'withdraw'>('overview');
  const [showWithdrawalModal, setShowWithdrawalModal] = useState(false);
  const [withdrawAmount, setWithdrawAmount] = useState('');
  const [selectedBank, setSelectedBank] = useState('');
  const [accountNumber, setAccountNumber] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const totalTipsEarned = useMemo(
    () => MOCK_TIP_TRANSACTIONS.reduce((sum, t) => sum + t.amount, 0),
    []
  );

  const thisMonthTips = useMemo(
    () => MOCK_TIP_TRANSACTIONS.filter(
      (t) => new Date(t.timestamp).getMonth() === new Date().getMonth()
    ).reduce((sum, t) => sum + t.amount, 0),
    []
  );

  const filteredTransactions = useMemo(
    () => MOCK_TIP_TRANSACTIONS.filter(
      (t) =>
        t.senderName.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.contentTitle.toLowerCase().includes(searchQuery.toLowerCase())
    ),
    [searchQuery]
  );

  const handleWithdrawal = async () => {
    if (!withdrawAmount || !selectedBank || !accountNumber) {
      toast({
        title: 'Error',
        description: 'Please fill in all fields',
        variant: 'destructive',
      });
      return;
    }

    const amount = parseInt(withdrawAmount);
    if (amount < 10000) {
      toast({
        title: 'Error',
        description: 'Minimum withdrawal amount is ₦10,000',
        variant: 'destructive',
      });
      return;
    }

    if (amount > totalTipsEarned) {
      toast({
        title: 'Error',
        description: 'Insufficient balance',
        variant: 'destructive',
      });
      return;
    }

    setIsProcessing(true);

    try {
      const response = await fetch('/api/v1/tips/withdraw', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount,
          bank_name: selectedBank,
          account_number: accountNumber,
        }),
      });

      if (!response.ok) throw new Error('Withdrawal failed');

      toast({
        title: 'Success',
        description: 'Withdrawal request submitted. Processing may take 1-2 business days.',
      });

      setShowWithdrawalModal(false);
      setWithdrawAmount('');
      setSelectedBank('');
      setAccountNumber('');
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to process withdrawal',
        variant: 'destructive',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'processing':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle2 className="w-4 h-4" />;
      case 'processing':
        return <Clock className="w-4 h-4" />;
      case 'pending':
        return <AlertCircle className="w-4 h-4" />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 via-gray-800 to-gray-900 py-8">
      <div className="container mx-auto px-4 max-w-6xl">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Heart className="w-8 h-8 text-red-500" />
              <h1 className="text-4xl font-bold text-white">Tips</h1>
            </div>
            <Button
              onClick={() => setShowWithdrawalModal(true)}
              className="gap-2 bg-purple-600 hover:bg-purple-700"
            >
              <Send className="w-4 h-4" />
              Withdraw Tips
            </Button>
          </div>
          <p className="text-gray-400 mt-2">Earn and manage tips from your fans</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-card rounded-lg border border-border p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Total Tips Earned</p>
                <p className="text-3xl font-bold text-white mt-2">
                  ₦{totalTipsEarned.toLocaleString()}
                </p>
              </div>
              <Heart className="w-8 h-8 text-red-500 opacity-20" />
            </div>
          </div>

          <div className="bg-card rounded-lg border border-border p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">This Month</p>
                <p className="text-3xl font-bold text-white mt-2">
                  ₦{thisMonthTips.toLocaleString()}
                </p>
              </div>
              <TrendingUp className="w-8 h-8 text-purple-500 opacity-20" />
            </div>
          </div>

          <div className="bg-card rounded-lg border border-border p-6">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-gray-400 text-sm font-medium">Total Supporters</p>
                <p className="text-3xl font-bold text-white mt-2">{MOCK_TOP_TIPPERS.length}</p>
              </div>
              <User className="w-8 h-8 text-blue-500 opacity-20" />
            </div>
          </div>
        </div>

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4 bg-gray-800 border border-gray-700">
            <TabsTrigger value="overview" className="flex items-center gap-2">
              <Heart className="w-4 h-4" />
              Overview
            </TabsTrigger>
            <TabsTrigger value="transactions" className="flex items-center gap-2">
              <ArrowUpRight className="w-4 h-4" />
              Transactions
            </TabsTrigger>
            <TabsTrigger value="leaderboard" className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Top Tippers
            </TabsTrigger>
            <TabsTrigger value="withdraw" className="flex items-center gap-2">
              <Wallet className="w-4 h-4" />
              Withdrawals
            </TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            <div className="bg-card rounded-lg border border-border p-6">
              <h2 className="text-xl font-bold text-white mb-4">Recent Tips</h2>
              <div className="space-y-3">
                {MOCK_TIP_TRANSACTIONS.slice(0, 5).map((tip) => (
                  <div
                    key={tip.id}
                    className="flex items-center justify-between p-4 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500" />
                        <div>
                          <p className="text-white font-medium">{tip.senderName}</p>
                          <p className="text-xs text-gray-400">on {tip.contentTitle}</p>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-purple-400">₦{tip.amount.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(tip.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Transactions Tab */}
          <TabsContent value="transactions" className="space-y-4">
            <div className="bg-card rounded-lg border border-border p-4">
              <div className="flex items-center gap-2 mb-4">
                <Search className="w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search by name or content..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="flex-1 bg-transparent border-0 text-white placeholder-gray-500 focus:outline-none"
                />
              </div>
            </div>

            <div className="space-y-3">
              {filteredTransactions.map((tip) => (
                <div key={tip.id} className="bg-card rounded-lg border border-border p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3 flex-1">
                      <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-500" />
                      <div className="flex-1">
                        <h3 className="text-white font-semibold">{tip.senderName}</h3>
                        <p className="text-sm text-gray-400">{tip.contentTitle}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-lg font-bold text-purple-400">+₦{tip.amount.toLocaleString()}</p>
                      <p className="text-xs text-gray-500">
                        {new Date(tip.timestamp).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  {tip.message && (
                    <div className="pl-15 pr-4 py-2 bg-gray-800/50 rounded border border-gray-700">
                      <p className="text-sm text-gray-300 italic">"{tip.message}"</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </TabsContent>

          {/* Leaderboard Tab */}
          <TabsContent value="leaderboard" className="space-y-4">
            <div className="bg-card rounded-lg border border-border overflow-hidden">
              <div className="p-6 border-b border-border">
                <h2 className="text-xl font-bold text-white">Top Supporters</h2>
                <p className="text-gray-400 text-sm mt-1">Your most generous tippers</p>
              </div>

              <div className="space-y-2">
                {MOCK_TOP_TIPPERS.map((tipper) => (
                  <div
                    key={tipper.senderId}
                    className="p-4 hover:bg-gray-800/50 transition flex items-center justify-between border-b border-gray-700 last:border-0"
                  >
                    <div className="flex items-center gap-4 flex-1">
                      <div className="w-8 h-8 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold">
                        {tipper.rank}
                      </div>

                      <div className="flex-1">
                        <p className="text-white font-medium">{tipper.name}</p>
                        <p className="text-xs text-gray-500">{tipper.tipCount} tips</p>
                      </div>
                    </div>

                    <div className="text-right">
                      <p className="text-lg font-bold text-purple-400">
                        ₦{tipper.totalTips.toLocaleString()}
                      </p>
                      <p className="text-xs text-gray-500">
                        Last: {new Date(tipper.lastTip).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>

          {/* Withdrawals Tab */}
          <TabsContent value="withdraw" className="space-y-4">
            <div className="bg-card rounded-lg border border-border p-6">
              <h2 className="text-xl font-bold text-white mb-4">Withdrawal History</h2>
              <div className="space-y-3">
                {MOCK_WITHDRAWALS.map((withdrawal) => (
                  <div key={withdrawal.id} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <p className="text-white font-semibold">₦{withdrawal.amount.toLocaleString()}</p>
                          <div className={`flex items-center gap-1 px-2 py-1 rounded border ${getStatusColor(withdrawal.status)}`}>
                            {getStatusIcon(withdrawal.status)}
                            <span className="text-xs font-medium capitalize">{withdrawal.status}</span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-400">{withdrawal.bankName} • {withdrawal.accountNumber}</p>
                      </div>
                      <div className="text-right text-sm text-gray-500">
                        <p>Requested: {new Date(withdrawal.requestedAt).toLocaleDateString()}</p>
                        {withdrawal.completedAt && (
                          <p>Completed: {new Date(withdrawal.completedAt).toLocaleDateString()}</p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </TabsContent>
        </Tabs>

        {/* Withdrawal Modal */}
        {showWithdrawalModal && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50">
            <div className="bg-card rounded-lg border border-border max-w-md w-full">
              <div className="p-6 border-b border-border">
                <h2 className="text-xl font-bold text-white">Request Withdrawal</h2>
                <p className="text-gray-400 text-sm mt-1">
                  Available balance: ₦{totalTipsEarned.toLocaleString()}
                </p>
              </div>

              <div className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Withdrawal Amount
                  </label>
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium">₦</span>
                    <input
                      type="number"
                      value={withdrawAmount}
                      onChange={(e) => setWithdrawAmount(e.target.value)}
                      placeholder="10,000 minimum"
                      min="10000"
                      max={totalTipsEarned}
                      className="flex-1 px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Bank Name
                  </label>
                  <select
                    value={selectedBank}
                    onChange={(e) => setSelectedBank(e.target.value)}
                    className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white focus:outline-none focus:border-purple-500"
                  >
                    <option value="">Select bank</option>
                    <option value="gtbank">GTBank</option>
                    <option value="firstbank">First Bank</option>
                    <option value="accessbank">Access Bank</option>
                    <option value="zenithbank">Zenith Bank</option>
                    <option value="ubabank">UBA</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-white mb-2">
                    Account Number
                  </label>
                  <input
                    type="text"
                    value={accountNumber}
                    onChange={(e) => setAccountNumber(e.target.value)}
                    placeholder="10 digits"
                    maxLength={10}
                    className="w-full px-3 py-2 rounded-lg bg-gray-800 border border-gray-700 text-white placeholder-gray-500 focus:outline-none focus:border-purple-500"
                  />
                </div>

                <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-3">
                  <p className="text-sm text-blue-200">
                    Processing takes 1-2 business days. A platform fee of 2% will be deducted.
                  </p>
                </div>
              </div>

              <div className="flex gap-2 p-6 border-t border-border">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setShowWithdrawalModal(false)}
                  disabled={isProcessing}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1 bg-purple-600 hover:bg-purple-700"
                  onClick={handleWithdrawal}
                  disabled={isProcessing}
                >
                  {isProcessing ? 'Processing...' : 'Request Withdrawal'}
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
