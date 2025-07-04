import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { AppState, User, ChatSession, UserPreferences, VoiceState, ModalState } from '../types';

// Main app store
interface AppStore extends AppState {
  // Actions
  setUser: (user: User | null) => void;
  setAuthenticated: (isAuthenticated: boolean) => void;
  setCurrentSession: (session: ChatSession | null) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  updatePreferences: (preferences: Partial<UserPreferences>) => void;
  logout: () => void;
}

export const useAppStore = create<AppStore>()(
  persist(
    (set, get) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      currentSession: null,
      isLoading: false,
      error: null,
      preferences: {
        theme: 'light',
        fontSize: 'large',
        voiceEnabled: true,
        notificationsEnabled: true,
        language: 'en',
        accessibilityMode: false,
      },

      // Actions
      setUser: (user) => set({ user }),
      setAuthenticated: (isAuthenticated) => set({ isAuthenticated }),
      setCurrentSession: (session) => set({ currentSession: session }),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      updatePreferences: (newPreferences) =>
        set((state) => ({
          preferences: { ...state.preferences, ...newPreferences },
        })),
      logout: () =>
        set({
          user: null,
          isAuthenticated: false,
          currentSession: null,
          error: null,
        }),
    }),
    {
      name: 'elderwise-app-store',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
        preferences: state.preferences,
      }),
    }
  )
);

// Voice store
interface VoiceStore extends VoiceState {
  // Actions
  startListening: () => void;
  stopListening: () => void;
  setProcessing: (isProcessing: boolean) => void;
  setTranscript: (transcript: string) => void;
  setConfidence: (confidence: number) => void;
  setError: (error: string | null) => void;
  resetVoice: () => void;
}

export const useVoiceStore = create<VoiceStore>((set) => ({
  // Initial state
  isListening: false,
  isProcessing: false,
  transcript: '',
  confidence: 0,
  error: null,

  // Actions
  startListening: () => set({ isListening: true, error: null }),
  stopListening: () => set({ isListening: false }),
  setProcessing: (isProcessing) => set({ isProcessing }),
  setTranscript: (transcript) => set({ transcript }),
  setConfidence: (confidence) => set({ confidence }),
  setError: (error) => set({ error, isListening: false, isProcessing: false }),
  resetVoice: () =>
    set({
      isListening: false,
      isProcessing: false,
      transcript: '',
      confidence: 0,
      error: null,
    }),
}));

// Modal store
interface ModalStore extends ModalState {
  // Actions
  openModal: (type: ModalState['type'], data?: any) => void;
  closeModal: () => void;
}

export const useModalStore = create<ModalStore>((set) => ({
  // Initial state
  isOpen: false,
  type: null,
  data: null,

  // Actions
  openModal: (type, data) => set({ isOpen: true, type, data }),
  closeModal: () => set({ isOpen: false, type: null, data: null }),
}));

// Chat store
interface ChatStore {
  messages: ChatMessage[];
  isTyping: boolean;
  sessionId: string | null;
  
  // Actions
  addMessage: (message: ChatMessage) => void;
  setMessages: (messages: ChatMessage[]) => void;
  setTyping: (isTyping: boolean) => void;
  setSessionId: (sessionId: string | null) => void;
  clearMessages: () => void;
}

import { ChatMessage } from '../types';

export const useChatStore = create<ChatStore>((set) => ({
  // Initial state
  messages: [],
  isTyping: false,
  sessionId: null,

  // Actions
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  setMessages: (messages) => set({ messages }),
  setTyping: (isTyping) => set({ isTyping }),
  setSessionId: (sessionId) => set({ sessionId }),
  clearMessages: () => set({ messages: [], sessionId: null }),
}));

// Navigation store
interface NavigationStore {
  currentRoute: string;
  previousRoute: string | null;
  canGoBack: boolean;
  
  // Actions
  setCurrentRoute: (route: string) => void;
  goBack: () => void;
}

export const useNavigationStore = create<NavigationStore>((set, get) => ({
  // Initial state
  currentRoute: '/',
  previousRoute: null,
  canGoBack: false,

  // Actions
  setCurrentRoute: (route) =>
    set((state) => ({
      previousRoute: state.currentRoute,
      currentRoute: route,
      canGoBack: true,
    })),
  goBack: () => {
    const { previousRoute } = get();
    if (previousRoute) {
      set((state) => ({
        currentRoute: previousRoute,
        previousRoute: null,
        canGoBack: false,
      }));
    }
  },
}));