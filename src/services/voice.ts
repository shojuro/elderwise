import { useVoiceStore } from '../store';

class VoiceService {
  private recognition: SpeechRecognition | null = null;
  private synthesis: SpeechSynthesis | null = null;
  private isSupported: boolean = false;

  constructor() {
    this.initializeSpeechRecognition();
    this.initializeSpeechSynthesis();
  }

  private initializeSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';
      this.recognition.maxAlternatives = 1;

      this.setupRecognitionEvents();
      this.isSupported = true;
    } else {
      console.warn('Speech recognition not supported in this browser');
      this.isSupported = false;
    }
  }

  private initializeSpeechSynthesis() {
    if ('speechSynthesis' in window) {
      this.synthesis = window.speechSynthesis;
    } else {
      console.warn('Speech synthesis not supported in this browser');
    }
  }

  private setupRecognitionEvents() {
    if (!this.recognition) return;

    const { setTranscript, setConfidence, setError, stopListening, setProcessing } = useVoiceStore.getState();

    this.recognition.onstart = () => {
      console.log('Voice recognition started');
    };

    this.recognition.onresult = (event) => {
      let finalTranscript = '';
      let interimTranscript = '';

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        const confidence = event.results[i][0].confidence;

        if (event.results[i].isFinal) {
          finalTranscript += transcript;
          setConfidence(confidence);
        } else {
          interimTranscript += transcript;
        }
      }

      if (finalTranscript) {
        setTranscript(finalTranscript.trim());
        setProcessing(true);
      } else {
        setTranscript(interimTranscript.trim());
      }
    };

    this.recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      let errorMessage = 'Voice recognition failed';
      
      switch (event.error) {
        case 'no-speech':
          errorMessage = 'No speech detected. Please try again.';
          break;
        case 'audio-capture':
          errorMessage = 'Microphone not accessible. Please check permissions.';
          break;
        case 'not-allowed':
          errorMessage = 'Microphone permission denied. Please enable microphone access.';
          break;
        case 'network':
          errorMessage = 'Network error. Please check your connection.';
          break;
        default:
          errorMessage = `Voice recognition error: ${event.error}`;
      }

      setError(errorMessage);
    };

    this.recognition.onend = () => {
      console.log('Voice recognition ended');
      stopListening();
      setProcessing(false);
    };
  }

  public startListening(): boolean {
    if (!this.isSupported || !this.recognition) {
      useVoiceStore.getState().setError('Voice recognition not supported in this browser');
      return false;
    }

    try {
      const { startListening, resetVoice } = useVoiceStore.getState();
      resetVoice();
      startListening();
      this.recognition.start();
      return true;
    } catch (error) {
      console.error('Failed to start voice recognition:', error);
      useVoiceStore.getState().setError('Failed to start voice recognition');
      return false;
    }
  }

  public stopListening(): void {
    if (this.recognition) {
      this.recognition.stop();
    }
  }

  public speak(text: string, options: SpeechSynthesisUtteranceOptions = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.synthesis) {
        reject(new Error('Speech synthesis not supported'));
        return;
      }

      // Cancel any ongoing speech
      this.synthesis.cancel();

      const utterance = new SpeechSynthesisUtterance(text);
      
      // Default options for elderly users
      utterance.rate = options.rate || 0.8; // Slower speech
      utterance.pitch = options.pitch || 1.0;
      utterance.volume = options.volume || 0.9;
      utterance.lang = options.lang || 'en-US';

      // Try to use a female voice if available (often more comforting)
      const voices = this.synthesis.getVoices();
      const preferredVoice = voices.find(voice => 
        voice.lang.startsWith('en') && voice.name.toLowerCase().includes('female')
      ) || voices.find(voice => voice.lang.startsWith('en')) || voices[0];

      if (preferredVoice) {
        utterance.voice = preferredVoice;
      }

      utterance.onend = () => resolve();
      utterance.onerror = (event) => reject(new Error(`Speech synthesis error: ${event.error}`));

      this.synthesis.speak(utterance);
    });
  }

  public stopSpeaking(): void {
    if (this.synthesis) {
      this.synthesis.cancel();
    }
  }

  public getAvailableVoices(): SpeechSynthesisVoice[] {
    if (!this.synthesis) return [];
    return this.synthesis.getVoices();
  }

  public isVoiceSupported(): boolean {
    return this.isSupported;
  }

  public isSpeechSynthesisSupported(): boolean {
    return !!this.synthesis;
  }

  // Request microphone permission
  public async requestMicrophonePermission(): Promise<boolean> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      // Close the stream immediately, we just needed to check permission
      stream.getTracks().forEach(track => track.stop());
      return true;
    } catch (error) {
      console.error('Microphone permission denied:', error);
      return false;
    }
  }

  // Check if microphone is available
  public async isMicrophoneAvailable(): Promise<boolean> {
    try {
      const devices = await navigator.mediaDevices.enumerateDevices();
      return devices.some(device => device.kind === 'audioinput');
    } catch (error) {
      console.error('Error checking microphone availability:', error);
      return false;
    }
  }

  // Voice activity detection
  public createVoiceActivityDetector(
    onVoiceStart: () => void,
    onVoiceEnd: () => void,
    threshold: number = 0.01
  ): Promise<() => void> {
    return new Promise(async (resolve, reject) => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        const audioContext = new AudioContext();
        const analyser = audioContext.createAnalyser();
        const microphone = audioContext.createMediaStreamSource(stream);
        const dataArray = new Uint8Array(analyser.frequencyBinCount);

        microphone.connect(analyser);
        analyser.fftSize = 256;

        let isVoiceActive = false;
        let silenceStart = 0;
        const silenceThreshold = 1000; // 1 second of silence

        const checkAudioLevel = () => {
          analyser.getByteFrequencyData(dataArray);
          const average = dataArray.reduce((sum, value) => sum + value, 0) / dataArray.length;
          const normalizedLevel = average / 255;

          if (normalizedLevel > threshold) {
            if (!isVoiceActive) {
              isVoiceActive = true;
              onVoiceStart();
            }
            silenceStart = Date.now();
          } else if (isVoiceActive && Date.now() - silenceStart > silenceThreshold) {
            isVoiceActive = false;
            onVoiceEnd();
          }

          requestAnimationFrame(checkAudioLevel);
        };

        checkAudioLevel();

        // Return cleanup function
        resolve(() => {
          stream.getTracks().forEach(track => track.stop());
          audioContext.close();
        });
      } catch (error) {
        reject(error);
      }
    });
  }
}

// Interface for speech recognition (for TypeScript)
interface SpeechRecognitionOptions {
  continuous?: boolean;
  interimResults?: boolean;
  lang?: string;
  maxAlternatives?: number;
}

interface SpeechSynthesisUtteranceOptions {
  rate?: number;
  pitch?: number;
  volume?: number;
  lang?: string;
  voice?: SpeechSynthesisVoice;
}

// Extend Window interface for speech recognition
declare global {
  interface Window {
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export const voiceService = new VoiceService();
export default voiceService;