import { Capacitor } from '@capacitor/core';
import { App } from '@capacitor/app';
import { Haptics, ImpactStyle, NotificationType } from '@capacitor/haptics';
import { Keyboard } from '@capacitor/keyboard';
import { StatusBar, Style } from '@capacitor/status-bar';
import { SplashScreen } from '@capacitor/splash-screen';

// Check if running on mobile
export const isMobile = Capacitor.isNativePlatform();
export const isAndroid = Capacitor.getPlatform() === 'android';
export const isIOS = Capacitor.getPlatform() === 'ios';

// Haptic feedback for elder-friendly interactions
export const hapticFeedback = {
  light: async () => {
    if (isMobile) {
      await Haptics.impact({ style: ImpactStyle.Light });
    }
  },
  medium: async () => {
    if (isMobile) {
      await Haptics.impact({ style: ImpactStyle.Medium });
    }
  },
  heavy: async () => {
    if (isMobile) {
      await Haptics.impact({ style: ImpactStyle.Heavy });
    }
  },
  success: async () => {
    if (isMobile) {
      await Haptics.notification({ type: NotificationType.Success });
    }
  },
  error: async () => {
    if (isMobile) {
      await Haptics.notification({ type: NotificationType.Error });
    }
  }
};

// Initialize mobile-specific features
export const initializeMobile = async () => {
  if (!isMobile) return;

  try {
    // Hide splash screen
    await SplashScreen.hide();

    // Set status bar style
    await StatusBar.setStyle({ style: Style.Light });
    await StatusBar.setBackgroundColor({ color: '#B8A9E0' }); // Lavender

    // Handle back button
    App.addListener('backButton', (info) => {
      if (!info.canGoBack) {
        App.exitApp();
      } else {
        window.history.back();
      }
    });

    // Handle keyboard for better UX
    Keyboard.addListener('keyboardWillShow', () => {
      document.body.classList.add('keyboard-open');
    });

    Keyboard.addListener('keyboardWillHide', () => {
      document.body.classList.remove('keyboard-open');
    });

  } catch (error) {
    console.error('Error initializing mobile features:', error);
  }
};

// Elder-friendly mobile utilities
export const mobileUtils = {
  // Increase touch target size on mobile
  getTouchTargetSize: () => isMobile ? 'min-h-[60px]' : 'min-h-[48px]',
  
  // Get font size adjustments for mobile
  getMobileFontSize: (baseSize: string) => {
    if (!isMobile) return baseSize;
    
    const sizeMap: Record<string, string> = {
      'text-sm': 'text-base',
      'text-base': 'text-lg',
      'text-lg': 'text-xl',
      'text-xl': 'text-2xl',
      'text-2xl': 'text-3xl',
    };
    
    return sizeMap[baseSize] || baseSize;
  },
  
  // Vibrate on important actions
  vibrateOnAction: async () => {
    await hapticFeedback.light();
  },
};