'use client';

import { useState, useMemo } from 'react';
import { Calendar, Clock, MapPin, Phone, MessageSquare, CheckCircle, XCircle, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { DateRangePicker } from '@/components/ui/date-range-picker';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

type BookingStatus = 'pending' | 'confirmed' | 'completed' | 'cancelled';

interface Booking {
  id: string;
  clientName: string;
  clientPhone: string;
  beatTitle: string;
  beatId: string;
  bookingDate: Date;
  duration: number; // in hours
  location: string;
  status: BookingStatus;
  notes?: string;
  totalPrice: number;
  createdAt: Date;
}

// Mock bookings data
const MOCK_BOOKINGS: Booking[] = [
  {
    id: '1',
    clientName: 'Chioma Okonkwo',
    clientPhone: '+234 802 123 4567',
    beatTitle: 'Lagos Nights',
    beatId: 'beat-2',
    bookingDate: new Date(Date.now() + 2 * 24 * 60 * 60000),
    duration: 3,
    location: 'Studio A, Lagos',
    status: 'confirmed',
    notes: 'Client prefers afternoon session',
    totalPrice: 50000,
    createdAt: new Date(Date.now() - 5 * 24 * 60 * 60000),
  },
  {
    id: '2',
    clientName: 'Tunde Adeyemi',
    clientPhone: '+234 705 987 6543',
    beatTitle: 'Midnight Voyage',
    beatId: 'beat-1',
    bookingDate: new Date(Date.now() + 10 * 24 * 60 * 60000),
    duration: 2,
    location: 'Remote',
    status: 'pending',
    totalPrice: 35000,
    createdAt: new Date(Date.now() - 1 * 24 * 60 * 60000),
  },
  {
    id: '3',
    clientName: 'Zaria Music Group',
    clientPhone: '+234 803 456 7890',
    beatTitle: 'Heritage',
    beatId: 'beat-3',
    bookingDate: new Date(Date.now() - 5 * 24 * 60 * 60000),
    duration: 4,
    location: 'Studio C, Abuja',
    status: 'completed',
    notes: 'Session completed successfully',
    totalPrice: 75000,
    createdAt: new Date(Date.now() - 15 * 24 * 60 * 60000),
  },
  {
    id: '4',
    clientName: 'DJ Thunder',
    clientPhone: '+234 812 567 8901',
    beatTitle: 'Afrosynth Wave',
    beatId: 'beat-5',
    bookingDate: new Date(Date.now() - 2 * 24 * 60 * 60000),
    duration: 5,
    location: 'Studio B, Lagos',
    status: 'cancelled',
    notes: 'Client cancelled due to schedule conflict',
    totalPrice: 85000,
    createdAt: new Date(Date.now() - 10 * 24 * 60 * 60000),
  },
];

const STATUS_COLORS: Record<BookingStatus, string> = {
  pending: 'bg-tertiary/20 text-tertiary border-tertiary/30',
  confirmed: 'bg-secondary/20 text-secondary border-secondary/30',
  completed: 'bg-secondary-fixed/20 text-secondary-fixed border-secondary-fixed/30',
  cancelled: 'bg-destructive/20 text-destructive border-destructive/30',
};

const STATUS_ICONS: Record<BookingStatus, React.ReactNode> = {
  pending: <Clock className="h-4 w-4" />,
  confirmed: <CheckCircle className="h-4 w-4" />,
  completed: <CheckCircle className="h-4 w-4" />,
  cancelled: <XCircle className="h-4 w-4" />,
};

export default function BookingsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<BookingStatus | 'all'>('all');
  const [dateRange, setDateRange] = useState<{ start: Date; end: Date } | null>(null);
  const [selectedBooking, setSelectedBooking] = useState<Booking | null>(null);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');

  // Filter bookings
  const filteredBookings = useMemo(() => {
    let bookings = [...MOCK_BOOKINGS];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      bookings = bookings.filter(
        (b) =>
          b.clientName.toLowerCase().includes(query) ||
          b.beatTitle.toLowerCase().includes(query) ||
          b.clientPhone.includes(query)
      );
    }

    // Status filter
    if (selectedStatus !== 'all') {
      bookings = bookings.filter((b) => b.status === selectedStatus);
    }

    // Date range filter
    if (dateRange) {
      bookings = bookings.filter((b) => {
        const bookingDate = b.bookingDate.getTime();
        const startTime = dateRange.start.getTime();
        const endTime = dateRange.end.getTime();
        return bookingDate >= startTime && bookingDate <= endTime;
      });
    }

    // Sort by booking date
    bookings.sort((a, b) => b.bookingDate.getTime() - a.bookingDate.getTime());

    return bookings;
  }, [searchQuery, selectedStatus, dateRange]);

  // Calculate statistics
  const stats = useMemo(
    () => ({
      total: MOCK_BOOKINGS.length,
      pending: MOCK_BOOKINGS.filter((b) => b.status === 'pending').length,
      confirmed: MOCK_BOOKINGS.filter((b) => b.status === 'confirmed').length,
      completed: MOCK_BOOKINGS.filter((b) => b.status === 'completed').length,
      totalRevenue: MOCK_BOOKINGS.filter((b) => b.status === 'completed').reduce((sum, b) => sum + b.totalPrice, 0),
    }),
    []
  );

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-NG', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="min-h-screen bg-background pb-8">
      <div className="max-w-container-max mx-auto px-margin-mobile md:px-margin-desktop py-stack-lg">
        {/* Header */}
        <div className="mb-stack-lg">
          <div className="flex items-center gap-3 mb-2">
            <div className={cn(
              'p-3 rounded-lg',
              'bg-surface-container border border-outline-variant/20'
            )}>
              <Calendar className="h-6 w-6 text-secondary" />
            </div>
            <div>
              <h1 className={cn(
                'font-headline-lg text-headline-lg-mobile md:text-headline-lg',
                'text-on-surface'
              )}>
                Bookings
              </h1>
              <p className={cn(
                'font-body-md text-body-md',
                'text-on-surface-variant'
              )}>
                Manage your beat bookings and sessions
              </p>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-gutter mb-stack-lg">
          {[
            { label: 'Total Bookings', value: stats.total, color: 'text-secondary' },
            { label: 'Pending', value: stats.pending, color: 'text-tertiary' },
            { label: 'Confirmed', value: stats.confirmed, color: 'text-secondary' },
            { label: 'Revenue', value: formatCurrency(stats.totalRevenue), color: 'text-secondary-fixed' },
          ].map((stat, i) => (
            <div
              key={i}
              className={cn(
                'rounded-lg border ghost-border p-stack-md',
                'bg-surface-container'
              )}
            >
              <p className={cn(
                'font-label-sm text-label-sm uppercase tracking-wider',
                'text-on-surface-variant'
              )}>
                {stat.label}
              </p>
              <p className={cn(
                'font-headline-md text-headline-md mt-2',
                stat.color
              )}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>

        {/* Filters */}
        <div className={cn(
          'rounded-lg border ghost-border p-stack-md mb-stack-lg',
          'bg-surface-container-low space-y-4'
        )}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-gutter">
            {/* Search */}
            <div className="md:col-span-2">
              <label className={cn(
                'font-label-sm text-label-sm block mb-2',
                'text-on-surface-variant uppercase tracking-wider'
              )}>
                Search
              </label>
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-on-surface-variant" />
                <Input
                  type="text"
                  placeholder="Search by client, beat, or phone..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className={cn(
                    'pl-10',
                    'bg-surface-container border border-outline-variant/30',
                    'text-on-surface placeholder-on-surface-variant/50'
                  )}
                />
              </div>
            </div>

            {/* Status Filter */}
            <div>
              <label className={cn(
                'font-label-sm text-label-sm block mb-2',
                'text-on-surface-variant uppercase tracking-wider'
              )}>
                Status
              </label>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value as BookingStatus | 'all')}
                className={cn(
                  'w-full px-3 py-2 rounded-lg',
                  'bg-surface-container border border-outline-variant/30',
                  'text-on-surface font-body-md',
                  'focus:outline-none focus:ring-2 focus:ring-secondary/40'
                )}
              >
                <option value="all">All Status</option>
                <option value="pending">Pending</option>
                <option value="confirmed">Confirmed</option>
                <option value="completed">Completed</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
          </div>

          {/* Date Range Filter */}
          <div>
            <label className={cn(
              'font-label-sm text-label-sm block mb-2',
              'text-on-surface-variant uppercase tracking-wider'
            )}>
              Date Range
            </label>
            <DateRangePicker
              onDateRangeChange={(range) => setDateRange(range)}
            />
          </div>
        </div>

        {/* Bookings List/Grid */}
        {filteredBookings.length > 0 ? (
          <>
            <p className={cn(
              'font-body-md text-body-md mb-stack-md',
              'text-on-surface-variant'
            )}>
              Showing {filteredBookings.length} booking{filteredBookings.length !== 1 ? 's' : ''}
            </p>

            <div className={cn(
              'space-y-4'
            )}>
              {filteredBookings.map((booking) => (
                <div
                  key={booking.id}
                  className={cn(
                    'rounded-lg border ghost-border p-stack-md',
                    'bg-surface-container hover:bg-surface-container-low',
                    'transition-colors cursor-pointer'
                  )}
                  onClick={() => setSelectedBooking(booking)}
                >
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-3">
                    {/* Client Info */}
                    <div>
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Client
                      </p>
                      <p className={cn(
                        'font-body-md text-body-md mt-1',
                        'text-on-surface'
                      )}>
                        {booking.clientName}
                      </p>
                    </div>

                    {/* Beat Info */}
                    <div>
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Beat
                      </p>
                      <p className={cn(
                        'font-body-md text-body-md mt-1',
                        'text-on-surface'
                      )}>
                        {booking.beatTitle}
                      </p>
                    </div>

                    {/* Date & Time */}
                    <div>
                      <p className={cn(
                        'font-label-sm text-label-sm',
                        'text-on-surface-variant uppercase tracking-wider'
                      )}>
                        Session Date
                      </p>
                      <p className={cn(
                        'font-body-md text-body-md mt-1',
                        'text-on-surface'
                      )}>
                        {formatDate(booking.bookingDate)}
                      </p>
                    </div>

                    {/* Status */}
                    <div className="flex items-end">
                      <div className={cn(
                        'inline-flex items-center gap-2 px-3 py-1 rounded-full',
                        'font-label-sm text-label-sm border',
                        STATUS_COLORS[booking.status]
                      )}>
                        {STATUS_ICONS[booking.status]}
                        {booking.status.charAt(0).toUpperCase() + booking.status.slice(1)}
                      </div>
                    </div>
                  </div>

                  {/* Details Row */}
                  <div className="flex flex-wrap items-center gap-4 pt-3 border-t border-outline-variant/20">
                    <div className="flex items-center gap-2 text-on-surface-variant">
                      <Clock className="h-4 w-4" />
                      <span className="text-sm">{booking.duration}h session</span>
                    </div>

                    <div className="flex items-center gap-2 text-on-surface-variant">
                      <MapPin className="h-4 w-4" />
                      <span className="text-sm">{booking.location}</span>
                    </div>

                    <div className="flex items-center gap-2 text-on-surface-variant">
                      <Phone className="h-4 w-4" />
                      <span className="text-sm">{booking.clientPhone}</span>
                    </div>

                    <div className="ml-auto">
                      <p className={cn(
                        'font-label-md text-label-md',
                        'text-secondary font-bold'
                      )}>
                        {formatCurrency(booking.totalPrice)}
                      </p>
                    </div>
                  </div>

                  {/* Actions */}
                  {booking.status === 'pending' && (
                    <div className="flex gap-2 mt-4 pt-3 border-t border-outline-variant/20">
                      <Button size="sm" variant="default">
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Confirm
                      </Button>
                      <Button size="sm" variant="outline">
                        <XCircle className="h-4 w-4 mr-2" />
                        Decline
                      </Button>
                      <Button size="sm" variant="outline" className="ml-auto gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Message
                      </Button>
                    </div>
                  )}

                  {booking.status === 'confirmed' && (
                    <div className="flex gap-2 mt-4 pt-3 border-t border-outline-variant/20">
                      <Button size="sm" variant="outline" className="gap-2">
                        <MessageSquare className="h-4 w-4" />
                        Message Client
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </>
        ) : (
          /* Empty State */
          <div className={cn(
            'rounded-lg border ghost-border p-stack-lg',
            'bg-surface-container-low text-center'
          )}>
            <Calendar className="h-12 w-12 text-on-surface-variant/50 mx-auto mb-4" />
            <p className={cn(
              'font-body-md text-body-md',
              'text-on-surface-variant'
            )}>
              No bookings found
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
