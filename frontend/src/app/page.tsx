'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';

export default function HomePage() {
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    const handleScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="bg-background text-on-background antialiased selection:bg-secondary selection:text-on-secondary min-h-screen">
      {/* Navigation */}
      <nav
        className={`fixed top-0 w-full z-50 transition-all duration-300 ${
          scrollY > 50
            ? 'bg-surface-container-low/95 backdrop-blur-md'
            : 'bg-surface-container-low'
        } border-b border-outline-variant/15`}
      >
        <div className="flex justify-between items-center px-margin-desktop md:px-margin-desktop w-full max-w-container-max mx-auto h-16 max-md:px-margin-mobile">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-secondary text-[24px]">
              music_note
            </span>
            <span className="font-headline-md text-headline-md font-bold text-secondary tracking-tight">
              Amani
            </span>
          </div>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <a
              href="#discover"
              className="text-secondary font-bold border-b-2 border-secondary pb-1 text-label-sm font-label-sm tracking-wider uppercase transition-colors"
            >
              Discover
            </a>
            <a
              href="#royalties"
              className="text-on-surface-variant font-medium hover:text-secondary transition-colors duration-200 text-label-sm font-label-sm tracking-wider uppercase"
            >
              Royalties
            </a>
            <a
              href="#marketplace"
              className="text-on-surface-variant font-medium hover:text-secondary transition-colors duration-200 text-label-sm font-label-sm tracking-wider uppercase"
            >
              Marketplace
            </a>
          </div>

          {/* Right Actions */}
          <div className="flex items-center gap-4">
            <button className="text-on-surface-variant hover:text-secondary transition-colors active:opacity-80">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="text-on-surface-variant hover:text-secondary transition-colors active:opacity-80">
              <span className="material-symbols-outlined">settings</span>
            </button>
            <div className="h-8 w-8 rounded-full bg-surface-variant border border-outline-variant/30 overflow-hidden cursor-pointer hover:border-secondary transition-colors flex items-center justify-center">
              <span className="material-symbols-outlined text-on-surface-variant">
                account_circle
              </span>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <header className="relative w-full h-[90vh] min-h-[600px] flex items-center justify-center overflow-hidden">
        {/* Background Image with Overlay */}
        <div className="absolute inset-0 z-0">
          <div
            className="w-full h-full bg-cover bg-center opacity-60"
            style={{
              backgroundImage:
                'url(https://lh3.googleusercontent.com/aida-public/AB6AXuACkgNpDG-6As6eSaA0UTeW7OLfzyeVGpyq5tqQxyakH2h8zKC6GA1NRZWhRSUjJYu1AE-zMmSDhc18-606nmQIDK021wMWLUgwsAHJfkBXQFtrDO79jo6Wvrw5ih3Wi__pV84vUlLwQbwjTfk4j8t41tO3Tt-vykz2yhP56PMpE0f6987kxwaK9OGKNRKp2EGHFrMta4GVVwSJWkqBnb4yCgSNNUwyy9PNQo8dueoBpu47l41xbuEs)',
            }}
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background via-background/80 to-transparent"></div>
          <div className="absolute inset-0 bg-gradient-to-r from-background/90 via-background/40 to-transparent"></div>
        </div>

        {/* Hero Content */}
        <div className="relative z-10 w-full max-w-container-max mx-auto px-margin-desktop max-md:px-margin-mobile flex flex-col items-start gap-stack-md mt-16">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-surface-container-low border border-outline-variant/30 backdrop-blur-sm">
            <span className="w-2 h-2 rounded-full bg-secondary animate-pulse"></span>
            <span className="font-label-sm text-label-sm text-secondary uppercase tracking-widest">
              Global Ecosystem
            </span>
          </div>

          {/* Headline */}
          <h1 className="font-display-lg text-display-lg max-w-3xl text-on-background text-shadow-subtle max-md:font-headline-lg-mobile max-md:text-headline-lg-mobile">
            The Global Ecosystem for{' '}
            <span className="text-secondary italic font-serif">Pan-African</span> Creatives.
          </h1>

          {/* Subheadline */}
          <p className="font-body-lg text-body-lg text-on-surface-variant max-w-xl">
            Bridge the gap between traditional excellence and global financial sophistication. Manage royalties, secure bookings, and build your heritage.
          </p>

          {/* CTA Buttons */}
          <div className="flex items-center gap-4 mt-stack-sm pt-stack-sm border-t border-outline-variant/30">
            <Link
              href="/register"
              className="bg-secondary text-on-secondary-fixed font-label-sm text-label-sm px-6 py-3 rounded hover:bg-secondary-fixed transition-colors uppercase tracking-wider font-bold"
            >
              Join the Network
            </Link>
            <Link
              href="/dashboard"
              className="bg-transparent border border-[#8B5E3C] text-on-background font-label-sm text-label-sm px-6 py-3 rounded hover:bg-[#8B5E3C]/10 transition-colors uppercase tracking-wider"
            >
              Explore Platform
            </Link>
          </div>
        </div>
      </header>

      {/* Choose Your Path Section */}
      <section className="py-stack-lg bg-surface-container-lowest w-full relative">
        <div className="max-w-container-max mx-auto px-margin-desktop max-md:px-margin-mobile">
          {/* Section Header */}
          <div className="mb-stack-lg flex flex-col items-center text-center">
            <h2 className="font-headline-lg text-headline-lg text-on-background max-md:font-headline-md max-md:text-headline-md mb-2">
              Choose Your Path
            </h2>
            <div className="w-12 h-1 bg-secondary rounded-full"></div>
          </div>

          {/* Role Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter">
            {/* Artist Card */}
            <RoleCard
              title="Artist"
              description="Distribute music, track royalties, and connect with a global audience seamlessly."
              image="https://lh3.googleusercontent.com/aida-public/AB6AXuDiCZTnRQ4kQ2ooek1CTqBxK6ymo9Xp711P4Jp976xfbUYR4ZqHD4WMobiuNjKPtDjEp7Pcj4YphdsuNZT1-w5cfPYKe1Vo850H48Bw4IrFFdJVYoiIkeLCed7yI45-wqALkbRxnYF9wgiH5JgjppbuWbvhfmj-CcWcrTYzWG0KcG6XzxIhScOBDgVoklL2IiCTs2W9NQTvbBwLcJpCzYUj0VnIqtJBbsX8R7_hkGrE3FRYxes05Qy1"
              tags={['Distribution', 'Royalties']}
            />

            {/* Producer Card */}
            <RoleCard
              title="Producer"
              description="Sell beats, manage split sheets, and build your professional catalog."
              image="https://lh3.googleusercontent.com/aida-public/AB6AXuCRP5Qa6hBJaWd6GIjy5oDjnVXaDHUejN1hxbx7rm7NIF2RzKi9MhxGv-AWVN1xmvKpbYGPWNpXwJ_OF4HrWGVXTNjLXdmLrwqNRu4FIIFktGYbTNiyzGylFhTpgl2rh-dXN4rwRo-CVTt3gOvGMCzt4Ao2etllCGhZg_RGYaM76GLjRP2T3it55pb76AqEtQPXsmeiXpRiVq7STOsA_2GNazNGGTpacv_Elu1I26V8H8_91eCSYTPi"
              tags={['Marketplace', 'Splits']}
            />

            {/* DJ Card */}
            <RoleCard
              title="DJ"
              description="Curate exclusive sets, manage bookings, and monetize your live performances."
              image="https://lh3.googleusercontent.com/aida-public/AB6AXuBWLgHWd6RagBT3-SWVp45lE9p_iicbVbJxo_PkOLs7-pbPVrLkL-BIiIE3spwVHs3f0aye8eN1PISKuA3hWfUgd-ILDdP1ivYofa9GkzM9t9xC3fCXrMzLb8i20o4dCPz6N1KNTvd22avA9-LD1S6IsvXu9_8Ds4UN21cgsKq2qRCKXSvMsQ2Am9pf8kkDKQGXbd4z2kYKQh6p_QqImAgrOsr7Td7rs2gKQP_YsnlCDPdqPptmz3zQ"
              tags={['Bookings', 'Curation']}
            />

            {/* Fan Card */}
            <RoleCard
              title="Fan"
              description="Discover exclusive drops, invest in rising talent, and access VIP experiences."
              image="https://lh3.googleusercontent.com/aida-public/AB6AXuDJ5WCESovwIp9CA_BoDhTTso0rjb4FLLr3LVzBOCZRFWFwmPheCyNjE29nvT8JgS_3gMveNdUXk7X6Oh-QZyk9_NcV1dc24VDDr8EDMfxmTVrY3A6iz2PZYQW4MDF5MzalCQKtMFHC0Ntu1gLtK_F9GpLCErkmesCS0yrtv03kIvA05tsMtR3QZ-7qAHNCUNs_6HMRfLkpywXW4X3Zd12RJm3yfnoruObH0ctknEWl4nWWslBYIotj"
              tags={['Discovery', 'Investment']}
            />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-surface border-t border-outline-variant/15 pt-stack-lg pb-stack-md">
        <div className="max-w-container-max mx-auto px-margin-desktop max-md:px-margin-mobile">
          {/* Footer Content */}
          <div className="flex flex-col md:flex-row justify-between items-start gap-stack-md border-b border-outline-variant/15 pb-stack-md mb-stack-md">
            {/* Left: Branding & Description */}
            <div className="max-w-sm">
              <div className="flex items-center gap-2 mb-4">
                <span className="material-symbols-outlined text-secondary text-[20px]">
                  music_note
                </span>
                <span className="font-headline-md text-body-lg font-bold text-on-surface tracking-tight">
                  Amani
                </span>
              </div>
              <p className="font-body-md text-body-md text-on-surface-variant">
                The Modern Heritage standard for the global creative economy.
              </p>
            </div>

            {/* Footer Links */}
            <div className="grid grid-cols-2 gap-stack-lg">
              {/* Platform Links */}
              <div className="flex flex-col gap-2">
                <h4 className="font-label-sm text-label-sm text-secondary uppercase tracking-wider mb-2">
                  Platform
                </h4>
                <a className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors">
                  Discover
                </a>
                <a className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors">
                  Royalties
                </a>
                <a className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors">
                  Marketplace
                </a>
              </div>

              {/* Legal Links */}
              <div className="flex flex-col gap-2">
                <h4 className="font-label-sm text-label-sm text-secondary uppercase tracking-wider mb-2">
                  Legal
                </h4>
                <a className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors">
                  Terms of Service
                </a>
                <a className="font-body-md text-body-md text-on-surface-variant hover:text-on-surface transition-colors">
                  Privacy Policy
                </a>
              </div>
            </div>
          </div>

          {/* Bottom Footer */}
          <div className="flex justify-between items-center">
            <p className="font-body-md text-body-md text-on-surface-variant text-sm">
              © 2024 BeatsPush. All rights reserved.
            </p>
            <div className="flex gap-4">
              <button className="material-symbols-outlined text-on-surface-variant hover:text-secondary cursor-pointer transition-colors">
                language
              </button>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

/* Role Card Component */
function RoleCard({
  title,
  description,
  image,
  tags,
}: {
  title: string;
  description: string;
  image: string;
  tags: string[];
}) {
  return (
    <div className="group relative bg-surface-container ghost-border rounded-lg overflow-hidden transition-transform duration-300 hover:-translate-y-2 cursor-pointer flex flex-col h-[400px]">
      {/* Image Section */}
      <div className="h-1/2 w-full relative overflow-hidden">
        <img
          alt={`${title} Role`}
          src={image}
          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105 opacity-80 group-hover:opacity-100"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-surface-container to-transparent"></div>
      </div>

      {/* Content Section */}
      <div className="p-6 flex flex-col flex-grow justify-between relative z-10 bg-surface-container">
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-headline-md text-headline-md text-secondary">{title}</h3>
            <span className="material-symbols-outlined text-secondary opacity-0 group-hover:opacity-100 transition-opacity transform group-hover:translate-x-1 duration-300">
              arrow_forward
            </span>
          </div>
          <p className="font-body-md text-body-md text-on-surface-variant">
            {description}
          </p>
        </div>

        {/* Tags */}
        <div className="mt-4 flex gap-2">
          {tags.map((tag) => (
            <span
              key={tag}
              className="px-2 py-1 bg-[#8B5E3C] text-white text-[10px] rounded-full uppercase tracking-wider font-semibold"
            >
              {tag}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}
