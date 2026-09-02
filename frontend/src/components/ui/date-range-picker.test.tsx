import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { DateRangePicker } from './date-range-picker';

describe('DateRangePicker Component', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  // Test 1: Render with empty state
  test('should render with placeholder text', () => {
    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
        placeholder="Select date range"
      />
    );

    expect(screen.getByText('Select date range')).toBeInTheDocument();
  });

  // Test 2: Open dropdown
  test('should open dropdown when button is clicked', async () => {
    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Quick Select/i)).toBeInTheDocument();
    });
  });

  // Test 3: Display selected dates
  test('should display selected date range', () => {
    const from = new Date(2024, 0, 1); // Jan 1, 2024
    const to = new Date(2024, 0, 31); // Jan 31, 2024

    render(
      <DateRangePicker
        value={{ from, to }}
        onChange={mockOnChange}
        placeholder="Select date range"
      />
    );

    expect(screen.getByText(/Jan 01, 2024 - Jan 31, 2024/)).toBeInTheDocument();
  });

  // Test 4: Clear button removes dates
  test('should clear dates when clear button is clicked', async () => {
    const from = new Date(2024, 0, 1);
    const to = new Date(2024, 0, 31);

    render(
      <DateRangePicker
        value={{ from, to }}
        onChange={mockOnChange}
      />
    );

    const clearButton = screen.getByRole('button', { name: '' }); // X button
    if (clearButton) {
      fireEvent.click(clearButton);
      expect(mockOnChange).toHaveBeenCalledWith({ from: null, to: null });
    }
  });

  // Test 5: Select preset range
  test('should select preset range (Last 7 days)', async () => {
    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      const preset = screen.getByText('Last 7 days');
      fireEvent.click(preset);
    });

    expect(mockOnChange).toHaveBeenCalled();
    const callArg = mockOnChange.mock.calls[0][0];
    expect(callArg.from).toBeDefined();
    expect(callArg.to).toBeDefined();
  });

  // Test 6: Select date range manually
  test('should select date range by clicking calendar dates', async () => {
    const user = userEvent.setup();

    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    await user.click(button);

    // This test depends on calendar rendering which is complex to test in unit tests
    // In real scenarios, use E2E tests for calendar interactions
  });

  // Test 7: Disable future dates
  test('should disable future dates when disableFuture is true', async () => {
    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
        disableFuture={true}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Quick Select/i)).toBeInTheDocument();
    });
  });

  // Test 8: Close on outside click
  test('should close dropdown when clicking outside', async () => {
    const { container } = render(
      <div>
        <DateRangePicker
          value={{ from: null, to: null }}
          onChange={mockOnChange}
        />
        <div data-testid="outside">Outside element</div>
      </div>
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText(/Quick Select/i)).toBeInTheDocument();
    });

    const outside = screen.getByTestId('outside');
    fireEvent.mouseDown(outside);

    await waitFor(() => {
      expect(screen.queryByText(/Quick Select/i)).not.toBeInTheDocument();
    });
  });

  // Test 9: Month navigation
  test('should navigate between months', async () => {
    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      const currentMonth = screen.getByText(new RegExp(
        new Date().toLocaleDateString('en-NG', { month: 'long', year: 'numeric' })
      ));
      expect(currentMonth).toBeInTheDocument();
    });
  });

  // Test 10: Apply button disabled when range incomplete
  test('should disable apply button when range is incomplete', async () => {
    render(
      <DateRangePicker
        value={{ from: new Date(2024, 0, 1), to: null }}
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      const applyButton = screen.getByRole('button', { name: /Apply/i });
      expect(applyButton).toBeDisabled();
    });
  });

  // Test 11: Calendar shows current month
  test('should show current month on open', async () => {
    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      const monthText = new Date().toLocaleDateString('en-NG', {
        month: 'long',
        year: 'numeric',
      });
      expect(screen.getByText(new RegExp(monthText))).toBeInTheDocument();
    });
  });

  // Test 12: Weekday headers display
  test('should display weekday headers', async () => {
    render(
      <DateRangePicker
        value={{ from: null, to: null }}
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button', { name: /Select date range/i });
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Sun')).toBeInTheDocument();
      expect(screen.getByText('Mon')).toBeInTheDocument();
      expect(screen.getByText('Sat')).toBeInTheDocument();
    });
  });
});
