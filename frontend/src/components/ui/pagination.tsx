import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from './button';
import { cn } from '@/lib/utils';

export interface PaginationProps {
  /** Current page number (1-indexed) */
  currentPage: number;
  /** Total number of items */
  totalItems: number;
  /** Items per page */
  pageSize: number;
  /** Callback when page changes */
  onPageChange: (page: number) => void;
  /** Show page numbers (disable on mobile) */
  showPageNumbers?: boolean;
  /** Custom className */
  className?: string;
}

export function Pagination({
  currentPage,
  totalItems,
  pageSize,
  onPageChange,
  showPageNumbers = true,
  className,
}: PaginationProps) {
  const totalPages = Math.ceil(totalItems / pageSize);

  // If only one page, don't show pagination
  if (totalPages <= 1) {
    return null;
  }

  const isFirstPage = currentPage === 1;
  const isLastPage = currentPage === totalPages;

  // Generate page numbers to display
  // Logic: show first, last, and 2 pages on each side of current
  const generatePageNumbers = () => {
    const pages: (number | string)[] = [];
    const maxPagesToShow = 5;
    const sidePages = 2;

    if (totalPages <= maxPagesToShow) {
      // Show all pages if total is small
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      // Always show first page
      pages.push(1);

      // Calculate range around current page
      const start = Math.max(2, currentPage - sidePages);
      const end = Math.min(totalPages - 1, currentPage + sidePages);

      // Add ellipsis if there's a gap
      if (start > 2) {
        pages.push('...');
      }

      // Add pages around current
      for (let i = start; i <= end; i++) {
        pages.push(i);
      }

      // Add ellipsis if there's a gap
      if (end < totalPages - 1) {
        pages.push('...');
      }

      // Always show last page
      pages.push(totalPages);
    }

    return pages;
  };

  const handlePreviousPage = () => {
    if (!isFirstPage) {
      onPageChange(currentPage - 1);
    }
  };

  const handleNextPage = () => {
    if (!isLastPage) {
      onPageChange(currentPage + 1);
    }
  };

  const handlePageClick = (page: number) => {
    if (page !== currentPage) {
      onPageChange(page);
    }
  };

  const pageNumbers = generatePageNumbers();

  return (
    <div
      className={cn(
        'flex items-center justify-center gap-2 py-4',
        className
      )}
    >
      {/* Previous Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handlePreviousPage}
        disabled={isFirstPage}
        className={cn(
          'gap-1.5 px-3',
          'text-on-surface-variant hover:text-on-surface',
          'border-outline-variant/30 hover:border-outline-variant/60',
          'transition-all duration-200'
        )}
        aria-label="Previous page"
      >
        <ChevronLeft className="w-4 h-4" />
        <span className="text-xs font-medium hidden sm:inline">Previous</span>
      </Button>

      {/* Page Numbers - Hidden on mobile, shown on tablet+ */}
      {showPageNumbers && (
        <div className="hidden sm:flex items-center gap-1">
          {pageNumbers.map((page, idx) => {
            if (page === '...') {
              return (
                <span
                  key={`ellipsis-${idx}`}
                  className="px-2 py-1 text-on-surface-variant text-xs"
                >
                  …
                </span>
              );
            }

            const pageNum = page as number;
            const isActive = pageNum === currentPage;

            return (
              <Button
                key={pageNum}
                variant={isActive ? 'secondary' : 'outline'}
                size="sm"
                onClick={() => handlePageClick(pageNum)}
                className={cn(
                  'w-8 h-8 p-0 text-xs font-medium',
                  isActive
                    ? 'bg-secondary text-on-secondary border-secondary'
                    : 'text-on-surface border-outline-variant/30 hover:border-outline-variant/60',
                  'transition-all duration-200'
                )}
                aria-label={`Go to page ${pageNum}`}
                aria-current={isActive ? 'page' : undefined}
              >
                {pageNum}
              </Button>
            );
          })}
        </div>
      )}

      {/* Next Button */}
      <Button
        variant="outline"
        size="sm"
        onClick={handleNextPage}
        disabled={isLastPage}
        className={cn(
          'gap-1.5 px-3',
          'text-on-surface-variant hover:text-on-surface',
          'border-outline-variant/30 hover:border-outline-variant/60',
          'transition-all duration-200'
        )}
        aria-label="Next page"
      >
        <span className="text-xs font-medium hidden sm:inline">Next</span>
        <ChevronRight className="w-4 h-4" />
      </Button>

      {/* Page Info - Shown on all sizes */}
      <div className="ml-auto">
        <p className="text-xs text-on-surface-variant whitespace-nowrap">
          Page <span className="font-semibold text-on-surface">{currentPage}</span> of{' '}
          <span className="font-semibold text-on-surface">{totalPages}</span>
        </p>
      </div>
    </div>
  );
}

/**
 * Pagination size selector component for choosing items per page
 */
export interface PaginationSizeProps {
  /** Current page size */
  pageSize: number;
  /** Available page size options */
  options?: number[];
  /** Callback when page size changes */
  onPageSizeChange: (size: number) => void;
  /** Custom className */
  className?: string;
}

export function PaginationSize({
  pageSize,
  options = [10, 20, 50, 100],
  onPageSizeChange,
  className,
}: PaginationSizeProps) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <label htmlFor="page-size" className="text-xs text-on-surface-variant font-medium">
        Show
      </label>
      <select
        id="page-size"
        value={pageSize}
        onChange={(e) => onPageSizeChange(Number(e.target.value))}
        className={cn(
          'px-2 py-1 rounded-md text-xs font-medium',
          'bg-surface-container-low border border-outline-variant/30',
          'text-on-surface hover:border-outline-variant/60',
          'focus:outline-none focus:ring-2 focus:ring-secondary/40',
          'transition-all duration-200'
        )}
      >
        {options.map((option) => (
          <option key={option} value={option}>
            {option}
          </option>
        ))}
      </select>
      <span className="text-xs text-on-surface-variant">per page</span>
    </div>
  );
}

export default Pagination;
