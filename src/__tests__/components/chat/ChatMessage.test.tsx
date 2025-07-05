import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatMessage, TypingIndicator } from '../../../components/chat/ChatMessage';
import { ChatMessage as ChatMessageType } from '../../../types';
import { formatDistanceToNow } from 'date-fns';

// Mock the hooks
jest.mock('../../../hooks/useVoice', () => ({
  useVoiceResponse: () => ({
    speakMessage: jest.fn().mockResolvedValue(undefined),
    stopSpeaking: jest.fn(),
    isEnabled: true,
  }),
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

describe('ChatMessage Component', () => {
  const mockUserMessage: ChatMessageType = {
    id: '1',
    content: 'Hello, how are you?',
    sender: 'user',
    timestamp: new Date().toISOString(),
    type: 'text',
  };

  const mockAIMessage: ChatMessageType = {
    id: '2',
    content: 'I am doing well, thank you!',
    sender: 'ai',
    timestamp: new Date().toISOString(),
    type: 'text',
  };

  const mockVoiceMessage: ChatMessageType = {
    id: '3',
    content: 'This is a voice message',
    sender: 'user',
    timestamp: new Date().toISOString(),
    type: 'voice',
  };

  it('renders user message correctly', () => {
    render(<ChatMessage message={mockUserMessage} />);
    
    expect(screen.getByText('Hello, how are you?')).toBeInTheDocument();
    expect(screen.getByText('Hello, how are you?').closest('.chat-bubble-user')).toBeInTheDocument();
  });

  it('renders AI message correctly', () => {
    render(<ChatMessage message={mockAIMessage} />);
    
    expect(screen.getByText('I am doing well, thank you!')).toBeInTheDocument();
    expect(screen.getByText('I am doing well, thank you!').closest('.chat-bubble-ai')).toBeInTheDocument();
    expect(screen.getByText('EW')).toBeInTheDocument(); // AI avatar
  });

  it('shows timestamp when enabled', () => {
    const timestamp = new Date();
    const message = { ...mockUserMessage, timestamp: timestamp.toISOString() };
    
    render(<ChatMessage message={message} showTimestamp={true} />);
    
    const expectedText = formatDistanceToNow(timestamp, { addSuffix: true });
    expect(screen.getByText(expectedText)).toBeInTheDocument();
  });

  it('hides timestamp when disabled', () => {
    render(<ChatMessage message={mockUserMessage} showTimestamp={false} />);
    
    const timestampRegex = /ago/;
    const timestamps = screen.queryAllByText(timestampRegex);
    expect(timestamps).toHaveLength(0);
  });

  it('shows voice message indicator for voice messages', () => {
    render(<ChatMessage message={mockVoiceMessage} />);
    
    expect(screen.getByText('Voice message')).toBeInTheDocument();
    expect(screen.getByText('This is a voice message')).toBeInTheDocument();
  });

  it('renders speak button for AI messages when voice is enabled', () => {
    const { useVoiceResponse } = require('../../../hooks/useVoice');
    useVoiceResponse.mockReturnValue({
      speakMessage: jest.fn(),
      stopSpeaking: jest.fn(),
      isEnabled: true,
    });

    render(<ChatMessage message={mockAIMessage} />);
    
    const speakButton = screen.getByRole('button', { name: 'Read message aloud' });
    expect(speakButton).toBeInTheDocument();
  });

  it('does not render speak button when voice is disabled', () => {
    const { useVoiceResponse } = require('../../../hooks/useVoice');
    useVoiceResponse.mockReturnValue({
      speakMessage: jest.fn(),
      stopSpeaking: jest.fn(),
      isEnabled: false,
    });

    render(<ChatMessage message={mockAIMessage} />);
    
    const speakButton = screen.queryByRole('button', { name: 'Read message aloud' });
    expect(speakButton).not.toBeInTheDocument();
  });

  it('handles speak button click', async () => {
    const mockSpeakMessage = jest.fn().mockResolvedValue(undefined);
    const { useVoiceResponse } = require('../../../hooks/useVoice');
    useVoiceResponse.mockReturnValue({
      speakMessage: mockSpeakMessage,
      stopSpeaking: jest.fn(),
      isEnabled: true,
    });

    render(<ChatMessage message={mockAIMessage} />);
    
    const speakButton = screen.getByRole('button', { name: 'Read message aloud' });
    fireEvent.click(speakButton);
    
    await waitFor(() => {
      expect(mockSpeakMessage).toHaveBeenCalledWith('I am doing well, thank you!');
    });
  });

  it('stops speaking when clicked again', async () => {
    const mockStopSpeaking = jest.fn();
    const mockSpeakMessage = jest.fn(() => new Promise(() => {})); // Never resolves
    const { useVoiceResponse } = require('../../../hooks/useVoice');
    useVoiceResponse.mockReturnValue({
      speakMessage: mockSpeakMessage,
      stopSpeaking: mockStopSpeaking,
      isEnabled: true,
    });

    render(<ChatMessage message={mockAIMessage} />);
    
    const speakButton = screen.getByRole('button', { name: 'Read message aloud' });
    fireEvent.click(speakButton);
    
    // Button should change to stop speaking
    await waitFor(() => {
      expect(screen.getByRole('button', { name: 'Stop speaking' })).toBeInTheDocument();
    });
    
    fireEvent.click(screen.getByRole('button', { name: 'Stop speaking' }));
    expect(mockStopSpeaking).toHaveBeenCalled();
  });

  it('shows error styling for error messages', () => {
    const errorMessage: ChatMessageType = {
      ...mockAIMessage,
      metadata: { category: 'error' },
    };
    
    render(<ChatMessage message={errorMessage} />);
    
    const messageBubble = screen.getByText('I am doing well, thank you!').closest('.chat-bubble-ai');
    expect(messageBubble).toHaveClass('border-coral-200', 'bg-coral-50');
  });

  it('shows important memory indicator', () => {
    const importantMessage: ChatMessageType = {
      ...mockAIMessage,
      metadata: { important: true },
    };
    
    render(<ChatMessage message={importantMessage} />);
    
    expect(screen.getByText('Important memory')).toBeInTheDocument();
  });

  it('positions user messages on the right', () => {
    render(<ChatMessage message={mockUserMessage} />);
    
    const messageContainer = screen.getByText('Hello, how are you?').closest('.flex');
    expect(messageContainer).toHaveClass('justify-end');
  });

  it('positions AI messages on the left', () => {
    render(<ChatMessage message={mockAIMessage} />);
    
    const messageContainer = screen.getByText('I am doing well, thank you!').closest('.flex');
    expect(messageContainer).toHaveClass('justify-start');
  });
});

describe('TypingIndicator Component', () => {
  it('renders typing indicator with correct text', () => {
    render(<TypingIndicator />);
    
    expect(screen.getByText('ElderWise is thinking')).toBeInTheDocument();
    expect(screen.getByText('EW')).toBeInTheDocument();
  });

  it('shows loading dots animation', () => {
    render(<TypingIndicator />);
    
    const loadingDots = document.querySelector('.loading-dots');
    expect(loadingDots).toBeInTheDocument();
    expect(loadingDots?.children).toHaveLength(3);
  });
});