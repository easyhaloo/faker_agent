/**
 * Infinite Scroll Optimizer
 * 
 * Utility functions for optimizing infinite scroll performance
 */

/**
 * Creates a debounced scroll handler for infinite scroll
 * @param {Function} callback - The function to call when scroll threshold is reached
 * @param {Object} options - Configuration options
 * @param {number} options.threshold - Pixels from bottom to trigger (default: 100)
 * @param {number} options.debounceDelay - Debounce delay in ms (default: 200)
 * @param {boolean} options.preventDuplicates - Prevent duplicate requests (default: true)
 * @returns {Object} - Scroll handler with cleanup method
 */
export function createOptimizedScrollHandler(callback, options = {}) {
  const {
    threshold = 100,
    debounceDelay = 200,
    preventDuplicates = true
  } = options;

  let scrollTimeout = null;
  let isRequesting = false;
  let isDestroyed = false;

  const handleScroll = (event) => {
    if (isDestroyed) return;

    const { scrollTop, scrollHeight, clientHeight } = event.target;
    const isNearBottom = scrollHeight - scrollTop - clientHeight <= threshold;

    // Clear existing timeout
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
    }

    // Set new timeout for debounced loading
    scrollTimeout = setTimeout(() => {
      if (isNearBottom && !isRequesting && !isDestroyed) {
        if (preventDuplicates) {
          isRequesting = true;
          callback().finally(() => {
            isRequesting = false;
          });
        } else {
          callback();
        }
      }
    }, debounceDelay);
  };

  // Cleanup function
  const cleanup = () => {
    isDestroyed = true;
    if (scrollTimeout) {
      clearTimeout(scrollTimeout);
      scrollTimeout = null;
    }
  };

  return {
    handleScroll,
    cleanup,
    // Expose for testing
    getIsRequesting: () => isRequesting
  };
}

/**
 * Throttles a function to prevent excessive calls
 * @param {Function} func - The function to throttle
 * @param {number} limit - Time limit in milliseconds
 * @returns {Function} - Throttled function
 */
export function throttle(func, limit) {
  let inThrottle;
  return function() {
    const args = arguments;
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

/**
 * Checks if an element is near the bottom of its scroll container
 * @param {HTMLElement} element - The scrollable element
 * @param {number} threshold - Pixels from bottom (default: 100)
 * @returns {boolean} - True if near bottom
 */
export function isNearBottom(element, threshold = 100) {
  if (!element) return false;
  
  const { scrollTop, scrollHeight, clientHeight } = element;
  return scrollHeight - scrollTop - clientHeight <= threshold;
}

/**
 * Creates a scroll observer with Intersection Observer API (more efficient)
 * @param {HTMLElement} sentinel - The sentinel element to observe
 * @param {Function} callback - Callback when sentinel is intersected
 * @param {Object} options - Intersection observer options
 * @returns {IntersectionObserver} - The observer instance
 */
export function createIntersectionScrollHandler(sentinel, callback, options = {}) {
  const {
    root = null,
    rootMargin = '100px',
    threshold = 0.1
  } = options;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        callback();
      }
    });
  }, {
    root,
    rootMargin,
    threshold
  });

  observer.observe(sentinel);
  return observer;
}

export default {
  createOptimizedScrollHandler,
  throttle,
  isNearBottom,
  createIntersectionScrollHandler
};