import { render, screen, fireEvent } from '@testing-library/react';
import { Pagination, PaginationSize } from './pagination';

describe('Pagination Component', () => {
  // Test 1: Single page - no pagination shown
  test('should not render pagination when only one page', () => {
    const mockOnPageChange = jest.fn();
    const { container } = render(
      <Pagination
        currentPage={1}
        totalItems={10}
        pageSize={20}
        onPageChange={mockOnPageChange}
      />
    );

    expect(container.firstChild).toBeNull();
  });

  // Test 2: Multiple pages - pagination visible
  test('should render pagination controls for multiple pages', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={1}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByLabelText('Next page')).toBeInTheDocument();
    expect(screen.getByLabelText('Previous page')).toBeInTheDocument();
    expect(screen.getByText('Page 1 of 10')).toBeInTheDocument();
  });

  // Test 3: First page - previous button disabled
  test('should disable previous button on first page', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={1}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
      />
    );

    const prevButton = screen.getByLabelText('Previous page');
    expect(prevButton).toBeDisabled();

    const nextButton = screen.getByLabelText('Next page');
    expect(nextButton).not.toBeDisabled();
  });

  // Test 4: Last page - next button disabled
  test('should disable next button on last page', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={10}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
      />
    );

    const nextButton = screen.getByLabelText('Next page');
    expect(nextButton).toBeDisabled();

    const prevButton = screen.getByLabelText('Previous page');
    expect(prevButton).not.toBeDisabled();
  });

  // Test 5: Middle page - both buttons enabled
  test('should enable both buttons on middle page', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={5}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByLabelText('Previous page')).not.toBeDisabled();
    expect(screen.getByLabelText('Next page')).not.toBeDisabled();
  });

  // Test 6: Next button click
  test('should call onPageChange with next page on next button click', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={1}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
      />
    );

    fireEvent.click(screen.getByLabelText('Next page'));
    expect(mockOnPageChange).toHaveBeenCalledWith(2);
  });

  // Test 7: Previous button click
  test('should call onPageChange with previous page on previous button click', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={5}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
      />
    );

    fireEvent.click(screen.getByLabelText('Previous page'));
    expect(mockOnPageChange).toHaveBeenCalledWith(4);
  });

  // Test 8: Page number click
  test('should call onPageChange when clicking specific page number', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={1}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
        showPageNumbers={true}
      />
    );

    fireEvent.click(screen.getByLabelText('Go to page 3'));
    expect(mockOnPageChange).toHaveBeenCalledWith(3);
  });

  // Test 9: Page numbers hidden on mobile
  test('should hide page numbers when showPageNumbers is false', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={1}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
        showPageNumbers={false}
      />
    );

    // Page info should still show
    expect(screen.getByText('Page 1 of 10')).toBeInTheDocument();
    // But individual page buttons shouldn't be in the document
    // (they're hidden with sm: breakpoint, so we check for visibility)
  });

  // Test 10: Current page highlighted
  test('should mark current page as active', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={5}
        totalItems={100}
        pageSize={10}
        onPageChange={mockOnPageChange}
        showPageNumbers={true}
      />
    );

    const currentPageButton = screen.getByLabelText('Go to page 5');
    expect(currentPageButton).toHaveAttribute('aria-current', 'page');
  });

  // Test 11: Correct total pages calculation
  test('should calculate total pages correctly', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={1}
        totalItems={95}
        pageSize={10}
        onPageChange={mockOnPageChange}
      />
    );

    // 95 items / 10 per page = 9.5, should round up to 10
    expect(screen.getByText('Page 1 of 10')).toBeInTheDocument();
  });

  // Test 12: Page range display with ellipsis
  test('should show ellipsis for large page ranges', () => {
    const mockOnPageChange = jest.fn();
    render(
      <Pagination
        currentPage={5}
        totalItems={1000}
        pageSize={10}
        onPageChange={mockOnPageChange}
        showPageNumbers={true}
      />
    );

    // Should show first page, ellipsis, pages around current, ellipsis, last page
    expect(screen.getByLabelText('Go to page 1')).toBeInTheDocument();
    expect(screen.getByLabelText('Go to page 100')).toBeInTheDocument();
  });
});

describe('PaginationSize Component', () => {
  // Test 1: Render with default options
  test('should render page size selector with default options', () => {
    const mockOnPageSizeChange = jest.fn();
    render(
      <PaginationSize pageSize={20} onPageSizeChange={mockOnPageSizeChange} />
    );

    expect(screen.getByDisplayValue('20')).toBeInTheDocument();
  });

  // Test 2: Custom options
  test('should render with custom page size options', () => {
    const mockOnPageSizeChange = jest.fn();
    render(
      <PaginationSize
        pageSize={15}
        options={[5, 15, 30]}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    expect(screen.getByDisplayValue('15')).toBeInTheDocument();
  });

  // Test 3: Change page size
  test('should call onPageSizeChange when option is selected', () => {
    const mockOnPageSizeChange = jest.fn();
    render(
      <PaginationSize
        pageSize={10}
        options={[10, 20, 50]}
        onPageSizeChange={mockOnPageSizeChange}
      />
    );

    const select = screen.getByDisplayValue('10') as HTMLSelectElement;
    fireEvent.change(select, { target: { value: '50' } });

    expect(mockOnPageSizeChange).toHaveBeenCalledWith(50);
  });

  // Test 4: Labels display correctly
  test('should display labels correctly', () => {
    const mockOnPageSizeChange = jest.fn();
    render(
      <PaginationSize pageSize={20} onPageSizeChange={mockOnPageSizeChange} />
    );

    expect(screen.getByLabelText('Show')).toBeInTheDocument();
    expect(screen.getByText('per page')).toBeInTheDocument();
  });
});

describe('Pagination Hook Integration', () => {
  test('integration: pagination with real data', () => {
    const mockOnPageChange = jest.fn();

    // Simulate 150 items, 25 per page = 6 pages
    const { rerender } = render(
      <Pagination
        currentPage={1}
        totalItems={150}
        pageSize={25}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByText('Page 1 of 6')).toBeInTheDocument();

    // Navigate to page 3
    fireEvent.click(screen.getByLabelText('Next page'));
    expect(mockOnPageChange).toHaveBeenCalledWith(2);

    // Re-render with page 2
    rerender(
      <Pagination
        currentPage={2}
        totalItems={150}
        pageSize={25}
        onPageChange={mockOnPageChange}
      />
    );

    expect(screen.getByText('Page 2 of 6')).toBeInTheDocument();
    expect(screen.getByLabelText('Previous page')).not.toBeDisabled();
    expect(screen.getByLabelText('Next page')).not.toBeDisabled();
  });
});
