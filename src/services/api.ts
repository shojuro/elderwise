import axios, { AxiosInstance, AxiosError } from 'axios';
import { 
  APIResponse, 
  ChatRequest, 
  ChatResponse, 
  User, 
  Memory, 
  MemorySearch, 
  HealthMetric,
  MoodEntry,
  FamilyAlert 
} from '../types';

class APIService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for auth
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('elderwise-token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.api.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('elderwise-token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Authentication
  async login(credentials: { username: string; password: string }): Promise<APIResponse<{ user: User; token: string }>> {
    try {
      const response = await this.api.post('/auth/login', credentials);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async logout(): Promise<APIResponse> {
    try {
      const response = await this.api.post('/auth/logout');
      localStorage.removeItem('elderwise-token');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // User management
  async createUser(userData: {
    user_id: string;
    name: string;
    age: number;
    conditions?: string[];
    interests?: string[];
  }): Promise<APIResponse<any>> {
    try {
      const response = await this.api.post('/users/create', userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getUser(userId: string): Promise<APIResponse<User>> {
    try {
      const response = await this.api.get(`/users/${userId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async updateUser(userId: string, userData: {
    name?: string;
    age?: number;
    conditions?: string[];
    interests?: string[];
  }): Promise<APIResponse<any>> {
    try {
      const response = await this.api.put(`/users/${userId}`, userData);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getUserStats(userId: string): Promise<APIResponse<any>> {
    try {
      const response = await this.api.get(`/users/${userId}/stats`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Chat functionality
  async sendMessage(request: ChatRequest): Promise<APIResponse<ChatResponse>> {
    try {
      const response = await this.api.post('/ai/respond', {
        user_id: request.userId,
        message: request.message,
        session_id: request.sessionId,
        temperature: 0.7,
        max_tokens: 500,
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async sendMessageStream(request: ChatRequest): Promise<EventSource> {
    const params = new URLSearchParams({
      user_id: request.userId,
      message: request.message,
      session_id: request.sessionId || '',
    });

    const eventSource = new EventSource(
      `${this.api.defaults.baseURL}/ai/respond/stream?${params}`
    );

    return eventSource;
  }

  async validateSystem(): Promise<APIResponse<any>> {
    try {
      const response = await this.api.get('/ai/validate');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Memory management
  async createMemory(memory: Partial<Memory>): Promise<APIResponse<Memory>> {
    try {
      const response = await this.api.post('/memory/create', memory);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async searchMemories(searchParams: MemorySearch): Promise<APIResponse<Memory[]>> {
    try {
      const response = await this.api.post('/memory/search', searchParams);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getRecentMemories(userId: string, limit: number = 20): Promise<APIResponse<Memory[]>> {
    try {
      const response = await this.api.get(`/memory/${userId}/recent?limit=${limit}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getSessionHistory(userId: string): Promise<APIResponse<any[]>> {
    try {
      const response = await this.api.get(`/memory/${userId}/session`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async archiveMemories(): Promise<APIResponse<any>> {
    try {
      const response = await this.api.post('/memory/archive');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Health tracking
  async addHealthMetric(metric: Partial<HealthMetric>): Promise<APIResponse<HealthMetric>> {
    try {
      const response = await this.api.post('/health/metrics', metric);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getHealthMetrics(userId: string, type?: string, days?: number): Promise<APIResponse<HealthMetric[]>> {
    try {
      const params = new URLSearchParams();
      if (type) params.append('type', type);
      if (days) params.append('days', days.toString());
      
      const response = await this.api.get(`/health/${userId}/metrics?${params}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async addMoodEntry(mood: Partial<MoodEntry>): Promise<APIResponse<MoodEntry>> {
    try {
      const response = await this.api.post('/health/mood', mood);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getMoodHistory(userId: string, days: number = 30): Promise<APIResponse<MoodEntry[]>> {
    try {
      const response = await this.api.get(`/health/${userId}/mood?days=${days}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Family features
  async getFamilyAlerts(familyMemberId: string): Promise<APIResponse<FamilyAlert[]>> {
    try {
      const response = await this.api.get(`/family/${familyMemberId}/alerts`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async markAlertAsRead(alertId: string): Promise<APIResponse<any>> {
    try {
      const response = await this.api.patch(`/family/alerts/${alertId}/read`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getUserSummary(userId: string): Promise<APIResponse<any>> {
    try {
      const response = await this.api.get(`/family/users/${userId}/summary`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Emergency features
  async triggerEmergencyAlert(userId: string, type: string): Promise<APIResponse<any>> {
    try {
      const response = await this.api.post('/emergency/alert', {
        userId,
        type,
        timestamp: new Date().toISOString(),
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  async getEmergencyContacts(userId: string): Promise<APIResponse<any[]>> {
    try {
      const response = await this.api.get(`/emergency/${userId}/contacts`);
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Health check
  async healthCheck(): Promise<APIResponse<any>> {
    try {
      const response = await this.api.get('/health');
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // File upload
  async uploadFile(file: File, type: string): Promise<APIResponse<{ url: string }>> {
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const response = await this.api.post('/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error);
    }
  }

  // Error handling
  private handleError(error: any): Error {
    if (error.response) {
      // Server responded with error status
      const message = error.response.data?.message || error.response.statusText;
      return new Error(`API Error: ${message}`);
    } else if (error.request) {
      // Request was made but no response received
      return new Error('Network Error: Unable to reach server');
    } e