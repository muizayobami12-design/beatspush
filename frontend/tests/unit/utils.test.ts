import { describe, it, expect } from 'vitest';
import {
  cn,
  formatCurrency,
  formatDuration,
  truncate,
  formatCompactNumber,
  isValidEmail,
  getInitials,
} from '@/lib/utils';

describe('Utils', () => {
  describe('cn', () => {
    it('should merge class names correctly', () => {
      expect(cn('foo', 'bar')).toBe('foo bar');
      expect(cn('foo', { bar: true })).toBe('foo bar');
      expect(cn('foo', { bar: false })).toBe('foo');
    });
  });

  describe('formatCurrency', () => {
    it('should format currency correctly', () => {
      expect(formatCurrency(100)).toBe('$100.00');
      expect(formatCurrency(1234.56)).toBe('$1,234.56');
    });
  });

  describe('formatDuration', () => {
    it('should format duration in MM:SS', () => {
      expect(formatDuration(0)).toBe('0:00');
      expect(formatDuration(65)).toBe('1:05');
      expect(formatDuration(125)).toBe('2:05');
      expect(formatDuration(3661)).toBe('61:01');
    });
  });

  describe('truncate', () => {
    it('should truncate text correctly', () => {
      expect(truncate('Hello World', 5)).toBe('Hello...');
      expect(truncate('Hello', 10)).toBe('Hello');
    });
  });

  describe('formatCompactNumber', () => {
    it('should format numbers compactly', () => {
      expect(formatCompactNumber(1000)).toBe('1K');
      expect(formatCompactNumber(1500)).toBe('1.5K');
      expect(formatCompactNumber(1000000)).toBe('1M');
    });
  });

  describe('isValidEmail', () => {
    it('should validate email correctly', () => {
      expect(isValidEmail('test@example.com')).toBe(true);
      expect(isValidEmail('invalid')).toBe(false);
      expect(isValidEmail('test@')).toBe(false);
    });
  });

  describe('getInitials', () => {
    it('should get initials from name', () => {
      expect(getInitials('John Doe')).toBe('JD');
      expect(getInitials('Jane')).toBe('J');
      expect(getInitials('Mary Jane Watson')).toBe('MJ');
    });
  });
});
