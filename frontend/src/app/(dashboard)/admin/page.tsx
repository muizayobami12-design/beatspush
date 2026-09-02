'use client';

import { motion } from 'framer-motion';
import { usePlatformStats } from '@/hooks/useAdmin';
import { Button } from '@/components/ui/button';
import { Users, Music, DollarSign, TrendingUp, UserPlus, BarChart3, Shield, ChevronRight } from 'lucide-react';
import Link from 'next/link';
import { Skeleton } from '@/components/ui/skeleton';
import { StatsCard } from '@/components/dashboards/shared/StatsCard';

export default function AdminDashboardPage() {
  const { data: stats, isLoading } = usePlatformStats();

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Skeleton className="h-10 w-64 mb-8" />
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Skeleton key={i} className="h-32" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background pb-24 md:pb-0">
      {/* Welcome Section */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="container mx-auto px-4 py-8 md:py-12"
      >
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-8">
          <div>
            <h1 className="text-4xl md:text-5xl font-black mb-2">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                Admin Dashboard
              </span>
            </h1>
            <p className="text-lg text-muted-foreground">
              Monitor and manage your BeatsPush platform.
            </p>
          </div>
          <Link href="/admin/users">
            <Button className="gap-2 px-6 py-3 h-auto text-base">
              <Users className="h-5 w-5" />
              Manage Users
            </Button>
          </Link>
        </div>
      </motion.div>

      {/* Stats Cards */}
      <motion.section
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="container mx-auto px-4 py-8"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard 
            icon={Users} 
            label="Total Users" 
            value={stats?.totalUsers?.toLocaleString() || '0'}
            change={{ value: 12, isPositive: true }}
          />
          <StatsCard 
            icon={TrendingUp} 
            label="Active Users" 
            value={stats?.activeUsers?.toLocaleString() || '0'}
            change={{ value: 8, isPositive: true }}
          />
          <StatsCard 
            icon={Music} 
            label="Total Tracks" 
            value={stats?.totalTracks?.toLocaleString() || '0'}
            change={{ value: 15, isPositive: true }}
          />
          <StatsCard 
            icon={DollarSign} 
            label="Total Revenue" 
            value={`₦${(stats?.totalRevenue || 0).toLocaleString()}`}
            change={{ value: 24, isPositive: true }}
          />
        </div>
      </motion.section>

      {/* Main Content Grid */}
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* User Growth Stats */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15 }}
          className="bg-card border border-primary/20 rounded-2xl p-8 hover:border-primary/40 transition-all"
        >
          <h2 className="text-2xl font-bold mb-8 flex items-center gap-2 text-foreground">
            <UserPlus className="w-6 h-6 text-blue-400" />
            User Growth Analytics
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              { period: 'Today', value: stats?.newUsersToday || 0, color: 'from-blue-500/20 to-blue-600/10' },
              { period: 'This Week', value: stats?.newUsersThisWeek || 0, color: 'from-emerald-500/20 to-emerald-600/10' },
              { period: 'This Month', value: stats?.newUsersThisMonth || 0, color: 'from-purple-500/20 to-purple-600/10' },
            ].map((stat, idx) => (
              <motion.div
                key={stat.period}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
                className={`bg-gradient-to-br ${stat.color} border border-primary/10 rounded-xl p-6 hover:border-primary/30 transition-all`}
              >
                <p className="text-sm text-muted-foreground mb-2">{stat.period}</p>
                <p className="text-4xl font-bold text-foreground">{stat.value}</p>
                <p className="text-xs text-muted-foreground mt-2">New users registered</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* Platform Overview */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 lg:grid-cols-2 gap-6"
        >
          {/* Key Metrics */}
          <div className="bg-card border border-primary/20 rounded-2xl p-8 hover:border-primary/40 transition-all">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-2 text-foreground">
              <BarChart3 className="w-6 h-6 text-purple-400" />
              Key Metrics
            </h3>
            <div className="space-y-4">
              {[
                { label: 'Platform Activity', value: '98.5%', trend: '+2.3%' },
                { label: 'User Retention', value: '76.2%', trend: '+4.1%' },
                { label: 'Revenue Growth', value: '₦12.4M', trend: '+18.5%' },
                { label: 'Avg. Session Time', value: '12m 34s', trend: '+3.2m' },
              ].map((metric, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-4 rounded-lg bg-muted/50 border border-primary/10 hover:border-primary/30 transition-all"
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-foreground">{metric.label}</span>
                    <span className="text-sm font-bold text-green-400">{metric.trend}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-2xl font-bold text-primary">{metric.value}</span>
                    <div className="w-24 h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-blue-400 to-purple-500" style={{ width: '76%' }}></div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          {/* System Status */}
          <div className="bg-card border border-primary/20 rounded-2xl p-8 hover:border-primary/40 transition-all">
            <h3 className="text-2xl font-bold mb-6 flex items-center gap-2 text-foreground">
              <Shield className="w-6 h-6 text-green-400" />
              System Status
            </h3>
            <div className="space-y-4">
              {[
                { service: 'API Server', status: 'Operational', uptime: '99.99%' },
                { service: 'Database', status: 'Operational', uptime: '99.98%' },
                { service: 'Cache Layer', status: 'Operational', uptime: '99.95%' },
                { service: 'CDN', status: 'Operational', uptime: '99.99%' },
              ].map((service, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: 10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="p-4 rounded-lg bg-green-500/5 border border-green-500/30 hover:border-green-500/60 transition-all flex items-center justify-between"
                >
                  <div>
                    <p className="font-semibold text-foreground">{service.service}</p>
                    <p className="text-xs text-muted-foreground">Uptime: {service.uptime}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="w-3 h-3 rounded-full bg-green-500 animate-pulse"></span>
                    <span className="text-xs font-bold text-green-400">{service.status}</span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.section>

        {/* Quick Actions */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.25 }}
          className="bg-card border border-primary/20 rounded-2xl p-8 hover:border-primary/40 transition-all"
        >
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2 text-foreground">
            <ChevronRight className="w-6 h-6 text-yellow-400" />
            Quick Actions
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link href="/admin/users" className="group">
              <div className="p-6 rounded-xl bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 hover:border-blue-500/50 transition-all hover:shadow-lg hover:-translate-y-1 cursor-pointer">
                <Users className="w-8 h-8 text-blue-400 mb-3 group-hover:scale-110 transition-transform" />
                <p className="font-bold text-foreground mb-1">Manage Users</p>
                <p className="text-xs text-muted-foreground">View and manage user accounts</p>
              </div>
            </Link>

            <Link href="/dashboard/admin" className="group">
              <div className="p-6 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 hover:border-purple-500/50 transition-all hover:shadow-lg hover:-translate-y-1 cursor-pointer">
                <Music className="w-8 h-8 text-purple-400 mb-3 group-hover:scale-110 transition-transform" />
                <p className="font-bold text-foreground mb-1">Content Moderation</p>
                <p className="text-xs text-muted-foreground">Review and approve content</p>
              </div>
            </Link>

            <div className="group p-6 rounded-xl bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-500/20 hover:border-emerald-500/50 transition-all hover:shadow-lg hover:-translate-y-1 cursor-not-allowed opacity-50">
              <DollarSign className="w-8 h-8 text-emerald-400 mb-3 group-hover:scale-110 transition-transform" />
              <p className="font-bold text-foreground mb-1">Financial Reports</p>
              <p className="text-xs text-muted-foreground">Coming soon</p>
            </div>
          </div>
        </motion.section>

        {/* System Information */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-r from-primary/10 via-primary/5 to-primary/10 border border-primary/20 rounded-2xl p-8 text-foreground"
        >
          <h3 className="text-lg font-bold mb-4">System Information</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground text-xs mb-1">App Version</p>
              <p className="font-bold">v2.1.0</p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs mb-1">Last Update</p>
              <p className="font-bold">Sep 1, 2026</p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs mb-1">Server Status</p>
              <p className="font-bold text-green-400">Online</p>
            </div>
            <div>
              <p className="text-muted-foreground text-xs mb-1">Database</p>
              <p className="font-bold text-blue-400">Connected</p>
            </div>
          </div>
        </motion.section>
      </div>
    </div>
  );
}
