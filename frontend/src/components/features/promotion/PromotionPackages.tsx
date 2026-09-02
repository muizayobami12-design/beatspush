'use client';

import { Check, X, Zap } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export interface PromotionPackage {
  id: string;
  name: string;
  tier: 'free' | 'mini' | 'starter' | 'growth' | 'pro' | 'premium';
  price: number;
  currency: string;
  billing_period: string;
  description: string;
  features: {
    feature: string;
    included: boolean;
  }[];
  promotion_slots: number;
  featured_duration_days: number;
  social_media_reach: string;
  priority_support: boolean;
  custom_analytics: boolean;
  recommended?: boolean;
}

interface PromotionPackagesProps {
  packages: PromotionPackage[];
  onSelectPackage: (packageId: string) => void;
  selectedPackageId?: string;
  isLoading?: boolean;
}

export function PromotionPackages({
  packages,
  onSelectPackage,
  selectedPackageId,
  isLoading = false,
}: PromotionPackagesProps) {
  const tierColors = {
    free: 'border-gray-600 bg-gray-900/30',
    mini: 'border-blue-600/50 bg-blue-900/20',
    starter: 'border-cyan-600/50 bg-cyan-900/20',
    growth: 'border-purple-600/50 bg-purple-900/20',
    pro: 'border-pink-600/50 bg-pink-900/20',
    premium: 'border-yellow-600/50 bg-yellow-900/30',
  };

  const tierBadgeColors = {
    free: 'bg-gray-700 text-gray-100',
    mini: 'bg-blue-700 text-blue-100',
    starter: 'bg-cyan-700 text-cyan-100',
    growth: 'bg-purple-700 text-purple-100',
    pro: 'bg-pink-700 text-pink-100',
    premium: 'bg-yellow-700 text-yellow-100',
  };

  const tierHeaderColors = {
    free: 'text-gray-300',
    mini: 'text-blue-300',
    starter: 'text-cyan-300',
    growth: 'text-purple-300',
    pro: 'text-pink-300',
    premium: 'text-yellow-300',
  };

  return (
    <div className="space-y-6">
      {/* Packages Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {packages.map((pkg) => (
          <div
            key={pkg.id}
            className={cn(
              'relative rounded-lg border-2 p-6 transition-all duration-300',
              tierColors[pkg.tier],
              selectedPackageId === pkg.id && 'border-opacity-100 shadow-lg shadow-current',
              !selectedPackageId && 'hover:border-opacity-75'
            )}
          >
            {/* Recommended Badge */}
            {pkg.recommended && (
              <div className="absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2">
                <div className="flex items-center gap-1 px-3 py-1 rounded-full bg-gradient-to-r from-yellow-500 to-orange-500 text-white text-xs font-bold shadow-lg">
                  <Zap className="w-3 h-3" />
                  RECOMMENDED
                </div>
              </div>
            )}

            {/* Header */}
            <div className="mb-6 space-y-2">
              <div className="flex items-center justify-between">
                <h3 className={cn('text-2xl font-bold', tierHeaderColors[pkg.tier])}>
                  {pkg.name}
                </h3>
                <span className={cn(
                  'px-3 py-1 rounded-full text-xs font-bold',
                  tierBadgeColors[pkg.tier]
                )}>
                  {pkg.tier.toUpperCase()}
                </span>
              </div>
              <p className="text-sm text-gray-400">{pkg.description}</p>
            </div>

            {/* Pricing */}
            <div className="mb-6 space-y-1">
              <div className="flex items-baseline gap-1">
                <span className="text-4xl font-bold text-white">
                  {pkg.price === 0 ? 'Free' : pkg.price.toLocaleString()}
                </span>
                {pkg.price > 0 && (
                  <>
                    <span className="text-gray-400">{pkg.currency}</span>
                    <span className="text-sm text-gray-500">/{pkg.billing_period}</span>
                  </>
                )}
              </div>
              {pkg.price > 0 && (
                <p className="text-xs text-gray-500">
                  {pkg.price} {pkg.currency} billed {pkg.billing_period}
                </p>
              )}
            </div>

            {/* Key Metrics */}
            <div className="mb-6 space-y-3 pb-6 border-b border-gray-700">
              <div className="space-y-2 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Promotion Slots</span>
                  <span className="font-bold text-white">{pkg.promotion_slots}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Featured Duration</span>
                  <span className="font-bold text-white">{pkg.featured_duration_days} days</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-400">Social Reach</span>
                  <span className="font-bold text-white">{pkg.social_media_reach}</span>
                </div>
              </div>
            </div>

            {/* Features */}
            <div className="mb-6 space-y-3">
              <h4 className="text-sm font-bold text-white">Included Features</h4>
              <div className="space-y-2">
                {pkg.features.map((feature, idx) => (
                  <div
                    key={idx}
                    className="flex items-center gap-2 text-sm"
                  >
                    {feature.included ? (
                      <Check className="w-5 h-5 text-green-400 flex-shrink-0" />
                    ) : (
                      <X className="w-5 h-5 text-gray-600 flex-shrink-0" />
                    )}
                    <span className={feature.included ? 'text-gray-300' : 'text-gray-600'}>
                      {feature.feature}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Support & Analytics */}
            <div className="mb-6 space-y-2 pb-6 border-b border-gray-700">
              <div className="flex items-center gap-2 text-sm">
                {pkg.priority_support ? (
                  <Check className="w-5 h-5 text-green-400 flex-shrink-0" />
                ) : (
                  <X className="w-5 h-5 text-gray-600 flex-shrink-0" />
                )}
                <span className={pkg.priority_support ? 'text-gray-300' : 'text-gray-600'}>
                  Priority Support
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                {pkg.custom_analytics ? (
                  <Check className="w-5 h-5 text-green-400 flex-shrink-0" />
                ) : (
                  <X className="w-5 h-5 text-gray-600 flex-shrink-0" />
                )}
                <span className={pkg.custom_analytics ? 'text-gray-300' : 'text-gray-600'}>
                  Custom Analytics
                </span>
              </div>
            </div>

            {/* Button */}
            <Button
              onClick={() => onSelectPackage(pkg.id)}
              disabled={isLoading}
              variant={selectedPackageId === pkg.id ? 'default' : 'outline'}
              className={cn(
                'w-full',
                pkg.recommended && selectedPackageId !== pkg.id && 'bg-gradient-to-r from-yellow-600 to-orange-600 hover:from-yellow-700 hover:to-orange-700 text-white'
              )}
            >
              {selectedPackageId === pkg.id ? (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  Selected
                </>
              ) : (
                'Select Plan'
              )}
            </Button>
          </div>
        ))}
      </div>

      {/* Feature Comparison Table */}
      <div className="mt-12 space-y-4">
        <h3 className="text-2xl font-bold text-white">Feature Comparison</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-700">
                <th className="text-left py-3 px-4 font-semibold text-gray-300">Feature</th>
                {packages.map((pkg) => (
                  <th key={pkg.id} className="text-center py-3 px-4 font-semibold text-gray-300">
                    <div className="text-xs">{pkg.name}</div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              <tr>
                <td className="py-3 px-4 text-gray-300">Base Analytics</td>
                {packages.map((pkg) => (
                  <td key={pkg.id} className="text-center py-3 px-4">
                    <Check className="w-5 h-5 text-green-400 mx-auto" />
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">Advanced Analytics</td>
                {packages.map((pkg) => (
                  <td key={pkg.id} className="text-center py-3 px-4">
                    {pkg.custom_analytics ? (
                      <Check className="w-5 h-5 text-green-400 mx-auto" />
                    ) : (
                      <X className="w-5 h-5 text-gray-600 mx-auto" />
                    )}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">Priority Support</td>
                {packages.map((pkg) => (
                  <td key={pkg.id} className="text-center py-3 px-4">
                    {pkg.priority_support ? (
                      <Check className="w-5 h-5 text-green-400 mx-auto" />
                    ) : (
                      <X className="w-5 h-5 text-gray-600 mx-auto" />
                    )}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">Social Media Integration</td>
                {packages.map((pkg) => (
                  <td key={pkg.id} className="text-center py-3 px-4">
                    {pkg.tier !== 'free' ? (
                      <Check className="w-5 h-5 text-green-400 mx-auto" />
                    ) : (
                      <X className="w-5 h-5 text-gray-600 mx-auto" />
                    )}
                  </td>
                ))}
              </tr>
              <tr>
                <td className="py-3 px-4 text-gray-300">Free Tools Access</td>
                {packages.map((pkg) => (
                  <td key={pkg.id} className="text-center py-3 px-4">
                    <Check className="w-5 h-5 text-green-400 mx-auto" />
                  </td>
                ))}
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
