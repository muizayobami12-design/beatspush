/**
 * Unit tests for QuotaResetNotification component
 * Tests notification display, auto-dismiss, and manual dismiss functionality
 */

import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QuotaResetNotification } from './QuotaResetNotification';

describe('QuotaResetNotification', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Rendering', () => {
    it('should render notification when visible is true', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      expect(screen.getByText('Your AI quota has been reset!')).toBeInTheDocument();
      expect(screen.getByText('You now have 20 AI requests available.')).toBeInTheDocument();
    });

    it('should not render when visible is false', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={false}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      expect(screen.queryByText('Your AI quota has been reset!')).not.toBeInTheDocument();
    });

    it('should render with custom reset amount', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={50}
        />
      );

      expect(screen.getByText('You now have 50 AI requests available.')).toBeInTheDocument();
    });

    it('should render with default reset amount when not provided', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
        />
      );

      expect(screen.getByText('You now have 20 AI requests available.')).toBeInTheDocument();
    });
  });

  describe('Auto-dismiss functionality', () => {
    it('should auto-dismiss after 5 seconds', async () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      expect(onDismiss).not.toHaveBeenCalled();

      // Fast-forward 5 seconds (for the dismiss timer)
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      // Fast-forward 300ms more (for the fade-out animation)
      act(() => {
        jest.advanceTimersByTime(300);
      });

      expect(onDismiss).toHaveBeenCalledTimes(1);
    });

    it('should add exit animation class before dismissing', () => {
      const onDismiss = jest.fn();
      const { container } = render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const notification = container.firstChild as HTMLElement;
      
      // Should start without exit animation
      expect(notification).toHaveClass('opacity-100');
      expect(notification).toHaveClass('translate-y-0');

      // Fast-forward to trigger exit animation
      act(() => {
        jest.advanceTimersByTime(5000);
      });

      // Should have exit animation classes
      expect(notification).toHaveClass('opacity-0');
      expect(notification).toHaveClass('translate-y-[-10px]');
    });
  });

  describe('Manual dismiss functionality', () => {
    it('should dismiss when close button is clicked', async () => {
      const onDismiss = jest.fn();
      const user = userEvent.setup({ delay: null });
      
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const dismissButton = screen.getByLabelText('Dismiss notification');
      await user.click(dismissButton);

      // Fast-forward animation duration
      act(() => {
        jest.advanceTimersByTime(300);
      });

      expect(onDismiss).toHaveBeenCalledTimes(1);
    });

    it('should add exit animation when manually dismissed', async () => {
      const onDismiss = jest.fn();
      const user = userEvent.setup({ delay: null });
      
      const { container } = render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const notification = container.firstChild as HTMLElement;
      const dismissButton = screen.getByLabelText('Dismiss notification');

      // Should start visible
      expect(notification).toHaveClass('opacity-100');

      await user.click(dismissButton);

      // Should have exit animation
      expect(notification).toHaveClass('opacity-0');
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const notification = screen.getByRole('status');
      expect(notification).toHaveAttribute('aria-live', 'polite');
    });

    it('should have accessible dismiss button', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const dismissButton = screen.getByLabelText('Dismiss notification');
      expect(dismissButton).toBeInTheDocument();
    });

    it('should have focus styles on dismiss button', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const dismissButton = screen.getByLabelText('Dismiss notification');
      expect(dismissButton).toHaveClass('focus:ring-2');
      expect(dismissButton).toHaveClass('focus:ring-green-500');
    });
  });

  describe('Timer cleanup', () => {
    it('should clear timer when component unmounts', () => {
      const onDismiss = jest.fn();
      const { unmount } = render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      unmount();

      // Fast-forward time after unmount
      act(() => {
        jest.advanceTimersByTime(10000);
      });

      // onDismiss should not be called after unmount
      expect(onDismiss).not.toHaveBeenCalled();
    });

    it('should reset exit state when visible changes from false to true', () => {
      const onDismiss = jest.fn();
      const { container, rerender } = render(
        <QuotaResetNotification
          visible={false}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      expect(container.firstChild).toBeNull();

      // Make visible
      rerender(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const notification = container.firstChild as HTMLElement;
      expect(notification).toHaveClass('opacity-100');
      expect(notification).toHaveClass('translate-y-0');
    });
  });

  describe('Visual styling', () => {
    it('should have success (green) color styling', () => {
      const onDismiss = jest.fn();
      const { container } = render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const notification = container.firstChild as HTMLElement;
      expect(notification).toHaveClass('bg-green-50');
      expect(notification).toHaveClass('border-green-200');
      expect(notification).toHaveClass('text-green-800');
    });

    it('should have smooth transition classes', () => {
      const onDismiss = jest.fn();
      const { container } = render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      const notification = container.firstChild as HTMLElement;
      expect(notification).toHaveClass('transition-all');
      expect(notification).toHaveClass('duration-300');
      expect(notification).toHaveClass('ease-in-out');
    });

    it('should render CheckCircle icon', () => {
      const onDismiss = jest.fn();
      render(
        <QuotaResetNotification
          visible={true}
          onDismiss={onDismiss}
          resetAmount={20}
        />
      );

      // Check for icon by its container class
      const icon = document.querySelector('.text-green-600');
      expect(icon).toBeInTheDocument();
    });
  });
});
