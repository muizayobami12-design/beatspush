'use client';

import { useState } from 'react';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { Music, Disc3, Mic2, Users, ArrowRight, Sparkles, Zap, TrendingUp, DollarSign, MessageCircle, Crown } from 'lucide-react';
import { Button } from '@/components/ui/button';

const roles = [
  {
    id: 'artist',
    title: 'Artist',
    icon: Mic2,
    tagline: 'Share Your Voice. Grow Your Fanbase.',
    description: 'Upload unlimited tracks, connect directly with fans, and monetize your music through tips, premium content, and direct sales.',
    gradient: 'from-pink-500 via-purple-500 to-indigo-600',
    features: [
      { icon: TrendingUp, text: 'Build your fanbase organically' },
      { icon: DollarSign, text: 'Earn through tips & premium tracks' },
      { icon: MessageCircle, text: 'Direct fan engagement' },
      { icon: Crown, text: 'Verified artist badge' },
    ],
    stats: [
      { value: '10K+', label: 'Active Artists' },
      { value: '₦2.5M', label: 'Monthly Earnings' },
      { value: '500K+', label: 'Fans Reached' },
    ],
    image: '🎤',
    color: 'pink',
  },
  {
    id: 'producer',
    title: 'Producer',
    icon: Music,
    tagline: 'Sell Beats. Build Your Empire.',
    description: 'List your beats with flexible licensing (lease or exclusive), reach artists worldwide, and earn 85% on every sale. Professional marketplace built for producers.',
    gradient: 'from-orange-500 via-red-500 to-pink-600',
    features: [
      { icon: Disc3, text: 'Sell beats with lease/exclusive licensing' },
      { icon: DollarSign, text: '85% revenue share (15% platform fee)' },
      { icon: TrendingUp, text: 'Featured beat placements' },
      { icon: Zap, text: 'Instant payment processing' },
    ],
    stats: [
      { value: '5K+', label: 'Producers' },
      { value: '₦5M', label: 'Monthly Sales' },
      { value: '20K+', label: 'Beats Sold' },
    ],
    image: '🎹',
    color: 'orange',
  },
  {
    id: 'dj',
    title: 'DJ',
    icon: Disc3,
    tagline: 'Spin Sets. Get Discovered. Earn.',
    description: 'Upload DJ mixes, receive track submissions from artists, get paid for playlist placements, and build your brand as a tastemaker.',
    gradient: 'from-cyan-500 via-blue-500 to-purple-600',
    features: [
      { icon: Disc3, text: 'Upload unlimited DJ mixes' },
      { icon: MessageCircle, text: 'Receive artist submissions' },
      { icon: DollarSign, text: 'Earn from submissions & tips' },
      { icon: Crown, text: 'Verified DJ status' },
    ],
    stats: [
      { value: '2K+', label: 'Active DJs' },
      { value: '₦1M', label: 'Submission Revenue' },
      { value: '50K+', label: 'Mix Streams' },
    ],
    image: '🎧',
    color: 'cyan',
  },
  {
    id: 'fan',
    title: 'Fan',
    icon: Users,
    tagline: 'Discover. Connect. Support.',
    description: 'Stream unlimited music, support your favorite artists with tips, get exclusive content, and be part of fan clubs. Your passion fuels creativity.',
    gradient: 'from-green-500 via-emerald-500 to-teal-600',
    features: [
      { icon: Music, text: 'Stream unlimited music' },
      { icon: MessageCircle, text: 'Direct artist messaging' },
      { icon: DollarSign, text: 'Tip artists you love' },
      { icon: Crown, text: 'Join exclusive fan clubs' },
    ],
    stats: [
      { value: '50K+', label: 'Active Fans' },
      { value: '₦10M', label: 'Tips Sent' },
      { value: '1M+', label: 'Monthly Streams' },
    ],
    image: '🎵',
    color: 'green',
  },
];

export default function RolesPage() {
  const [selectedRole, setSelectedRole] = useState<string | null>(null);
  const [hoveredRole, setHoveredRole] = useState<string | null>(null);

  const currentRole = roles.find(r => r.id === (selectedRole || hoveredRole));

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-950 text-white overflow-hidden">
      {/* Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-pink-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-2000"></div>
        <div className="absolute top-40 left-40 w-80 h-80 bg-cyan-500 rounded-full mix-blend-multiply filter blur-xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>

      {/* Header */}
      <div className="relative z-10 container mx-auto px-4 py-8">
        <Link href="/" className="inline-flex items-center gap-2 text-white/80 hover:text-white transition-colors">
          <ArrowRight className="h-4 w-4 rotate-180" />
          <span>Back to Home</span>
        </Link>
      </div>

      {/* Main Content */}
      <div className="relative z-10 container mx-auto px-4 py-12">
        {/* Hero Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center mb-16"
        >
          <motion.div
            animate={{
              scale: [1, 1.2, 1],
              rotate: [0, 5, -5, 0],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              repeatType: "reverse",
            }}
            className="inline-block mb-6"
          >
            <Sparkles className="h-16 w-16 text-yellow-400" />
          </motion.div>
          
          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-clip-text text-transparent bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500">
            Choose Your Path
          </h1>
          <p className="text-xl md:text-2xl text-white/70 max-w-3xl mx-auto">
            Join Nigeria's #1 music platform. Whether you create, spin, or just love music — BeatPush has your back.
          </p>
        </motion.div>

        {/* Role Cards Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {roles.map((role, index) => (
            <motion.div
              key={role.id}
              initial={{ opacity: 0, y: 50 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              onHoverStart={() => setHoveredRole(role.id)}
              onHoverEnd={() => setHoveredRole(null)}
              onClick={() => setSelectedRole(selectedRole === role.id ? null : role.id)}
              className="cursor-pointer"
            >
              <div className={`
                relative h-full rounded-2xl p-6 backdrop-blur-sm border border-white/10
                transition-all duration-300 overflow-hidden
                ${selectedRole === role.id || hoveredRole === role.id 
                  ? 'scale-105 shadow-2xl' 
                  : 'hover:scale-102'
                }
              `}>
                {/* Gradient Background */}
                <div className={`absolute inset-0 bg-gradient-to-br ${role.gradient} opacity-10`}></div>
                
                {/* Content */}
                <div className="relative z-10">
                  {/* Icon */}
                  <div className={`
                    w-16 h-16 rounded-xl bg-gradient-to-br ${role.gradient} 
                    flex items-center justify-center mb-4
                    transform transition-transform duration-300
                    ${hoveredRole === role.id ? 'rotate-12 scale-110' : ''}
                  `}>
                    <role.icon className="h-8 w-8 text-white" />
                  </div>

                  {/* Title & Emoji */}
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="text-2xl font-bold">{role.title}</h3>
                    <span className="text-3xl">{role.image}</span>
                  </div>

                  {/* Tagline */}
                  <p className={`text-sm font-semibold mb-3 bg-gradient-to-r ${role.gradient} bg-clip-text text-transparent`}>
                    {role.tagline}
                  </p>

                  {/* Description */}
                  <p className="text-sm text-white/60 mb-4 line-clamp-3">
                    {role.description}
                  </p>

                  {/* Stats */}
                  <div className="grid grid-cols-3 gap-2 mb-4">
                    {role.stats.map((stat, i) => (
                      <div key={i} className="text-center">
                        <div className="text-lg font-bold text-white">{stat.value}</div>
                        <div className="text-xs text-white/50">{stat.label}</div>
                      </div>
                    ))}
                  </div>

                  {/* View Details Button */}
                  <Button
                    className={`w-full bg-gradient-to-r ${role.gradient} hover:opacity-90 transition-opacity`}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedRole(role.id);
                    }}
                  >
                    Learn More
                    <ArrowRight className="h-4 w-4 ml-2" />
                  </Button>
                </div>

                {/* Animated Glow Effect */}
                {(hoveredRole === role.id || selectedRole === role.id) && (
                  <motion.div
                    className={`absolute inset-0 bg-gradient-to-br ${role.gradient} opacity-20 blur-xl`}
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.2, 0.3, 0.2],
                    }}
                    transition={{
                      duration: 2,
                      repeat: Infinity,
                    }}
                  />
                )}
              </div>
            </motion.div>
          ))}
        </div>

        {/* Detailed View */}
        <AnimatePresence>
          {selectedRole && currentRole && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-16"
            >
              <div className={`
                rounded-3xl p-8 md:p-12 backdrop-blur-md border border-white/10
                bg-gradient-to-br ${currentRole.gradient} bg-opacity-10
              `}>
                <div className="grid md:grid-cols-2 gap-12 items-center">
                  {/* Left: Features */}
                  <div>
                    <div className="flex items-center gap-4 mb-6">
                      <div className={`w-20 h-20 rounded-2xl bg-gradient-to-br ${currentRole.gradient} flex items-center justify-center`}>
                        <currentRole.icon className="h-10 w-10 text-white" />
                      </div>
                      <div>
                        <h2 className="text-4xl font-bold">{currentRole.title}</h2>
                        <p className="text-xl text-white/70">{currentRole.tagline}</p>
                      </div>
                    </div>

                    <p className="text-lg text-white/80 mb-8">
                      {currentRole.description}
                    </p>

                    <div className="space-y-4 mb-8">
                      {currentRole.features.map((feature, i) => (
                        <motion.div
                          key={i}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: i * 0.1 }}
                          className="flex items-start gap-3"
                        >
                          <div className={`p-2 rounded-lg bg-gradient-to-br ${currentRole.gradient} bg-opacity-20`}>
                            <feature.icon className="h-5 w-5" />
                          </div>
                          <span className="text-white/90">{feature.text}</span>
                        </motion.div>
                      ))}
                    </div>

                    <div className="flex gap-4">
                      <Link href="/register" className="flex-1">
                        <Button size="lg" className={`w-full bg-gradient-to-r ${currentRole.gradient} hover:opacity-90`}>
                          Get Started as {currentRole.title}
                          <ArrowRight className="h-5 w-5 ml-2" />
                        </Button>
                      </Link>
                    </div>
                  </div>

                  {/* Right: Stats & Visual */}
                  <div className="space-y-6">
                    {/* Large Stats */}
                    {currentRole.stats.map((stat, i) => (
                      <motion.div
                        key={i}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ delay: i * 0.1 }}
                        className="p-6 rounded-2xl backdrop-blur-sm bg-white/5 border border-white/10"
                      >
                        <div className="text-4xl font-bold mb-2 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
                          {stat.value}
                        </div>
                        <div className="text-white/60">{stat.label}</div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* CTA Section */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-center"
        >
          <div className="inline-flex items-center gap-2 text-white/60 mb-4">
            <Zap className="h-5 w-5 text-yellow-400" />
            <span>Join thousands of creators earning on BeatPush</span>
          </div>
          <div className="flex flex-wrap justify-center gap-4">
            <Link href="/register">
              <Button size="lg" className="bg-gradient-to-r from-pink-500 to-purple-600 hover:opacity-90">
                Sign Up Now
              </Button>
            </Link>
            <Link href="/login">
              <Button size="lg" variant="outline" className="border-white/20 hover:bg-white/10">
                Already Have Account?
              </Button>
            </Link>
          </div>
        </motion.div>
      </div>

      {/* Custom Animations */}
      <style jsx global>{`
        @keyframes blob {
          0%, 100% { transform: translate(0, 0) scale(1); }
          25% { transform: translate(20px, -50px) scale(1.1); }
          50% { transform: translate(-20px, 20px) scale(0.9); }
          75% { transform: translate(50px, 50px) scale(1.05); }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
}
