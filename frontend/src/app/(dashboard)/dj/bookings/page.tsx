'use client';

import { useState, useEffect } from 'react';
import { ArrowLeft, Calendar, MapPin, Clock, DollarSign, User, CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface Booking {
  id: string;
  event_name: string;
  organizer_name: string;
  event_date: string;
  event_time: string;
  location: string;
  duration_hours: number;
  fee: number;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed';
  special_requests?: string;
  created_at: string;
}

export default function DJBookingsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');

  // Settings
  const [hourlyRate, setHourlyRate] = useState('15000');
  const [availability, setAvailability] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    // Simulate loading bookings
    setTimeout(() => {
      setIsLoading(false);
      // Mock data - replace with actual API call
      setBookings([]);
    }, 1000);
  }, []);

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-NG', {
      style: 'currency',
      currency: 'NGN',
      minimumFractionDigits: 0,
    }).format(price);
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'text-green-600 bg-green-100 dark:bg-green-900/20';
      case 'cancelled':
        return 'text-red-600 bg-red-100 dark:bg-red-900/20';
      case 'completed':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900/20';
      default:
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900/20';
    }
  };

  const filteredBookings = filter === 'all' 
    ? bookings 
    : bookings.filter(b => b.status === filter);

  return (
    <div className="min-h-screen bg-background pb-24">
      {/* Header */}
      <div className="border-b bg-card">
        <div className="container mx-auto px-4 py-6">
          <Link href="/dashboard">
            <Button variant="ghost" size="sm" className="gap-2 mb-4">
              <ArrowLeft className="h-4 w-4" />
              Back to Dashboard
            </Button>
          </Link>
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">DJ Bookings</h1>
              <p className="text-muted-foreground">
                Manage your event bookings and availability
              </p>
            </div>
            <Button onClick={() => setShowSettings(!showSettings)}>
              {showSettings ? 'Hide Settings' : 'Booking Settings'}
            </Button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-4 py-8">
        {/* Booking Settings */}
        {showSettings && (
          <div className="bg-card rounded-lg border p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Booking Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium mb-2">
                  Hourly Rate (₦)
                </label>
                <Input
                  type="number"
                  value={hourlyRate}
                  onChange={(e) => setHourlyRate(e.target.value)}
                  placeholder="15000"
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Your rate per hour for events
                </p>
              </div>

              <div>
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={availability}
                    onChange={(e) => setAvailability(e.target.checked)}
                    className="w-4 h-4 rounded border-input"
                  />
                  <span className="text-sm font-medium">Available for bookings</span>
                </label>
                <p className="text-xs text-muted-foreground mt-1">
                  Allow event organizers to book you
                </p>
              </div>
            </div>

            <Button className="mt-4">Save Settings</Button>
          </div>
        )}

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-card rounded-lg border p-4">
            <p className="text-sm text-muted-foreground mb-1">Total Bookings</p>
            <p className="text-2xl font-bold">{bookings.length}</p>
          </div>
          <div className="bg-card rounded-lg border p-4">
            <p className="text-sm text-muted-foreground mb-1">Pending</p>
            <p className="text-2xl font-bold">
              {bookings.filter((b) => b.status === 'pending').length}
            </p>
          </div>
          <div className="bg-card rounded-lg border p-4">
            <p className="text-sm text-muted-foreground mb-1">Confirmed</p>
            <p className="text-2xl font-bold">
              {bookings.filter((b) => b.status === 'confirmed').length}
            </p>
          </div>
          <div className="bg-card rounded-lg border p-4">
            <p className="text-sm text-muted-foreground mb-1">Total Earnings</p>
            <p className="text-2xl font-bold">
              {formatPrice(bookings.reduce((sum, b) => sum + b.fee, 0))}
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 mb-6">
          {['all', 'pending', 'confirmed', 'completed', 'cancelled'].map((status) => (
            <Button
              key={status}
              variant={filter === status ? 'default' : 'outline'}
              size="sm"
              onClick={() => setFilter(status)}
              className="capitalize"
            >
              {status}
            </Button>
          ))}
        </div>

        {/* Bookings List */}
        {isLoading ? (
          <div className="flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
          </div>
        ) : filteredBookings.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-16 text-center">
            <div className="p-4 rounded-full bg-muted mb-4">
              <Calendar className="h-12 w-12 text-muted-foreground" />
            </div>
            <h3 className="text-xl font-semibold mb-2">No bookings yet</h3>
            <p className="text-muted-foreground max-w-md mb-4">
              {availability
                ? 'Event organizers can book you directly from your profile.'
                : 'Enable availability to start receiving booking requests.'}
            </p>
            {!availability && (
              <Button onClick={() => setShowSettings(true)}>
                Enable Bookings
              </Button>
            )}
          </div>
        ) : (
          <div className="space-y-4">
            {filteredBookings.map((booking) => (
              <div
                key={booking.id}
                className="bg-card rounded-lg border p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between gap-4">
                  {/* Booking Info */}
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-lg font-semibold">{booking.event_name}</h3>
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${getStatusColor(
                          booking.status
                        )}`}
                      >
                        {booking.status}
                      </span>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                      <div className="flex items-center gap-2 text-sm">
                        <User className="h-4 w-4 text-muted-foreground" />
                        <span>{booking.organizer_name}</span>
                      </div>

                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="h-4 w-4 text-muted-foreground" />
                        <span>
                          {new Date(booking.event_date).toLocaleDateString()} at{' '}
                          {booking.event_time}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span>{booking.location}</span>
                      </div>

                      <div className="flex items-center gap-2 text-sm">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span>{booking.duration_hours} hours</span>
                      </div>

                      <div className="flex items-center gap-2 text-sm font-semibold text-primary">
                        <DollarSign className="h-4 w-4" />
                        <span>{formatPrice(booking.fee)}</span>
                      </div>
                    </div>

                    {booking.special_requests && (
                      <div className="p-3 rounded-lg bg-muted/50 text-sm">
                        <p className="font-medium mb-1">Special Requests:</p>
                        <p className="text-muted-foreground">{booking.special_requests}</p>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  {booking.status === 'pending' && (
                    <div className="flex flex-col gap-2">
                      <Button size="sm" className="gap-2">
                        <CheckCircle2 className="h-4 w-4" />
                        Accept
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="gap-2 text-red-600 hover:text-red-600"
                      >
                        <XCircle className="h-4 w-4" />
                        Decline
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Section */}
        <div className="mt-8 p-6 rounded-lg bg-blue-500/10 border border-blue-500/20">
          <div className="flex gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 dark:text-blue-400 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-blue-600 dark:text-blue-400 mb-1">
                How DJ Bookings Work
              </p>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Set your hourly rate and availability</li>
                <li>• Event organizers can request bookings from your profile</li>
                <li>• You receive ₦500 deposit when you accept</li>
                <li>• Full payment collected after event completion</li>
                <li>• Platform fee: 15% of total booking</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
