import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { SearchAutocomplete } from './search-autocomplete';

describe('SearchAutocomplete', () => {
  // Test 1: Renders input field
  it('should render search input field', () => {
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i);
    expect(input).toBeInTheDocument();
  });

  // Test 2: Shows suggestions on input
  it('should display suggestions on input change', async () => {
    const user = userEvent.setup();
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'midnight');
    await waitFor(() => {
      expect(screen.getByText('Midnight Voyage')).toBeInTheDocument();
    });
  });

  // Test 3: Filters suggestions by query
  it('should filter suggestions based on query', async () => {
    const user = userEvent.setup();
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'lagos');
    await waitFor(() => {
      expect(screen.getByText('Lagos Nights')).toBeInTheDocument();
      expect(screen.queryByText('Midnight Voyage')).not.toBeInTheDocument();
    });
  });

  // Test 4: Groups suggestions by category
  it('should group suggestions by category', async () => {
    const user = userEvent.setup();
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'a');
    await waitFor(() => {
      const categoryHeaders = screen.queryAllByText(/beats|artists|playlists|sounds/i);
      expect(categoryHeaders.length).toBeGreaterThan(0);
    });
  });

  // Test 5: Arrow key navigation
  it('should navigate suggestions with arrow keys', async () => {
    const user = userEvent.setup();
    const onSuggestionSelect = jest.fn();
    render(<SearchAutocomplete onSuggestionSelect={onSuggestionSelect} />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'a');
    await waitFor(() => {
      expect(screen.getByText('Midnight Voyage')).toBeInTheDocument();
    });

    await user.keyboard('{ArrowDown}{ArrowDown}{Enter}');
    await waitFor(() => {
      expect(onSuggestionSelect).toHaveBeenCalled();
    });
  });

  // Test 6: Escapes dropdown on Escape key
  it('should close dropdown on Escape key', async () => {
    const user = userEvent.setup();
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'midnight');
    await user.keyboard('{Escape}');

    await waitFor(() => {
      expect(screen.queryByText('Midnight Voyage')).not.toBeInTheDocument();
    });
  });

  // Test 7: Selects suggestion on click
  it('should select suggestion on click', async () => {
    const user = userEvent.setup();
    const onSuggestionSelect = jest.fn();
    render(<SearchAutocomplete onSuggestionSelect={onSuggestionSelect} />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'midnight');
    await waitFor(() => {
      expect(screen.getByText('Midnight Voyage')).toBeInTheDocument();
    });

    const suggestion = screen.getByText('Midnight Voyage').closest('button');
    if (suggestion) {
      await user.click(suggestion);
    }

    expect(onSuggestionSelect).toHaveBeenCalled();
  });

  // Test 8: Clear button removes query
  it('should clear query when clear button clicked', async () => {
    const user = userEvent.setup();
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i) as HTMLInputElement;

    await user.type(input, 'test');
    expect(input.value).toBe('test');

    const clearButton = screen.getByLabelText('Clear search');
    await user.click(clearButton);

    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });

  // Test 9: Stores recent searches in localStorage
  it('should store recent searches in localStorage', async () => {
    const user = userEvent.setup();
    const mockLocalStorage = {
      getItem: jest.fn(() => null),
      setItem: jest.fn(),
      removeItem: jest.fn(),
      clear: jest.fn(),
      length: 0,
      key: jest.fn(),
    };
    Object.defineProperty(window, 'localStorage', { value: mockLocalStorage });

    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'test query');
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(mockLocalStorage.setItem).toHaveBeenCalled();
    });
  });

  // Test 10: Calls onSearch callback on form submit
  it('should call onSearch callback on form submission', async () => {
    const user = userEvent.setup();
    const onSearch = jest.fn();
    render(<SearchAutocomplete onSearch={onSearch} />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'test');
    await user.keyboard('{Enter}');

    await waitFor(() => {
      expect(onSearch).toHaveBeenCalledWith('test');
    });
  });

  // Test 11: Debounces suggestions request
  it('should debounce suggestions request', async () => {
    const user = userEvent.setup({ delay: null });
    const getSuggestions = jest.fn().mockResolvedValue([]);
    render(<SearchAutocomplete getSuggestions={getSuggestions} />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'test');

    // Should not call immediately due to debounce
    expect(getSuggestions).not.toHaveBeenCalled();

    // Wait for debounce to complete
    await waitFor(
      () => {
        expect(getSuggestions).toHaveBeenCalled();
      },
      { timeout: 500 }
    );
  });

  // Test 12: Highlights matching text in suggestions
  it('should highlight matching text in suggestions', async () => {
    const user = userEvent.setup();
    render(<SearchAutocomplete />);
    const input = screen.getByPlaceholderText(/search beats/i);

    await user.type(input, 'night');
    await waitFor(() => {
      const mark = screen.queryByText('night', { selector: 'mark' });
      expect(mark).toBeInTheDocument();
    });
  });
});
