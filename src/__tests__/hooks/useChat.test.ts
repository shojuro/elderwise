import { renderHook, act, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useChat } from '../../hooks/useChat';
import { apiService } from '../../services/api';
import { useChatStore, useAppStore } from '../../store';

// Mock dependencies
jest.mock('../../services/api');
jest.mock('../../store');
jest.mock('uuid', () => ({ v4: () => 'mock-uuid' }));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useChat Hook', () => {
  const mockUser = { id: 'test-user', name: 'Test User' };
  const mockAddMessage = jest.fn();
  const mockSetTyping = jest.fn();
  const mockSetSessionId = jest.fn();
  const mockClearMessages = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock store values
    (useAppStore as jest.Mock).mockReturnValue({ user: mockUser });
    (useChatStore as jest.Mock).mockReturnValue({
      messages: [],
      isTyping: false,
      sessionId: null,
      addMessage: mockAddMessage,
      setTyping: mockSetTyping,
      setSessionId: mockSetSessionId,
      clearMessages: mockClearMessages,
    });
  });

  it('initializes with correct default state', () => {
    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    expect(result.current.messages).toEqual([]);
    expect(result.current.isTyping).toBe(false);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.isConnected).toBe(true);
    expect(result.current.sessionId).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('sends a message successfully', async () => {
    const mockResponse = {
      response: 'AI response',
      session_id: 'session-123',
      response_time_ms: 150,
      context_summary: { relevant_memories_count: 2 },
    };

    (apiService.sendMessage as jest.Mock).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    await act(async () => {
      result.current.sendMessage('Hello AI');
    });

    await waitFor(() => {
      expect(mockAddMessage).toHaveBeenCalledTimes(2);
    });

    // Verify user message was added
    expect(mockAddMessage).toHaveBeenNthCalledWith(1, {
      id: 'mock-uuid',
      content: 'Hello AI',
      sender: 'user',
      timestamp: expect.any(String),
      type: 'text',
    });

    // Verify typing state was set
    expect(mockSetTyping).toHaveBeenCalledWith(true);

    // Verify API call
    expect(apiService.sendMessage).toHaveBeenCalledWith({
      message: 'Hello AI',
      userId: 'test-user',
      sessionId: undefined,
      type: 'text',
    });

    // Verify AI response was added
    expect(mockAddMessage).toHaveBeenNthCalledWith(2, {
      id: 'mock-uuid',
      content: 'AI response',
      sender: 'ai',
      timestamp: expect.any(String),
      type: 'text',
      metadata: {
        category: 'response',
        important: true,
        responseTimeMs: 150,
      },
    });

    // Verify session ID was set
    expect(mockSetSessionId).toHaveBeenCalledWith('session-123');

    // Verify typing state was cleared
    expect(mockSetTyping).toHaveBeenLastCalledWith(false);
  });

  it('handles message sending error', async () => {
    const mockError = new Error('Network error');
    (apiService.sendMessage as jest.Mock).mockRejectedValue(mockError);

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    await act(async () => {
      result.current.sendMessage('Hello AI');
    });

    await waitFor(() => {
      expect(mockAddMessage).toHaveBeenCalledTimes(2);
    });

    // Verify error message was added
    expect(mockAddMessage).toHaveBeenNthCalledWith(2, {
      id: 'mock-uuid',
      content: "I'm sorry, I'm having trouble responding right now. Please try again.",
      sender: 'ai',
      timestamp: expect.any(String),
      type: 'text',
      metadata: {
        category: 'error',
      },
    });

    // Verify typing state was cleared
    expect(mockSetTyping).toHaveBeenLastCalledWith(false);
  });

  it('sends voice message', async () => {
    const mockResponse = {
      response: 'Voice response',
      session_id: 'session-123',
      response_time_ms: 200,
    };

    (apiService.sendMessage as jest.Mock).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    await act(async () => {
      await result.current.sendVoiceMessage('Voice transcript');
    });

    await waitFor(() => {
      expect(apiService.sendMessage).toHaveBeenCalled();
    });

    expect(apiService.sendMessage).toHaveBeenCalledWith({
      message: 'Voice transcript',
      userId: 'test-user',
      sessionId: undefined,
      type: 'text',
    });
  });

  it('does not send empty voice message', async () => {
    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    await act(async () => {
      await result.current.sendVoiceMessage('   ');
    });

    expect(apiService.sendMessage).not.toHaveBeenCalled();
  });

  it('clears conversation', () => {
    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    act(() => {
      result.current.clearConversation();
    });

    expect(mockClearMessages).toHaveBeenCalled();
  });

  it('gets conversation summary', () => {
    const mockMessages = [
      { id: '1', sender: 'user', content: 'Hello' },
      { id: '2', sender: 'ai', content: 'Hi there' },
      { id: '3', sender: 'user', content: 'How are you?' },
    ];

    (useChatStore as jest.Mock).mockReturnValue({
      messages: mockMessages,
      isTyping: false,
      sessionId: 'session-123',
      addMessage: mockAddMessage,
      setTyping: mockSetTyping,
      setSessionId: mockSetSessionId,
      clearMessages: mockClearMessages,
    });

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    const summary = result.current.getConversationSummary();

    expect(summary).toEqual({
      totalMessages: 3,
      userMessages: 2,
      aiMessages: 1,
      lastMessage: mockMessages[2],
      sessionId: 'session-123',
    });
  });

  it('retries last user message', async () => {
    const mockMessages = [
      { id: '1', sender: 'user', content: 'First message', timestamp: '2024-01-01T10:00:00Z' },
      { id: '2', sender: 'ai', content: 'Response', timestamp: '2024-01-01T10:00:01Z' },
      { id: '3', sender: 'user', content: 'Last message', timestamp: '2024-01-01T10:00:02Z' },
    ];

    (useChatStore as jest.Mock).mockReturnValue({
      messages: mockMessages,
      isTyping: false,
      sessionId: null,
      addMessage: mockAddMessage,
      setTyping: mockSetTyping,
      setSessionId: mockSetSessionId,
      clearMessages: mockClearMessages,
    });

    const mockResponse = {
      response: 'Retry response',
      session_id: 'session-123',
      response_time_ms: 150,
    };

    (apiService.sendMessage as jest.Mock).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    await act(async () => {
      result.current.retryLastMessage();
    });

    await waitFor(() => {
      expect(apiService.sendMessage).toHaveBeenCalled();
    });

    expect(apiService.sendMessage).toHaveBeenCalledWith({
      message: 'Last message',
      userId: 'test-user',
      sessionId: undefined,
      type: 'text',
    });
  });

  it('does not retry if no user messages', () => {
    const mockMessages = [
      { id: '1', sender: 'ai', content: 'AI message' },
    ];

    (useChatStore as jest.Mock).mockReturnValue({
      messages: mockMessages,
      isTyping: false,
      sessionId: null,
      addMessage: mockAddMessage,
      setTyping: mockSetTyping,
      setSessionId: mockSetSessionId,
      clearMessages: mockClearMessages,
    });

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    act(() => {
      result.current.retryLastMessage();
    });

    expect(apiService.sendMessage).not.toHaveBeenCalled();
  });

  it('throws error when user is not authenticated', async () => {
    (useAppStore as jest.Mock).mockReturnValue({ user: null });

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    await expect(async () => {
      await act(async () => {
        result.current.sendMessage('Hello');
      });
    }).rejects.toThrow();
  });

  it('handles streaming messages', async () => {
    const mockEventSource = {
      onmessage: null as any,
      onerror: null as any,
      close: jest.fn(),
    };

    (apiService.sendMessageStream as jest.Mock).mockResolvedValue(mockEventSource);

    const { result } = renderHook(() => useChat(), { wrapper: createWrapper() });

    await act(async () => {
      await result.current.sendStreamingMessage('Stream this');
    });

    // Verify user message was added
    expect(mockAddMessage).toHaveBeenCalledWith({
      id: 'mock-uuid',
      content: 'Stream this',
      sender: 'user',
      timestamp: expect.any(String),
      type: 'text',
    });

    // Verify typing state was set
    expect(mockSetTyping).toHaveBeenCalledWith(true);

    // Simulate streaming messages
    act(() => {
      mockEventSource.onmessage({ data: 'Hello ' });
      mockEventSource.onmessage({ data: 'world!' });
      mockEventSource.onmessage({ data: '[DONE]' });
    });

    expect(mockEventSource.close).toHaveBeenCalled();
    expect(mockSetTyping).toHaveBeenLastCalledWith(false);
  });
});