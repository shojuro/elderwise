/**
 * Accessibility utilities for ElderWise
 * Ensures WCAG 2.1 AA compliance for elderly users
 */

// Screen reader announcements
export const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
  const announcer = document.createElement('div');
  announcer.setAttribute('role', 'status');
  announcer.setAttribute('aria-live', priority);
  announcer.setAttribute('aria-atomic', 'true');
  announcer.className = 'sr-only';
  announcer.textContent = message;
  
  document.body.appendChild(announcer);
  
  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcer);
  }, 1000);
};

// Focus management
export const focusManagement = {
  // Trap focus within a container
  trapFocus: (container: HTMLElement) => {
    const focusableElements = container.querySelectorAll<HTMLElement>(
      'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstFocusable = focusableElements[0];
    const lastFocusable = focusableElements[focusableElements.length - 1];
    
    const handleTabKey = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;
      
      if (e.shiftKey) {
        if (document.activeElement === firstFocusable) {
          lastFocusable.focus();
          e.preventDefault();
        }
      } else {
        if (document.activeElement === lastFocusable) {
          firstFocusable.focus();
          e.preventDefault();
        }
      }
    };
    
    container.addEventListener('keydown', handleTabKey);
    
    return () => {
      container.removeEventListener('keydown', handleTabKey);
    };
  },
  
  // Restore focus to a previously focused element
  restoreFocus: (element: HTMLElement | null) => {
    if (element && typeof element.focus === 'function') {
      element.focus();
    }
  },
  
  // Get currently focused element
  getCurrentFocus: (): HTMLElement | null => {
    return document.activeElement as HTMLElement;
  }
};

// Keyboard navigation
export const keyboardNavigation = {
  // Handle arrow key navigation in lists
  handleListNavigation: (
    e: KeyboardEvent,
    currentIndex: number,
    totalItems: number,
    onNavigate: (newIndex: number) => void
  ) => {
    switch (e.key) {
      case 'ArrowDown':
      case 'ArrowRight':
        e.preventDefault();
        onNavigate((currentIndex + 1) % totalItems);
        break;
      case 'ArrowUp':
      case 'ArrowLeft':
        e.preventDefault();
        onNavigate((currentIndex - 1 + totalItems) % totalItems);
        break;
      case 'Home':
        e.preventDefault();
        onNavigate(0);
        break;
      case 'End':
        e.preventDefault();
        onNavigate(totalItems - 1);
        break;
    }
  },
  
  // Check if user prefers keyboard navigation
  isKeyboardUser: () => {
    return document.body.classList.contains('keyboard-navigation');
  }
};

// Color contrast utilities
export const colorContrast = {
  // Calculate contrast ratio between two colors
  getContrastRatio: (color1: string, color2: string): number => {
    const getLuminance = (rgb: number[]): number => {
      const [r, g, b] = rgb.map(val => {
        val = val / 255;
        return val <= 0.03928 ? val / 12.92 : Math.pow((val + 0.055) / 1.055, 2.4);
      });
      return 0.2126 * r + 0.7152 * g + 0.0722 * b;
    };
    
    // Convert hex to RGB
    const hexToRgb = (hex: string): number[] => {
      const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
      return result
        ? [parseInt(result[1], 16), parseInt(result[2], 16), parseInt(result[3], 16)]
        : [0, 0, 0];
    };
    
    const rgb1 = hexToRgb(color1);
    const rgb2 = hexToRgb(color2);
    
    const lum1 = getLuminance(rgb1);
    const lum2 = getLuminance(rgb2);
    
    const brightest = Math.max(lum1, lum2);
    const darkest = Math.min(lum1, lum2);
    
    return (brightest + 0.05) / (darkest + 0.05);
  },
  
  // Check if contrast meets WCAG AA standards
  meetsWCAGAA: (ratio: number, fontSize: number): boolean => {
    // Large text (18pt or 14pt bold) requires 3:1
    // Normal text requires 4.5:1
    return fontSize >= 18 ? ratio >= 3 : ratio >= 4.5;
  }
};

// Motion preferences
export const motionPreferences = {
  // Check if user prefers reduced motion
  prefersReducedMotion: (): boolean => {
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  },
  
  // Apply reduced motion styles
  applyReducedMotion: () => {
    if (motionPreferences.prefersReducedMotion()) {
      document.documentElement.classList.add('reduce-motion');
    }
  }
};

// High contrast mode
export const highContrastMode = {
  // Check if high contrast mode is enabled
  isEnabled: (): boolean => {
    return (
      window.matchMedia('(prefers-contrast: high)').matches ||
      document.documentElement.classList.contains('high-contrast')
    );
  },
  
  // Toggle high contrast mode
  toggle: (enable?: boolean) => {
    const shouldEnable = enable ?? !document.documentElement.classList.contains('high-contrast');
    
    if (shouldEnable) {
      document.documentElement.classList.add('high-contrast');
      localStorage.setItem('elderwise-high-contrast', 'true');
    } else {
      document.documentElement.classList.remove('high-contrast');
      localStorage.removeItem('elderwise-high-contrast');
    }
  },
  
  // Initialize from user preferences
  init: () => {
    const saved = localStorage.getItem('elderwise-high-contrast');
    if (saved === 'true' || window.matchMedia('(prefers-contrast: high)').matches) {
      highContrastMode.toggle(true);
    }
  }
};

// Text size preferences
export const textSizePreferences = {
  sizes: ['small', 'medium', 'large', 'extra-large'] as const,
  
  // Get current text size
  getCurrent: (): string => {
    return localStorage.getItem('elderwise-text-size') || 'large';
  },
  
  // Set text size
  setSize: (size: 'small' | 'medium' | 'large' | 'extra-large') => {
    // Remove all size classes
    textSizePreferences.sizes.forEach(s => {
      document.documentElement.classList.remove(`text-size-${s}`);
    });
    
    // Add new size class
    document.documentElement.classList.add(`text-size-${size}`);
    localStorage.setItem('elderwise-text-size', size);
    
    // Announce change
    announce(`Text size changed to ${size.replace('-', ' ')}`);
  },
  
  // Initialize from saved preferences
  init: () => {
    const savedSize = textSizePreferences.getCurrent();
    textSizePreferences.setSize(savedSize as any);
  }
};

// Voice control utilities
export const voiceControl = {
  // Check if voice control is supported
  isSupported: (): boolean => {
    return 'webkitSpeechRecognition' in window || 'SpeechRecognition' in window;
  },
  
  // Voice commands configuration
  commands: {
    'go home': () => window.location.href = '/',
    'go back': () => window.history.back(),
    'scroll down': () => window.scrollBy(0, window.innerHeight / 2),
    'scroll up': () => window.scrollBy(0, -window.innerHeight / 2),
    'help': () => announce('Available commands: go home, go back, scroll up, scroll down, help'),
  }
};

// Initialize all accessibility features
export const initializeAccessibility = () => {
  // Set up keyboard navigation detection
  document.addEventListener('mousedown', () => {
    document.body.classList.remove('keyboard-navigation');
  });
  
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      document.body.classList.add('keyboard-navigation');
    }
  });
  
  // Initialize user preferences
  motionPreferences.applyReducedMotion();
  highContrastMode.init();
  textSizePreferences.init();
  
  // Set up skip links
  const skipLink = document.querySelector<HTMLAnchorElement>('#skip-to-content');
  if (skipLink) {
    skipLink.addEventListener('click', (e) => {
      e.preventDefault();
      const main = document.querySelector<HTMLElement>('main');
      if (main) {
        main.tabIndex = -1;
        main.focus();
        main.scrollIntoView();
      }
    });
  }
};

// ARIA live region manager
export class LiveRegionManager {
  private container: HTMLElement;
  
  constructor() {
    this.container = document.createElement('div');
    this.container.className = 'sr-only';
    this.container.setAttribute('aria-live', 'polite');
    this.container.setAttribute('aria-atomic', 'true');
    document.body.appendChild(this.container);
  }
  
  announce(message: string, priority: 'polite' | 'assertive' = 'polite') {
    this.container.setAttribute('aria-live', priority);
    this.container.textContent = message;
    
    // Clear after announcement
    setTimeout(() => {
      this.container.textContent = '';
    }, 1000);
  }
  
  destroy() {
    document.body.removeChild(this.container);
  }
}

// Form validation announcements
export const formAccessibility = {
  announceError: (fieldName: string, error: string) => {
    announce(`Error in ${fieldName}: ${error}`, 'assertive');
  },
  
  announceSuccess: (message: string) => {
    announce(message, 'polite');
  },
  
  // Add error summary at form level
  createErrorSummary: (errors: Record<string, string>) => {
    const errorCount = Object.keys(errors).length;
    if (errorCount === 0) return null;
    
    const summary = document.createElement('div');
    summary.setAttribute('role', 'alert');
    summary.className = 'error-summary';
    
    const heading = document.createElement('h3');
    heading.textContent = `There ${errorCount === 1 ? 'is' : 'are'} ${errorCount} error${errorCount === 1 ? '' : 's'} in this form`;
    summary.appendChild(heading);
    
    const list = document.createElement('ul');
    Object.entries(errors).forEach(([field, error]) => {
      const item = document.createElement('li');
      const link = document.createElement('a');
      link.href = `#${field}`;
      link.textContent = `${field}: ${error}`;
      item.appendChild(link);
      list.appendChild(item);
    });
    summary.appendChild(list);
    
    return summary;
  }
};