// User types
export interface User {
  id: string;
  name: string;
  age: number;
  conditions: string[];
  interests: string[];
  createdAt: string;
  updatedAt: string;
  role: 'elderly' | 'family' | 'caregiver';
  profileImage?: string;
  emergencyContacts?: EmergencyContact[];
}

export interface EmergencyContact {
  id: string;
  name: string;
  relationship: string;
  phone: string;
  isPrimary: boolean;
}

// Chat types
export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'ai';
  timestamp: string;
  type: 'text' | 'voice';
  metadata?: {
    emotion?: string;
    category?: string;
    important?: boolean;
  };
}

export interface ChatSession {
  id: string;
  userId: string;
  messages: ChatMessage[];
  startedAt: string;
  lastActivity: string;
  summary?: string;
}

// Memory types
export interface Memory {
  id: string;
  userId: string;
  content: string;
  type: 'interaction' | 'health' | 'emotion' | 'event' | 'preference';
  tags: string[];
  timestamp: string;
  retention: 'active' | 'archive';
  importance: number;
  relatedMemories?: string[];
}

export interface MemorySearch {
  query: string;
  filters: {
    type?: Memory['type'];
    tags?: string[];
    dateRange?: {
      start: string;
      end: string;
    };
  };
}

// Health types
export interface HealthMetric {
  id: string;
  userId: string;
  type: 'mood' | 'pain' | 'energy' | 'sleep' | 'medication';
  value: number | string;
  timestamp: string;
  notes?: string;
}

export interface MoodEntry {
  id: string;
  userId: string;
  mood: 1 | 2 | 3 | 4 | 5; // 1 = very sad, 5 = very happy
  emotions: string[];
  timestamp: string;
  context?: string;
}

export interface MedicationReminder {
  id: string;
  userId: string;
  name: string;
  dosage: string;
  frequency: string;
  times: string[]; // Array of time strings like "08:00", "20:00"
  isActive: boolean;
  notes?: string;
}

// Family types
export interface FamilyMember {
  id: string;
  name: string;
  relationship: string;
  email: string;
  phone?: string;
  permissions: FamilyPermissions;
  connectedUsers: string[]; // User IDs they can monitor
}

export interface FamilyPermissions {
  viewConversations: boolean;
  viewHealthData: boolean;
  receiveAlerts: boolean;
  manageSettings: boolean;
}

export interface FamilyAlert {
  id: string;
  type: 'health_concern' | 'medication_missed' | 'emergency' | 'milestone';
  userId: string;
  message: string;
  timestamp: string;
  isRead: boolean;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

// Navigation types
export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
  requiresAuth?: boolean;
}

// API types
export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatRequest {
  message: string;
  userId: string;
  sessionId?: string;
  type?: 'text' | 'voice';
}

export interface ChatResponse {
  response: string;
  sessionId: string;
  responseTimeMs: number;
  contextSummary: {
    profileLoaded: boolean;
    recentInteractionsCount: number;
    relevantMemoriesCount: number;
    recentFragmentsCount: number;
  };
}

// UI State types
export interface AppState {
  user: User | null;
  isAuthenticated: boolean;
  currentSession: ChatSession | null;
  isLoading: boolean;
  error: string | null;
  preferences: UserPreferences;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'high-contrast';
  fontSize: 'small' | 'medium' | 'large' | 'extra-large';
  voiceEnabled: boolean;
  notificationsEnabled: boolean;
  language: string;
  accessibilityMode: boolean;
}

// Voice types
export interface VoiceState {
  isListening: boolean;
  isProcessing: boolean;
  transcript: string;
  confidence: number;
  error: string | null;
}

// Modal types
export interface ModalState {
  isOpen: boolean;
  type: 'emergency' | 'medication' | 'mood' | 'memory' | 'help' | null;
  data?: any;
}

// Form types
export interface ContactForm {
  name: string;
  age: number;
  conditions: string[];
  interests: string[];
  emergencyContacts: Omit<EmergencyContact, 'id'>[];
}

export interface MoodForm {
  mood: number;
  emotions: string[];
  notes?: string;
}

export interface FeedbackForm {
  type: 'bug' | 'suggestion' | 'compliment';
  message: string;
  includeScreenshot: boolean;
}

// Analytics types
export interface UserAnalytics {
  userId: string;
  totalConversations: number;
  averageSessionLength: number;
  mostActiveTime: string;
  moodTrends: MoodEntry[];
  healthMetrics: HealthMetric[];
  engagementScore: number;
}

// Error types
export interface AppError {
  code: string;
  message: string;
  details?: any;
  timestamp: string;
  userId?: string;
}