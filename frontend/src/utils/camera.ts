import { Camera, CameraResultType, CameraSource, Photo } from '@capacitor/camera';
import { Filesystem, Directory } from '@capacitor/filesystem';
import { isMobile, hapticFeedback } from './capacitor';

export interface CameraOptions {
  quality?: number;
  allowEditing?: boolean;
  saveToGallery?: boolean;
}

export interface PhotoResult {
  base64Data: string;
  webPath: string;
  format: string;
}

/**
 * Elder-friendly camera utilities
 */
export const cameraUtils = {
  /**
   * Take a photo with elder-friendly settings
   */
  async takePhoto(options: CameraOptions = {}): Promise<PhotoResult | null> {
    try {
      // Request camera permissions
      const permissions = await Camera.requestPermissions();
      
      if (permissions.camera !== 'granted') {
        throw new Error('Camera permission denied');
      }
      
      // Haptic feedback before capture
      await hapticFeedback.light();
      
      // Take photo with optimized settings for elderly users
      const photo = await Camera.getPhoto({
        quality: options.quality || 90,
        allowEditing: options.allowEditing || false,
        resultType: CameraResultType.Base64,
        source: CameraSource.Camera,
        saveToGallery: options.saveToGallery || true,
        width: 1024, // Reasonable size for medication identification
        height: 1024,
        correctOrientation: true,
        presentationStyle: 'popover'
      });
      
      // Success haptic feedback
      await hapticFeedback.success();
      
      return {
        base64Data: photo.base64String || '',
        webPath: photo.webPath,
        format: photo.format
      };
      
    } catch (error) {
      console.error('Camera error:', error);
      await hapticFeedback.error();
      
      // User-friendly error messages
      if (error instanceof Error) {
        if (error.message.includes('cancelled')) {
          return null; // User cancelled, not an error
        }
        throw new Error(getElderlyFriendlyErrorMessage(error.message));
      }
      throw error;
    }
  },
  
  /**
   * Select a photo from gallery
   */
  async selectFromGallery(): Promise<PhotoResult | null> {
    try {
      const permissions = await Camera.requestPermissions();
      
      if (permissions.photos !== 'granted') {
        throw new Error('Photo library permission denied');
      }
      
      await hapticFeedback.light();
      
      const photo = await Camera.getPhoto({
        quality: 90,
        resultType: CameraResultType.Base64,
        source: CameraSource.Photos,
        width: 1024,
        height: 1024,
        correctOrientation: true
      });
      
      await hapticFeedback.success();
      
      return {
        base64Data: photo.base64String || '',
        webPath: photo.webPath,
        format: photo.format
      };
      
    } catch (error) {
      console.error('Gallery error:', error);
      await hapticFeedback.error();
      
      if (error instanceof Error && error.message.includes('cancelled')) {
        return null;
      }
      throw error;
    }
  },
  
  /**
   * Save photo to device storage
   */
  async savePhoto(base64Data: string, fileName: string): Promise<string> {
    try {
      const savedFile = await Filesystem.writeFile({
        path: `medications/${fileName}`,
        data: base64Data,
        directory: Directory.Data,
        recursive: true
      });
      
      return savedFile.uri;
    } catch (error) {
      console.error('Save photo error:', error);
      throw new Error('Unable to save photo');
    }
  },
  
  /**
   * Delete a saved photo
   */
  async deletePhoto(fileName: string): Promise<void> {
    try {
      await Filesystem.deleteFile({
        path: `medications/${fileName}`,
        directory: Directory.Data
      });
    } catch (error) {
      console.error('Delete photo error:', error);
    }
  },
  
  /**
   * Check if camera is available
   */
  async isCameraAvailable(): Promise<boolean> {
    if (!isMobile) return false;
    
    try {
      const permissions = await Camera.checkPermissions();
      return permissions.camera === 'granted' || permissions.camera === 'prompt';
    } catch {
      return false;
    }
  }
};

/**
 * Convert error messages to elder-friendly language
 */
function getElderlyFriendlyErrorMessage(originalMessage: string): string {
  const errorMap: Record<string, string> = {
    'permission denied': 'Please allow the app to use your camera in Settings',
    'camera unavailable': 'Camera is not available right now. Please try again.',
    'no camera': 'No camera found on this device',
    'user cancelled': 'Photo cancelled',
    'out of memory': 'Not enough space to save photo. Please free up some space.'
  };
  
  const lowerMessage = originalMessage.toLowerCase();
  
  for (const [key, friendlyMessage] of Object.entries(errorMap)) {
    if (lowerMessage.includes(key)) {
      return friendlyMessage;
    }
  }
  
  return 'Something went wrong. Please try again.';
}

/**
 * Elder-friendly camera instructions
 */
export const cameraInstructions = {
  medication: {
    title: 'Taking a Medication Photo',
    steps: [
      'Place the pill on a plain, light-colored surface',
      'Make sure the room is well-lit',
      'Hold your phone steady above the pill',
      'The pill should fill most of the frame',
      'Tap the capture button when ready'
    ],
    tips: [
      'Natural light works best',
      'Avoid shadows on the pill',
      'Make sure any text on the pill is visible',
      'Take multiple photos if needed'
    ]
  }
};

/**
 * Validate if photo is suitable for medication identification
 */
export async function validateMedicationPhoto(base64Data: string): Promise<{
  isValid: boolean;
  issues: string[];
}> {
  const issues: string[] = [];
  
  try {
    // Check file size (base64 is ~1.37x larger than binary)
    const sizeInBytes = base64Data.length * 0.75;
    const sizeInMB = sizeInBytes / (1024 * 1024);
    
    if (sizeInMB > 10) {
      issues.push('Photo is too large. Please try again.');
    }
    
    if (sizeInMB < 0.01) {
      issues.push('Photo is too small. Please take a clearer photo.');
    }
    
    // Basic format validation
    if (!base64Data.startsWith('data:image/') && base64Data.length < 100) {
      issues.push('Invalid photo format.');
    }
    
    return {
      isValid: issues.length === 0,
      issues
    };
    
  } catch (error) {
    return {
      isValid: false,
      issues: ['Unable to validate photo. Please try again.']
    };
  }
}