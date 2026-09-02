/**
 * UpgradePrompt - Modal prompting free users to upgrade when quota exceeded
 * Shows premium benefits and pricing
 */

'use client';

import React from 'react';
import type { UpgradePromptProps } from '../types';

export function UpgradePrompt({ isOpen, onClose, onUpgrade }: UpgradePromptProps) {
  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[60] flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="upgrade-prompt-title"
    >
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 space-y-6">
        {/* Header */}
        <div className="text-center">
          <div className="text-5xl mb-3">⚡</div>
          <h2 id="upgrade-prompt-title" className="text-2xl font-bold text-gray-900">
            You've Reached Your Daily Limit
          </h2>
          <p className="text-gray-600 mt-2">
            Upgrade to Premium for unlimited AI assistance
          </p>
        </div>

        {/* Benefits */}
        <div className="space-y-3">
          <div className="flex items-start gap-3 p-3 bg-purple-50 rounded-lg">
            <span className="text-2xl">🚀</span>
            <div>
              <h3 className="font-semibold text-gray-900">Unlimited AI Requests</h3>
              <p className="text-sm text-gray-600">No daily limits, generate as much as you need</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
            <span className="text-2xl">⚡</span>
            <div>
              <h3 className="font-semibold text-gray-900">Priority Processing</h3>
              <p className="text-sm text-gray-600">Faster responses with premium infrastructure</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
            <span className="text-2xl">🎯</span>
            <div>
              <h3 className="font-semibold text-gray-900">Advanced Features</h3>
              <p className="text-sm text-gray-600">Access to advanced AI models and features</p>
            </div>
          </div>

          <div className="flex items-start gap-3 p-3 bg-amber-50 rounded-lg">
            <span className="text-2xl">📊</span>
            <div>
              <h3 className="font-semibold text-gray-900">Premium Analytics</h3>
              <p className="text-sm text-gray-600">Detailed insights and performance tracking</p>
            </div>
          </div>
        </div>

        {/* Pricing */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl p-4 text-white text-center">
          <div className="text-sm opacity-90">Starting at</div>
          <div className="text-4xl font-bold my-1">$9.99</div>
          <div className="text-sm opacity-90">per month</div>
        </div>

        {/* Actions */}
        <div className="space-y-2">
          <button
            onClick={onUpgrade}
            className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-blue-600 text-white font-semibold rounded-lg hover:opacity-90 transition-opacity shadow-lg"
          >
            Upgrade Now
          </button>
          <button
            onClick={onClose}
            className="w-full px-6 py-2 text-gray-600 hover:text-gray-900 transition-colors"
          >
            Maybe Later
          </button>
        </div>

        {/* Fine print */}
        <p className="text-xs text-gray-500 text-center">
          Cancel anytime. No hidden fees.
        </p>

        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-lg hover:bg-gray-100 transition-colors"
          aria-label="Close"
        >
          <svg
            className="w-5 h-5 text-gray-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      </div>
    </div>
  );
}
