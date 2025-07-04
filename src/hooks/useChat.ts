import { useState, useCallback } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useChatStore, useAppStore } from '../store';
import { apiService } from '../services/api';
import { ChatMessage, ChatRequest } from '../types';
import { v4 as uuidv4 } from 'uuid';

export const useChat = () => {
  const { user } = useAppStore();
  const { 
    messages, 
    isTyping, 
    sessionId, 
    addMessage, 
    setTyping, 
    setSessionId,
    clearMessages 
  } = useChatStore();
  
  const [isConnected, setIsConnected] = useState(true);

  // Send message mutation
  const sendMessageMutation = useMutation({
    mutationFn: async (message: string) => {
      if (!user) throw new Error('User not authenticated');

      const userMessage: ChatMessage = {
        id: uuidv4(),
        content: message,
        sender: 'user',
        timestamp: new Date().toISOString(),
        type: 'text',
      };

      // Add user message immediately
      addMessage(userMessage);
      setTyping(true);

      const request: ChatRequest = {
        message,
        userId: user.id,
        sessionId: sessionId || undefined,
        type: 'text',
      };

      const response = await apiService.sendMessage(request);
      return response;
    },
    onSuccess: (data) => {
      if (data) {
        // Update session ID if new
        if (data.session_id && data.session_id !== sessionId) {
          setSessionId(data.session_id);
        }

        // Add AI response
        const aiMessage: ChatMessage = {
          id: uuidv4(),
          content: data.response,
          sender: 'ai',
          timestamp: new Date().toISOString(),
          type: 'text',
          metadata: {
            category: 'response',
            important: data.context_summary?.relevant_memories_count > 0,
            responseTimeMs: data.response_time_ms,
          },
        };

        addMessage(aiMessage);
      }
      setTyping(false);
    },
    onError: (error) => {
      console.error('Failed to send message:', error);
      
      // Add error message
      const errorMessage: ChatMessage = {
        id: uuidv4(),
        content: "I'm sorry, I'm having trouble responding right now. Please try again.",
        sender: 'ai',
        timestamp: new Date().toISOString(),
        type: 'text',
        metadata: {
          category: 'error',
        },
      };

      addMessage(errorMessage);
      setTyping(false);
    },
  });

  // Send voice message
  const sendVoiceMessage = useCallback(async (transcript: string) => {
    if (!transcript.trim()) return;

    try {
      await sendMessageMutation.mutateAsync(transcript);
    } catch (error) {
      console.error('Failed to send voice message:', error);
    }
  }, [sendMessageMutation]);

  // Streaming message functionality
  const sendStreamingMessage = useCallback(async (message: string) => {
    if (!user) throw new Error('User not authenticated');

    const userMessage: ChatMessage = {
      id: uuidv4(),
      content: message,
      sender: 'user',
      timestamp: new Date().toISOString(),
      type: 'text',
    };

    // Add user message immediately
    addMessage(userMessage);
    setTyping(true);

    try {
      const request: ChatRequest = {
        message,
        userId: user.id,
        sessionId: sessionId || undefined,
        type: 'text',
      };

      const eventSource = await apiService.sendMessageStream(request);
      let aiResponseContent = '';
      const aiMessageId = uuidv4();

      eventSource.onmessage = (event) => {
        const data = event.data;
        
        if (data === '[DONE]') {
          eventSource.close();
          setTyping(false);
          return;
        }

        aiResponseContent += data;

        // Update the AI message in real-time
        const aiMessage: ChatMessage = {
          id: aiMessageId,
          content: aiResponseContent,
          sender: 'ai',
          timestamp: new Date().toISOString(),
          type: 'text',
        };

        // Check if this message already exists, update or add
        const existingMessageIndex = messages.findIndex(msg => msg.id === aiMessageId);
        if (existingMessageIndex >= 0) {
          // Update existing message
          const updatedMessages = [...messages];
          updatedMessages[existingMessageIndex] = aiMessage;
          // This would need a setMessages action in the store
        } else {
          // Add new message
          addMessage(aiMessage);
        }
      };

      eventSource.onerror = (error) => {
        console.error('Streaming error:', error);
        eventSource.close();
        setTyping(false);
        setIsConnected(false);
      };

    } catch (error) {
      console.error('Failed to start streaming:', error);
      setTyping(false);
    }
  }, [user, sessionId, messages, addMessage, setTyping]);

  // Clear conversation
  const clearConversation = useCallback(() => {
    clearMessages();
  }, [clearMessages]);

  // Get conversation summary
  const getConversationSummary = useCallback(() => {
    const totalMessages = messages.length;
    const userMessages = messages.filter(msg => msg.sender === 'user').length;
    const aiMessages = messages.filter(msg => msg.sender === 'ai').length;
    const lastMessage = messages[messages.length - 1];

    return {
      totalMessages,
      userMessages,
      aiMessages,
      lastMessage,
      sessionId,
    };
  }, [messages, sessionId]);

  // Retry last message
  const retryLastMessage = useCallback(() => {
    const lastUserMessage = [...messages]
      .reverse()
      .find(msg => msg.sender === 'user');

    if (lastUserMessage) {
      sendMessageMutation.mutate(lastUserMessage.content);
    }
  }, [messages, sendMessageMutation]);

  return {
    // State
    messages,
    isTyping,
    isLoading: sendMessageMutation.isPending,
    isConnected,
    sessionId,
    
    // Actions
    sendMessage: sendMessageMutation.mutate,
    sendVoiceMessage,
    sendStreamingMessage,
    clearConversation,
    retryLastMessage,
    
    // Utils
    getConversationSummary,
    
    // Error state
    error: sendMessageMutation.error?.message || null,
  };
};