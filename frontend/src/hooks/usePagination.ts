import { useState, useCallback } from 'react';

export interface UsePaginationOptions {
  /** Initial page number (1-indexed) */
  initialPage?: number;
  /** Initial page size */
  initialPageSize?: number;
}

export interface UsePaginationReturn {
  /** Current page number */
  currentPage: number;
  /** Current page size */
  pageSize: number;
  /** Total number of items */
  totalItems: number;
  /** Total number of pages */
  totalPages: number;
  /** Start index for current page (0-indexed) */
  startIndex: number;
  /** End index for current page (0-indexed) */
  endIndex: number;
  /** Set current page */
  setCurrentPage: (page: number) => void;
  /** Set page size */
  setPageSize: (size: number) => void;
  /** Set total items count */
  setTotalItems: (total: number) => void;
  /** Reset pagination to initial state */
  reset: () => void;
  /** Go to first page */
  goToFirstPage: () => void;
  /** Go to last page */
  goToLastPage: () => void;
}

/**
 * Hook for managing pagination state
 * Handles current page, page size, and calculations
 */
export function usePagination({
  initialPage = 1,
  initialPageSize = 20,
}: UsePaginationOptions = {}): UsePaginationReturn {
  const [currentPage, setCurrentPage] = useState(initialPage);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [totalItems, setTotalItems] = useState(0);

  const totalPages = Math.max(1, Math.ceil(totalItems / pageSize));

  // Ensure currentPage doesn't exceed totalPages
  const validCurrentPage = Math.min(currentPage, totalPages);

  const startIndex = (validCurrentPage - 1) * pageSize;
  const endIndex = Math.min(startIndex + pageSize, totalItems);

  const handleSetCurrentPage = useCallback((page: number) => {
    const validPage = Math.max(1, Math.min(page, totalPages));
    setCurrentPage(validPage);
  }, [totalPages]);

  const handleSetPageSize = useCallback((size: number) => {
    setPageSize(Math.max(1, size));
    // Reset to first page when page size changes
    setCurrentPage(1);
  }, []);

  const handleSetTotalItems = useCallback((total: number) => {
    setTotalItems(Math.max(0, total));
  }, []);

  const handleReset = useCallback(() => {
    setCurrentPage(initialPage);
    setPageSize(initialPageSize);
    setTotalItems(0);
  }, [initialPage, initialPageSize]);

  const handleGoToFirstPage = useCallback(() => {
    setCurrentPage(1);
  }, []);

  const handleGoToLastPage = useCallback(() => {
    setCurrentPage(Math.max(1, totalPages));
  }, [totalPages]);

  return {
    currentPage: validCurrentPage,
    pageSize,
    totalItems,
    totalPages,
    startIndex,
    endIndex,
    setCurrentPage: handleSetCurrentPage,
    setPageSize: handleSetPageSize,
    setTotalItems: handleSetTotalItems,
    reset: handleReset,
    goToFirstPage: handleGoToFirstPage,
    goToLastPage: handleGoToLastPage,
  };
}
