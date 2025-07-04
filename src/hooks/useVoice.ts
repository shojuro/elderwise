import { useEffect, useCallback } from 'react';
import { useVoiceStore } from '../store';
import { voiceService } from '../services/voice';

export const useVoice = () => {
  const {
    isListening,
    isProcessing,
    transcript,
    confidence,
    error,
    startListening,
    stopListening,
    setError,
    resetVoice,
  } = useVoiceStore();

  // Check if voice is supported
  const isSupported = voiceService.isVoiceSupported();
  const isSpeechSynthesisSupported = voiceService.isSpeechSynthesisSupported();

  // Start voice recognition
  const startVoiceRecognition = useCallback(async () => {
    if (!isSupported) {
      setError('Voice recognition is not supported in this browser');
      return false;
    }

    // Request microphone permission first
    const hasPermission = await voiceService.requestMicrophonePermission();
    if (!hasPermission) {
      setError('Microphone permission is required for voice input');
      return false;
    }

    return voiceService.startListening();
  }, [isSupported, setError]);

  // Stop voice recognition
  const stopVoiceRecognition = useCallback(() => {
    voiceService.stopListening();
  }, []);

  // Speak text (AI response)
  const speak = useCallback(async (text: string, options?: any) => {
    if (!isSpeechSynthesisSupported) {
      console.warn('Speech synthesis not supported');
      return;
    }

    try {
      await voiceService.speak(text, {
        rate: 0.8, // Slower for elderly users
        pitch: 1.0,
        volume: 0.9,
        ...options,
      });
    } catch (error) {
      console.error('Speech synthesis error:', error);
    }
  }, [isSpeechSynthesisSupported]);

  // Stop speaking
  const stopSpeaking = useCallback(() => {
    voiceService.stopSpeaking();
  }, []);

  // Get available voices
  const getVoices = useCallback(() => {
    return voiceService.getAvailableVoices();
  }, []);

  // Reset voice state
  const reset = useCallback(() => {
    voiceService.stopListening();
    voiceService.stopSpeaking();
    resetVoice();
  }, [resetVoice]);

  // Check microphone availability
  const checkMicrophoneAvailability = useCallback(async () => {
    return await voiceService.isMicrophoneAvailable();
  }, []);

  // Auto-stop listening after timeout
  useEffect(() => {
    if (!isListening) return;

    const timeout = setTimeout(() => {
      stopVoiceRecognition();
    }, 30000); // 30 seconds timeout

    return () => clearTimeout(timeout);
  }, [isListening, stopVoiceRecognition]);

  // Voice activity detection
  const startVoiceActivityDetection = useCallback(async (
    onVoiceStart: () => void,
    onVoiceEnd: () => void
  ) => {
    try {
      const cleanup = await voiceService.createVoiceActivityDetector(
        onVoiceStart,
        onVoiceEnd,
        0.01 // Threshold for voice detection
      );
      return cleanup;
    } catch (error) {
      console.error('Failed to start voice activity detection:', error);
      setError('Failed to access microphone for voice detection');
      return null;
    }
  }, [setError]);

  // Continuous listening mode (for hands-free operation)
  const startContinuousListening = useCallback(async () => {
    if (!isSupported) return null;

    let isActive = true;
    const restartDelay = 1000; // 1 second between restarts

    const continuousLoop = async () => {
      while (isActive) {
        try {
          const success = await startVoiceRecognition();
          if (!success) break;

          // Wait for recognition to complete
          await new Promise<void>((resolve) => {
            const checkStatus = () => {
              if (!isListening && !isProcessing) {
                resolve();
              } else {
                setTimeout(checkStatus, 100);
              }
            };
            checkStatus();
          });

          // Small delay before restarting
          await new Promise(resolve => setTimeout(resolve, restartDelay));
        } catch (error) {
          console.error('Continuous listening error:', error);
          break;
        }
      }
    };

    continuousLoop();

    // Return stop function
    return () => {
      isActive = false;
      stopVoiceRecognition();
    };
  }, [isSupported, startVoiceRecognition, stopVoiceRecognition, isListening, isProcessing]);

  return {
    // State
    isListening,
    isProcessing,
    transcript,
    confidence,
    error,
    isSupported,
    isSpeechSynthesisSupported,

    // Actions
    startVoiceRecognition,
    stopVoiceRecognition,
    speak,
    stopSpeaking,
    reset,

    // Utils
    getVoices,
    checkMicrophoneAvailability,
    startVoiceActivityDetection,
    startContinuousListening,

    // Computed
    hasTranscript: transcript.length > 0,
    isReady: !isProcessing && !error,
  };
};

// Hook for managing voice responses to AI messages
export const useVoiceResponse = () => {
  const { speak, stopSpeaking, isSpeechSynthesisSupported } = useVoice();
  const { preferences } = useAppStore();

  const speakMessage = useCallback(async (message: string) => {
    if (!preferences.voiceEnabled || !isSpeechSynthesisSupported) {
      return;
    }

    // Clean up the message for better speech
    const cleanMessage = message
      .replace(/\*\*(.*?)\*\*/g, '$1') // Remove bold markdown
      .replace(/\*(.*?)\*/g, '$1') // Remove italic markdown
      .replace(/`(.*?)`/g, '$1') // Remove code markdown
      .replace(/\[.*?\]\(.*?\)/g, '') // Remove links
      .replace(/\n\n/g, '. ') // Replace double newlines with periods
      .replace(/\n/g, ' ') // Replace single newlines with spaces
      .trim();

    await speak(cleanMessage, {
      rate: 0.7, // Slower for elderly users
      pitch: 1.0,
      volume: 0.8,
    });
  }, [speak, preferences.voiceEnabled, isSpeechSynthesisSupported]);

  return {
    speakMessage,
    stopSpeaking,
    isEnabled: preferences.voiceEnabled && isSpeechSynthesisSupported,
  };
};