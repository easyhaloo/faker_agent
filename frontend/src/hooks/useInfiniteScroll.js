import { useEffect, useRef, useCallback, useState } from 'react';

/**
 * Custom hook for infinite scroll with Intersection Observer
 * Provides seamless pagination with better performance than scroll event listeners
 */
export const useInfiniteScroll = ({ 
  hasMore, 
  isLoading, 
  onLoadMore, 
  threshold = 0.5, 
  rootMargin = '50px',
  delay = 150 
}) => {
  const observerRef = useRef(null);
  const loadingRef = useRef(false);
  const [targetElement, setTargetElement] = useState(null);
  const loadMoreTimeoutRef = useRef(null);

  // Reset loading ref when isLoading changes
  useEffect(() => {
    loadingRef.current = isLoading;
  }, [isLoading]);

  const handleIntersection = useCallback((entries) => {
    const [entry] = entries;
    
    // Check if the target element is intersecting and we should load more
    if (entry.isIntersecting && hasMore && !loadingRef.current) {
      // Add a small delay to prevent immediate loading on fast scroll
      if (loadMoreTimeoutRef.current) {
        clearTimeout(loadMoreTimeoutRef.current);
      }
      
      loadMoreTimeoutRef.current = setTimeout(() => {
        if (hasMore && !loadingRef.current && onLoadMore) {
          onLoadMore();
        }
      }, delay);
    }
  }, [hasMore, onLoadMore, delay]);

  useEffect(() => {
    if (!targetElement) return;

    // Create intersection observer
    observerRef.current = new IntersectionObserver(handleIntersection, {
      threshold,
      rootMargin,
      root: null // Use viewport as root
    });

    // Start observing the target element
    observerRef.current.observe(targetElement);

    // Cleanup function
    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
      if (loadMoreTimeoutRef.current) {
        clearTimeout(loadMoreTimeoutRef.current);
      }
    };
  }, [targetElement, handleIntersection, threshold, rootMargin]);

  // Method to set the target element for observation
  const setObserverTarget = useCallback((element) => {
    if (element) {
      setTargetElement(element);
    }
  }, []);

  return {
    setObserverTarget,
    observerRef
  };
};

/**
 * Hook for optimizing scroll performance and preventing layout shifts
 */
export const useScrollOptimizer = ({ 
  containerRef, 
  itemHeight = 80, 
  bufferSize = 5 
}) => {
  const [visibleRange, setVisibleRange] = useState({ start: 0, end: 20 });
  const [scrollTop, setScrollTop] = useState(0);
  const rafRef = useRef(null);

  const updateVisibleRange = useCallback(() => {
    if (!containerRef.current) return;

    const container = containerRef.current;
    const scrollTop = container.scrollTop;
    const containerHeight = container.clientHeight;
    
    // Calculate visible range with buffer
    const startIndex = Math.max(0, Math.floor(scrollTop / itemHeight) - bufferSize);
    const endIndex = Math.ceil((scrollTop + containerHeight) / itemHeight) + bufferSize;
    
    setVisibleRange({ start: startIndex, end: endIndex });
    setScrollTop(scrollTop);
  }, [containerRef, itemHeight, bufferSize]);

  const handleScroll = useCallback(() => {
    // Use requestAnimationFrame for smooth performance
    if (rafRef.current) {
      cancelAnimationFrame(rafRef.current);
    }
    
    rafRef.current = requestAnimationFrame(updateVisibleRange);
  }, [updateVisibleRange]);

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('scroll', handleScroll, { passive: true });
    updateVisibleRange(); // Initial calculation

    return () => {
      container.removeEventListener('scroll', handleScroll);
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
    };
  }, [containerRef, handleScroll, updateVisibleRange]);

  return {
    visibleRange,
    scrollTop,
    handleScroll
  };
};