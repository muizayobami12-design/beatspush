'use client';

import { useState, useEffect } from 'react';
import { Menu, X, ArrowLeft, Share2, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';

// ============ MOBILE HEADER ============

interface MobileHeaderProps {
  title: string;
  showBack?: boolean;
  onBack?: () => void;
  actions?: React.ReactNode[];
  fixed?: boolean;
}

export function MobileHeader({
  title,
  showBack = false,
  onBack,
  actions = [],
  fixed = true
}: MobileHeaderProps) {
  return (
    <div
      className={`
        flex items-center justify-between gap-2 p-4 bg-card border-b border-border
        ${fixed ? 'sticky top-0 z-40' : ''}
      `}
    >
      <div className="flex items-center gap-2 flex-1">
        {showBack && (
          <Button
            variant="ghost"
            size="sm"
            className="p-0"
            onClick={onBack}
          >
            <ArrowLeft className="w-5 h-5" />
          </Button>
        )}
        <h1 className="text-lg font-bold text-white truncate">{title}</h1>
      </div>
      <div className="flex gap-2">
        {actions.slice(0, 2)}
        {actions.length > 2 && (
          <Button variant="ghost" size="sm" className="p-0">
            <MoreVertical className="w-5 h-5" />
          </Button>
        )}
      </div>
    </div>
  );
}

// ============ MOBILE BOTTOM SHEET ============

interface MobileBottomSheetProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  snapPoints?: number[];
}

export function MobileBottomSheet({
  isOpen,
  onClose,
  title,
  children,
  snapPoints = [0.5, 1]
}: MobileBottomSheetProps) {
  const [currentSnap, setCurrentSnap] = useState(0);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
      />
      <div className="absolute bottom-0 left-0 right-0 bg-card rounded-t-2xl border-t border-border">
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-4">
          <div className="w-10 h-1 bg-gray-600 rounded-full" />
        </div>

        {/* Header */}
        <div className="px-4 pb-4 border-b border-border">
          <h2 className="text-lg font-bold text-white">{title}</h2>
        </div>

        {/* Content */}
        <div className="px-4 py-4 overflow-y-auto max-h-[80vh]">
          {children}
        </div>
      </div>
    </div>
  );
}

// ============ MOBILE CARD ============

interface MobileCardProps {
  children: React.ReactNode;
  onClick?: () => void;
  interactive?: boolean;
}

export function MobileCard({
  children,
  onClick,
  interactive = false
}: MobileCardProps) {
  return (
    <div
      className={`
        bg-card rounded-lg border border-border p-4 mb-3
        ${interactive ? 'cursor-pointer active:opacity-70 transition-opacity' : ''}
      `}
      onClick={onClick}
    >
      {children}
    </div>
  );
}

// ============ MOBILE TABS ============

interface MobileTabsProps {
  tabs: Array<{ label: string; value: string }>;
  active: string;
  onChange: (value: string) => void;
}

export function MobileTabs({ tabs, active, onChange }: MobileTabsProps) {
  return (
    <div className="sticky top-0 z-30 bg-card border-b border-border overflow-x-auto">
      <div className="flex gap-1 p-1">
        {tabs.map((tab) => (
          <button
            key={tab.value}
            onClick={() => onChange(tab.value)}
            className={`
              px-4 py-2 rounded-lg whitespace-nowrap font-medium text-sm transition
              ${
                active === tab.value
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:text-white'
              }
            `}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}

// ============ MOBILE BUTTON GROUP ============

interface MobileButtonGroupProps {
  buttons: Array<{ label: string; onClick: () => void; variant?: 'primary' | 'secondary'; loading?: boolean }>;
  vertical?: boolean;
}

export function MobileButtonGroup({
  buttons,
  vertical = false
}: MobileButtonGroupProps) {
  return (
    <div
      className={`
        fixed bottom-0 left-0 right-0 bg-card border-t border-border p-4
        ${vertical ? 'flex flex-col gap-2' : 'grid grid-cols-2 gap-2'}
      `}
    >
      {buttons.map((btn, idx) => (
        <Button
          key={idx}
          onClick={btn.onClick}
          variant={btn.variant === 'primary' ? 'default' : 'outline'}
          className={btn.variant === 'primary' ? 'bg-purple-600 hover:bg-purple-700' : ''}
          disabled={btn.loading}
        >
          {btn.label}
        </Button>
      ))}
    </div>
  );
}

// ============ MOBILE DRAWER ============

interface MobileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  direction?: 'left' | 'right';
}

export function MobileDrawer({
  isOpen,
  onClose,
  children,
  direction = 'left'
}: MobileDrawerProps) {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = 'unset';
    }
    return () => {
      document.body.style.overflow = 'unset';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50">
      <div
        className="absolute inset-0 bg-black/40"
        onClick={onClose}
      />
      <div
        className={`
          absolute top-0 h-full w-64 bg-card border-r border-border
          transition-transform duration-300
          ${direction === 'left' ? 'left-0' : 'right-0'}
        `}
      >
        <div className="p-4 border-b border-border flex justify-between items-center">
          <h2 className="font-bold text-white">Menu</h2>
          <Button
            variant="ghost"
            size="sm"
            className="p-0"
            onClick={onClose}
          >
            <X className="w-5 h-5" />
          </Button>
        </div>
        <div className="p-4">
          {children}
        </div>
      </div>
    </div>
  );
}

// ============ MOBILE TOUCH GESTURES ============

interface TouchGestureProps {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onLongPress?: () => void;
  children: React.ReactNode;
}

export function TouchGestureHandler({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onLongPress,
  children
}: TouchGestureProps) {
  const [touchStart, setTouchStart] = useState<{ x: number; y: number; time: number } | null>(null);

  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchStart({
      x: e.touches[0].clientX,
      y: e.touches[0].clientY,
      time: Date.now()
    });
  };

  const handleTouchEnd = (e: React.TouchEvent) => {
    if (!touchStart) return;

    const touchEnd = {
      x: e.changedTouches[0].clientX,
      y: e.changedTouches[0].clientY,
      time: Date.now()
    };

    const deltaX = touchEnd.x - touchStart.x;
    const deltaY = touchEnd.y - touchStart.y;
    const deltaTime = touchEnd.time - touchStart.time;
    const minDistance = 50;
    const maxTime = 500;

    // Long press
    if (deltaTime > 500 && Math.abs(deltaX) < 20 && Math.abs(deltaY) < 20) {
      onLongPress?.();
      return;
    }

    // Swipe detection
    if (deltaTime < maxTime) {
      if (deltaX < -minDistance) onSwipeLeft?.();
      if (deltaX > minDistance) onSwipeRight?.();
      if (deltaY < -minDistance) onSwipeUp?.();
      if (deltaY > minDistance) onSwipeDown?.();
    }

    setTouchStart(null);
  };

  return (
    <div
      onTouchStart={handleTouchStart}
      onTouchEnd={handleTouchEnd}
      className="w-full"
    >
      {children}
    </div>
  );
}

// ============ RESPONSIVE IMAGE ============

interface ResponsiveImageProps {
  src: string;
  alt: string;
  aspectRatio?: 'square' | 'video' | 'portrait';
}

export function ResponsiveImage({
  src,
  alt,
  aspectRatio = 'square'
}: ResponsiveImageProps) {
  const aspectRatioClasses = {
    square: 'aspect-square',
    video: 'aspect-video',
    portrait: 'aspect-[3/4]'
  };

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      className={`w-full ${aspectRatioClasses[aspectRatio]} object-cover rounded-lg`}
    />
  );
}

// ============ MOBILE PAGINATION ============

interface MobilePaginationProps {
  currentPage: number;
  totalPages: number;
  onPageChange: (page: number) => void;
  loading?: boolean;
}

export function MobilePagination({
  currentPage,
  totalPages,
  onPageChange,
  loading
}: MobilePaginationProps) {
  return (
    <div className="flex justify-between items-center gap-2 p-4 border-t border-border">
      <Button
        variant="outline"
        onClick={() => onPageChange(currentPage - 1)}
        disabled={currentPage === 1 || loading}
        size="sm"
      >
        Previous
      </Button>
      <span className="text-sm text-gray-400">
        {currentPage} / {totalPages}
      </span>
      <Button
        variant="outline"
        onClick={() => onPageChange(currentPage + 1)}
        disabled={currentPage === totalPages || loading}
        size="sm"
      >
        Next
      </Button>
    </div>
  );
}

// ============ MOBILE SAFE AREA ============

interface MobileSafeAreaProps {
  children: React.ReactNode;
  bottom?: boolean;
}

export function MobileSafeArea({
  children,
  bottom = false
}: MobileSafeAreaProps) {
  return (
    <div
      className={`
        px-4
        ${bottom ? 'pb-24' : 'pt-4'}
        max-w-full
      `}
      style={{
        paddingBottom: bottom ? 'max(1rem, env(safe-area-inset-bottom))' : undefined,
        paddingTop: !bottom ? 'max(1rem, env(safe-area-inset-top))' : undefined
      }}
    >
      {children}
    </div>
  );
}
