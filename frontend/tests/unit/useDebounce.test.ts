import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useDebounce } from '@/hooks/useDebounce';

describe('useDebounce', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('should return initial value immediately', () => {
    const { result } = renderHook(() => useDebounce('initial', 500));
    expect(result.current).toBe('initial');
  });

  it('should debounce value changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 },
      }
    );

    expect(result.current).toBe('initial');

    // Update value
    rerender({ value: 'updated', delay: 500 });
    
    // Value should not change immediately
    expect(result.current).toBe('initial');

    // Fast-forward time by 250ms (half delay)
    act(() => {
      vi.advanceTimersByTime(250);
    });
    
    // Still should not have changed
    expect(result.current).toBe('initial');

    // Fast-forward remaining time
    act(() => {
      vi.advanceTimersByTime(250);
    });
    
    // Now it should have updated
    expect(result.current).toBe('updated');
  });

  it('should cancel previous timeout on rapid changes', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 },
      }
    );

    // Rapid updates
    rerender({ value: 'change1', delay: 500 });
    act(() => vi.advanceTimersByTime(200));
    
    rerender({ value: 'change2', delay: 500 });
    act(() => vi.advanceTimersByTime(200));
    
    rerender({ value: 'change3', delay: 500 });
    act(() => vi.advanceTimersByTime(200));

    // Value should still be initial
    expect(result.current).toBe('initial');

    // Fast-forward enough time after last change
    act(() => {
      vi.advanceTimersByTime(300);
    });

    // Should be the last value only
    expect(result.current).toBe('change3');
  });

  it('should work with different delay values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 1000 },
      }
    );

    rerender({ value: 'updated', delay: 1000 });

    act(() => {
      vi.advanceTimersByTime(999);
    });
    expect(result.current).toBe('initial');

    act(() => {
      vi.advanceTimersByTime(1);
    });
    expect(result.current).toBe('updated');
  });

  it('should handle number values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 0, delay: 300 },
      }
    );

    expect(result.current).toBe(0);

    rerender({ value: 42, delay: 300 });

    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(result.current).toBe(42);
  });

  it('should handle object values', () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: { name: 'initial' }, delay: 300 },
      }
    );

    expect(result.current).toEqual({ name: 'initial' });

    rerender({ value: { name: 'updated' }, delay: 300 });

    act(() => {
      vi.advanceTimersByTime(300);
    });

    expect(result.current).toEqual({ name: 'updated' });
  });

  it('should cleanup timeout on unmount', () => {
    const { unmount, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      {
        initialProps: { value: 'initial', delay: 500 },
      }
    );

    rerender({ value: 'updated', delay: 500 });

    // Unmount before timeout completes
    unmount();

    // Advance timers - should not throw error
    act(() => {
      vi.advanceTimersByTime(500);
    });

    // Test passes if no errors thrown
    expect(true).toBe(true);
  });
});
