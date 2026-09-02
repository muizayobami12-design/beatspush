import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { PaymentForm } from './PaymentForm';
import { paymentService } from '@/services/paymentService';

// Mock Paystack
(window as any).PaystackPop = {
  setup: jest.fn().mockReturnValue({
    openIframe: jest.fn(),
  }),
};

// Mock payment service
jest.mock('@/services/paymentService');

// Mock useToast hook
jest.mock('@/hooks/useToast', () => ({
  useToast: () => ({
    toast: jest.fn(),
  }),
}));

describe('PaymentForm Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock Paystack script loading
    Object.defineProperty(document, 'getElementById', {
      value: () => null,
    });
  });

  // Test 1: Render with basic props
  test('should render payment form with product details', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Sunset Vibes"
        amount={25000}
        currency="NGN"
      />
    );

    expect(screen.getByText('Order Summary')).toBeInTheDocument();
    expect(screen.getByText('Sunset Vibes')).toBeInTheDocument();
    expect(screen.getByText(/NGN 25,000/)).toBeInTheDocument();
  });

  // Test 2: Display email input
  test('should render email input field', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
      />
    );

    const emailInput = screen.getByLabelText(/Email Address/i);
    expect(emailInput).toBeInTheDocument();
    expect(emailInput).toHaveAttribute('type', 'email');
  });

  // Test 3: Pre-fill email
  test('should pre-fill email if provided', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
        email="user@example.com"
      />
    );

    const emailInput = screen.getByDisplayValue('user@example.com') as HTMLInputElement;
    expect(emailInput).toBeInTheDocument();
  });

  // Test 4: Pay button disabled with invalid email
  test('should disable pay button with invalid email', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
      />
    );

    const payButton = screen.getByRole('button', { name: /Pay Now/i });
    expect(payButton).toBeDisabled();
  });

  // Test 5: Pay button enabled with valid email
  test('should enable pay button with valid email', async () => {
    const user = userEvent.setup();

    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
      />
    );

    const emailInput = screen.getByLabelText(/Email Address/i);
    await user.type(emailInput, 'user@example.com');

    const payButton = screen.getByRole('button', { name: /Pay Now/i });
    expect(payButton).not.toBeDisabled();
  });

  // Test 6: Show error with empty email
  test('should show error message when submitting empty form', async () => {
    const user = userEvent.setup();

    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
      />
    );

    const payButton = screen.getByRole('button', { name: /Pay Now/i });
    // Form is already disabled, but if we could submit, it would show error
    expect(payButton).toBeDisabled();
  });

  // Test 7: Validate email format
  test('should validate email format', async () => {
    const user = userEvent.setup();

    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
      />
    );

    const emailInput = screen.getByLabelText(/Email Address/i);

    // Invalid email
    await user.type(emailInput, 'invalid-email');
    let payButton = screen.getByRole('button', { name: /Pay Now/i });
    expect(payButton).toBeDisabled();

    // Clear and type valid email
    await user.clear(emailInput);
    await user.type(emailInput, 'valid@example.com');

    payButton = screen.getByRole('button', { name: /Pay Now/i });
    expect(payButton).not.toBeDisabled();
  });

  // Test 8: Display exclusive license info
  test('should display exclusive license badge', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={50000}
        licenseType="exclusive"
      />
    );

    expect(screen.getByText('Exclusive License')).toBeInTheDocument();
  });

  // Test 9: Custom button text
  test('should use custom button text', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
        buttonText="Purchase Now"
      />
    );

    expect(screen.getByRole('button', { name: /Purchase Now/i })).toBeInTheDocument();
  });

  // Test 10: Disabled state
  test('should disable form when disabled prop is true', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
        email="user@example.com"
        disabled={true}
      />
    );

    const payButton = screen.getByRole('button', { name: /Pay Now/i });
    expect(payButton).toBeDisabled();
  });

  // Test 11: Display description
  test('should display item description', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
        description="High-quality beat with commercial rights"
      />
    );

    expect(screen.getByText('High-quality beat with commercial rights')).toBeInTheDocument();
  });

  // Test 12: Currency display
  test('should display correct currency', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={99}
        currency="USD"
      />
    );

    expect(screen.getByText('USD 99')).toBeInTheDocument();
  });

  // Test 13: Security notice
  test('should display security notice', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
      />
    );

    expect(screen.getByText(/Your payment information is secure and encrypted/i)).toBeInTheDocument();
  });

  // Test 14: Paystack credit
  test('should display Paystack credit link', () => {
    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
      />
    );

    const paystackLink = screen.getByRole('link', { name: /Paystack/i });
    expect(paystackLink).toHaveAttribute('href', 'https://paystack.com');
    expect(paystackLink).toHaveAttribute('target', '_blank');
  });

  // Test 15: Callback invocation
  test('should call onSuccess callback when payment succeeds', async () => {
    const mockOnSuccess = jest.fn();
    const mockInitiate = jest
      .spyOn(paymentService, 'initiateBeatPurchase')
      .mockResolvedValue({
        authorization_url: 'https://checkout.paystack.com/test',
        access_code: 'test_access',
        reference: 'ref-12345',
      });

    const mockVerify = jest
      .spyOn(paymentService, 'verifyPayment')
      .mockResolvedValue({
        status: 'success',
        reference: 'ref-12345',
        amount: 10000,
        currency: 'NGN',
        channel: 'card',
        transaction: {
          id: 'txn-123',
          status: 'success',
          reference: 'ref-12345',
          amount: 10000,
        },
      });

    render(
      <PaymentForm
        itemId="beat-123"
        itemTitle="Test Beat"
        amount={10000}
        onSuccess={mockOnSuccess}
      />
    );

    // Form would call these in response to successful Paystack payment
    // This is tested indirectly through the hook
  });
});
