import { useState, useEffect, useRef, useCallback } from 'react';
import {
  announce,
  focusManagement,
  keyboardNavigation,
  motionPreferences,
  highContrastMode,
  textSizePreferences,
  LiveRegionManager
} from '../utils/accessibility';

// Hook for managing focus trap
export const useFocusTrap = (isActive: boolean) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const previousFocusRef = useRef<HTMLElement | null>(null);
  
  useEffect(() => {
    if (!isActive || !containerRef.current) return;
    
    // Store current focus
    previousFocusRef.current = focusManagement.getCurrentFocus();
    
    // Set up focus trap
    const cleanup = focusManagement.trapFocus(containerRef.current);
    
    // Focus first focusable element
    const firstFocusable = containerRef.current.querySelector<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    firstFocusable?.focus();
    
    return () => {
      cleanup();
      // Restore focus
      focusManagement.restoreFocus(previousFocusRef.current);
    };
  }, [isActive]);
  
  return containerRef;
};

// Hook for keyboard navigation in lists
export const useListKeyboardNavigation = (
  items: any[],
  onSelect: (index: number) => void,
  initialIndex: number = 0
) => {
  const [selectedIndex, setSelectedIndex] = useState(initialIndex);
  
  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    keyboardNavigation.handleListNavigation(
      e,
      selectedIndex,
      items.length,
      (newIndex) => {
        setSelectedIndex(newIndex);
        onSelect(newIndex);
      }
    );
    
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onSelect(selectedIndex);
    }
  }, [selectedIndex, items.length, onSelect]);
  
  return {
    selectedIndex,
    handleKeyDown,
    setSelectedIndex
  };
};

// Hook for managing announcements
export const useAnnouncement = () => {
  const liveRegionRef = useRef<LiveRegionManager | null>(null);
  
  useEffect(() => {
    liveRegionRef.current = new LiveRegionManager();
    
    return () => {
      liveRegionRef.current?.destroy();
    };
  }, []);
  
  const makeAnnouncement = useCallback((message: string, priority: 'polite' | 'assertive' = 'polite') => {
    liveRegionRef.current?.announce(message, priority);
  }, []);
  
  return makeAnnouncement;
};

// Hook for detecting and respecting motion preferences
export const useReducedMotion = () => {
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(
    motionPreferences.prefersReducedMotion()
  );
  
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    const handleChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };
    
    // Modern browsers
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
    // Legacy browsers
    else {
      mediaQuery.addListener(handleChange);
      return () => mediaQuery.removeListener(handleChange);
    }
  }, []);
  
  return prefersReducedMotion;
};

// Hook for managing high contrast mode
export const useHighContrast = () => {
  const [isHighContrast, setIsHighContrast] = useState(highContrastMode.isEnabled());
  
  const toggleHighContrast = useCallback(() => {
    highContrastMode.toggle();
    setIsHighContrast(highContrastMode.isEnabled());
  }, []);
  
  return {
    isHighContrast,
    toggleHighContrast
  };
};

// Hook for managing text size
export const useTextSize = () => {
  const [currentSize, setCurrentSize] = useState(textSizePreferences.getCurrent());
  
  const setTextSize = useCallback((size: 'small' | 'medium' | 'large' | 'extra-large') => {
    textSizePreferences.setSize(size);
    setCurrentSize(size);
  }, []);
  
  return {
    currentSize,
    setTextSize,
    availableSizes: textSizePreferences.sizes
  };
};

// Hook for skip navigation
export const useSkipNavigation = () => {
  const skipToMain = useCallback(() => {
    const main = document.querySelector<HTMLElement>('main');
    if (main) {
      main.tabIndex = -1;
      main.focus();
      main.scrollIntoView();
      announce('Skipped to main content');
    }
  }, []);
  
  const skipToNav = useCallback(() => {
    const nav = document.querySelector<HTMLElement>('nav');
    if (nav) {
      nav.tabIndex = -1;
      nav.focus();
      announce('Skipped to navigation');
    }
  }, []);
  
  return {
    skipToMain,
    skipToNav
  };
};

// Hook for form field announcements
export const useFormAnnouncements = () => {
  const announceRef = useAnnouncement();
  
  const announceFieldError = useCallback((fieldName: string, error: string) => {
    announceRef(`Error in ${fieldName}: ${error}`, 'assertive');
  }, [announceRef]);
  
  const announceFieldSuccess = useCallback((fieldName: string) => {
    announceRef(`${fieldName} is valid`, 'polite');
  }, [announceRef]);
  
  const announceFormSubmission = useCallback((success: boolean, message?: string) => {
    if (success) {
      announceRef(message || 'Form submitted successfully', 'polite');
    } else {
      announceRef(message || 'Form submission failed. Please check errors', 'assertive');
    }
  }, [announceRef]);
  
  return {
    announceFieldError,
    announceFieldSuccess,
    announceFormSubmission
  };
};

// Hook for managing ARIA attributes
export const useAriaAttributes = (role: string, label?: string) => {
  const idRef = useRef(`elderwise-${role}-${Date.now()}`);
  
  const ariaProps = {
    role,
    id: idRef.current,
    'aria-label': label,
    'aria-labelledby': label ? undefined : `${idRef.current}-label`,
    'aria-describedby': `${idRef.current}-description`
  };
  
  return {
    ariaProps,
    labelId: `${idRef.current}-label`,
    descriptionId: `${idRef.current}-description`
  };
};

// Hook for roving tabindex pattern
export const useRovingTabIndex = (items: any[]) => {
  const [focusedIndex, setFocusedIndex] = useState(0);
  const itemRefs = useRef<(HTMLElement | null)[]>([]);
  
  const handleKeyDown = useCallback((e: KeyboardEvent, index: number) => {
    switch (e.key) {
      case 'ArrowRight':
      case 'ArrowDown':
        e.preventDefault();
        const nextIndex = (index + 1) % items.length;
        setFocusedIndex(nextIndex);
        itemRefs.current[nextIndex]?.focus();
        break;
        
      case 'ArrowLeft':
      case 'ArrowUp':
        e.preventDefault();
        const prevIndex = (index - 1 + items.length) % items.length;
        setFocusedIndex(prevIndex);
        itemRefs.current[prevIndex]?.focus();
        break;
        
      case 'Home':
        e.preventDefault();
        setFocusedIndex(0);
        itemRefs.current[0]?.focus();
        break;
        
      case 'End':
        e.preventDefault();
        const lastIndex = items.length - 1;
        setFocusedIndex(lastIndex);
        itemRefs.current[lastIndex]?.focus();
        break;
    }
  }, [items.length]);
  
  const getTabIndex = (index: number) => index === focusedIndex ? 0 : -1;
  
  const setItemRef = (index: number) => (el: HTMLElement | null) => {
    itemRefs.current[index] = el;
  };
  
  return {
    focusedIndex,
    handleKeyDown,
    getTabIndex,
    setItemRef
  };
};