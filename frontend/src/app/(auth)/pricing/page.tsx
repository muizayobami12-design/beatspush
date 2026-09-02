'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Check, Zap, Crown, Sparkles, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Logo from '@/components/brand/Logo';

const plans = [
  {
    name: 'Free',
    price: '₦0',
    period: '/forever',
    description: 'Perfect to get started',
    features: [
      'Upload 10 tracks/month',
      'Basic analytics',
      'Community support',
      '15% platform fee',
      'Standard profile',
      'Basic messaging',
    ],
    cta: 'Start Free',
    popular: false,
    gradient: 'from-gray-500 to-gray-700',
  },
  {
    name: 'Pro',
    price: '₦2,500',
    period: '/month',
    description: 'For serious creators',
    features: [
      'Unlimited uploads',
      'Advanced analytics',
      'Priority support',
      '12% platform fee',
      'Verified badge',
      'Advanced messaging',
      'Featured placements',
      'Custom profile themes',
    ],
    cta: 'Go Pro',
    popular: true,
    gradient: 'from-pink-500 via-purple-500 to-cyan-500',
  },
  {
    name: 'Elite',
    price: '₦10,000',
    period: '/month',
    description: 'Maximum visibility',
    features: [
      'Everything in Pro',
      'Premium analytics',
      'Dedicated manager',
      '10% platform fee',
      'Crown badge',
      'Homepage featured',
      'Exclusive events',
      'API access',
      'White-label options',
    ],
    cta: 'Get Elite',
    popular: false,
    gradient: 'from-orange-500 via-red-500 to-pink-600',
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-black text-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-lg bg-black/50 border-b border-white/10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Logo size="md" />
            
            <div className="flex items-center gap-4">
              <Link href="/">
                <Button variant="ghost" className="text-white hover:text-pink-400">
                  Home
                </Button>
              </Link>
              <Link href="/login">
                <Button variant="ghost" className="text-white hover:text-pink-400">
                  Login
                </Button>
              </Link>
              <Link href="/register">
                <Button className="bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 hover:opacity-90">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative pt-32 pb-20 px-4 overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-purple-900/20 via-black to-pink-900/20" />
          <motion.div
            className="absolute top-0 -left-20 w-96 h-96 bg-purple-500/30 rounded-full blur-3xl"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{ duration: 8, repeat: Infinity }}
          />
          <motion.div
            className="absolute bottom-0 -right-20 w-96 h-96 bg-pink-500/30 rounded-full blur-3xl"
            animate={{
              scale: [1.2, 1, 1.2],
              opacity: [0.3, 0.5, 0.3],
            }}
            transition={{ duration: 8, repeat: Infinity, delay: 1 }}
          />
        </div>

        <div className="container mx-auto relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-16"
          >
            <motion.div
              animate={{
                rotate: [0, 5, -5, 0],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
              }}
              className="inline-block mb-6"
            >
              <Sparkles className="h-16 w-16 text-yellow-400" />
            </motion.div>
            
            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight">
              <span className="bg-gradient-to-r from-pink-500 via-purple-500 to-cyan-500 bg-clip-text text-transparent">
                Simple Pricing.
              </span>
              <br />
              <span className="text-white">
                Maximum Value.
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-300 max-w-3xl mx-auto">
              Choose the plan that fits your goals. Upgrade or downgrade anytime.
              <span className="text-pink-400 font-semibold"> No hidden fees.</span>
            </p>
          </motion.div>

          {/* Pricing Cards */}
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto mb-16">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 50 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative"
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-10">
                    <div className="px-4 py-1 rounded-full bg-gradient-to-r from-pink-500 to-purple-600 text-white text-sm font-bold flex items-center gap-1">
                      <Crown className="h-4 w-4" />
                      Most Popular
                    </div>
                  </div>
                )}

                <div
                  className={`
                    relative h-full rounded-3xl overflow-hidden
                    ${plan.popular 
                      ? 'bg-white/10 border-2 border-purple-500 shadow-2xl shadow-purple-500/20 scale-105' 
                      : 'bg-white/5 border border-white/10'
                    }
                  `}
                >
                  {/* Gradient Overlay */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${plan.gradient} opacity-5`} />
                  
                  <div className="relative z-10 p-8">
                    {/* Plan Name */}
                    <div className="mb-6">
                      <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
                      <p className="text-gray-400 text-sm">{plan.description}</p>
                    </div>

                    {/* Price */}
                    <div className="mb-8">
                      <div className="flex items-end gap-2 mb-2">
                        <span className={`text-5xl font-black bg-gradient-to-r ${plan.gradient} bg-clip-text text-transparent`}>
                          {plan.price}
                        </span>
                        <span className="text-gray-400 pb-2">{plan.period}</span>
                      </div>
                    </div>

                    {/* Features */}
                    <ul className="space-y-4 mb-8">
                      {plan.features.map((feature, i) => (
                        <li key={i} className="flex items-start gap-3">
                          <div className={`p-1 rounded-full bg-gradient-to-br ${plan.gradient} flex-shrink-0`}>
                            <Check className="h-3 w-3 text-white" />
                          </div>
                          <span className="text-sm text-gray-300">{feature}</span>
                        </li>
                      ))}
                    </ul>

                    {/* CTA Button */}
                    <Link href="/register" className="block">
                      <Button
                        size="lg"
                        className={`
                          w-full
                          ${plan.popular
                            ? `bg-gradient-to-r ${plan.gradient} hover:opacity-90`
                            : 'bg-white/10 hover:bg-white/20 border border-white/20'
                          }
                        `}
                      >
                        {plan.cta}
                        <ArrowRight className="h-4 w-4 ml-2" />
                      </Button>
                    </Link>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          {/* Features Comparison */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="max-w-4xl mx-auto"
          >
            <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-3xl p-8">
              <h2 className="text-3xl font-bold mb-8 text-center">
                All Plans Include
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                {[
                  '🎵 Stream unlimited music',
                  '💰 Earn from tips & sales',
                  '📊 Real-time analytics',
                  '💬 Direct fan messaging',
                  '🔒 Secure payments',
                  '📱 Mobile app access',
                  '🌍 Global distribution',
                  '⚡ Instant payouts',
                ].map((feature, i) => (
                  <div key={i} className="flex items-center gap-3">
                    <Zap className="h-5 w-5 text-yellow-400" />
                    <span className="text-gray-300">{feature}</span>
                  </div>
                ))}
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 px-4 border-t border-white/10">
        <div className="container mx-auto max-w-3xl">
          <h2 className="text-4xl font-bold mb-12 text-center">
            Frequently Asked <span className="bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent">Questions</span>
          </h2>
          <div className="space-y-6">
            {[
              {
                q: 'Can I change my plan later?',
                a: 'Yes! Upgrade or downgrade anytime. Changes take effect immediately.',
              },
              {
                q: 'What payment methods do you accept?',
                a: 'We accept cards, bank transfers, and mobile money (Paystack integration).',
              },
              {
                q: 'Is there a free trial?',
                a: 'The Free plan is available forever. Upgrade when you\'re ready!',
              },
              {
                q: 'What happens if I cancel?',
                a: 'You keep access until the end of your billing period. No refunds for partial months.',
              },
            ].map((faq, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                viewport={{ once: true }}
                className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6"
              >
                <h3 className="text-lg font-bold mb-2">{faq.q}</h3>
                <p className="text-gray-400">{faq.a}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto max-w-4xl">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative rounded-3xl overflow-hidden"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-pink-600 via-purple-600 to-cyan-600" />
            <div className="relative z-10 py-16 px-8 text-center">
              <h2 className="text-4xl md:text-5xl font-black mb-4">
                Ready to Get Started?
              </h2>
              <p className="text-xl text-white/90 mb-8 max-w-2xl mx-auto">
                Join 50,000+ creators already earning on BeatPush. Start for free today!
              </p>
              <Link href="/register">
                <Button size="lg" className="bg-black hover:bg-gray-900 text-white text-lg px-10 py-6">
                  Create Free Account
                  <ArrowRight className="h-5 w-5 ml-2" />
                </Button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 px-4 border-t border-white/10">
        <div className="container mx-auto">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <Logo size="sm" />
            <div className="text-sm text-gray-400">
              © 2024 BeatPush. All rights reserved.
            </div>
            <div className="flex gap-6 text-sm text-gray-400">
              <Link href="/" className="hover:text-white transition-colors">Home</Link>
              <Link href="/roles" className="hover:text-white transition-colors">Roles</Link>
              <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
