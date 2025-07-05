import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ChatInput } from '../../../components/chat/ChatInput';

// Mock the hooks
jest.mock('../../../hooks/useVoice', () => ({
  useVoice: () => ({
    isListening: false,
    isProcessing: false,
    transcript: '',
    error: null,
    isSupported: true,
    startVoiceRecognition: jest.fn().mockResolvedValue(true),
    stopVoiceRecognition: jest.fn(),
    reset: jest.fn(),
  }),
}));

// Mock framer-motion
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('ChatInput Component', () => {
  const mockOnSendMessage = jest.fn();
  const mockOnSendVoiceMessage = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders in text mode by default', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    expect(screen.getByPlaceholderText('Type your message or tap the microphone to speak...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send message' })).toBeInTheDocument();
  });

  it('sends text message on button click', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    const textarea = screen.getByPlaceholderText('Type your message or tap the microphone to speak...');
    const sendButton = screen.getByRole('button', { name: 'Send message' });

    fireEvent.change(textarea, { target: { value: 'Hello world' } });
    fireEvent.click(sendButton);

    expect(mockOnSendMessage).toHaveBeenCalledWith('Hello world');
    expect(textarea).toHaveValue('');
  });

  it('sends message on Enter key', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    const textarea = screen.getByPlaceholderText('Type your message or tap the microphone to speak...');

    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.keyPress(textarea, { key: 'Enter', shiftKey: false });

    expect(mockOnSendMessage).toHaveBeenCalledWith('Test message');
  });

  it('does not send message on Shift+Enter', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    const textarea = screen.getByPlaceholderText('Type your message or tap the microphone to speak...');

    fireEvent.change(textarea, { target: { value: 'Test message' } });
    fireEvent.keyPress(textarea, { key: 'Enter', shiftKey: true });

    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it('does not send empty messages', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    const sendButton = screen.getByRole('button', { name: 'Send message' });

    fireEvent.click(sendButton);
    expect(mockOnSendMessage).not.toHaveBeenCalled();

    // Try with whitespace only
    const textarea = screen.getByPlaceholderText('Type your message or tap the microphone to speak...');
    fireEvent.change(textarea, { target: { value: '   ' } });
    fireEvent.click(sendButton);
    expect(mockOnSendMessage).not.toHaveBeenCalled();
  });

  it('shows character count', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
        maxLength={500}
      />
    );

    expect(screen.getByText('0/500')).toBeInTheDocument();

    const textarea = screen.getByPlaceholderText('Type your message or tap the microphone to speak...');
    fireEvent.change(textarea, { target: { value: 'Hello' } });

    expect(screen.getByText('5/500')).toBeInTheDocument();
  });

  it('respects maxLength prop', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
        maxLength={10}
      />
    );

    const textarea = screen.getByPlaceholderText('Type your message or tap the microphone to speak...') as HTMLTextAreaElement;
    expect(textarea).toHaveAttribute('maxLength', '10');
  });

  it('disables input when disabled prop is true', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
        disabled={true}
      />
    );

    const textarea = screen.getByPlaceholderText('Type your message or tap the microphone to speak...');
    const sendButton = screen.getByRole('button', { name: 'Send message' });

    expect(textarea).toBeDisabled();
    expect(sendButton).toBeDisabled();
  });

  it('switches between text and voice modes', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Initially in text mode
    expect(screen.getByPlaceholderText('Type your message or tap the microphone to speak...')).toBeInTheDocument();

    // Click on Speak button
    const speakModeButton = screen.getByText('Speak');
    fireEvent.click(speakModeButton);

    // Should switch to voice mode
    expect(screen.getByText('Tap to speak')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Start listening' })).toBeInTheDocument();

    // Click on Type button
    const typeModeButton = screen.getByText('Type instead');
    fireEvent.click(typeModeButton);

    // Should switch back to text mode
    expect(screen.getByPlaceholderText('Type your message or tap the microphone to speak...')).toBeInTheDocument();
  });

  it('shows voice recording interface in voice mode', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Switch to voice mode
    fireEvent.click(screen.getByText('Speak'));

    expect(screen.getByText('Tap to speak')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Start listening' })).toBeInTheDocument();
    expect(screen.getByText('Start')).toBeInTheDocument();
  });

  it('handles voice recording lifecycle', async () => {
    const { useVoice } = require('../../../hooks/useVoice');
    const mockStartVoice = jest.fn().mockResolvedValue(true);
    const mockStopVoice = jest.fn();
    
    useVoice.mockReturnValue({
      isListening: false,
      isProcessing: false,
      transcript: '',
      error: null,
      isSupported: true,
      startVoiceRecognition: mockStartVoice,
      stopVoiceRecognition: mockStopVoice,
      reset: jest.fn(),
    });

    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Switch to voice mode
    fireEvent.click(screen.getByText('Speak'));

    // Start recording
    const startButton = screen.getByRole('button', { name: 'Start listening' });
    fireEvent.click(startButton);

    await waitFor(() => {
      expect(mockStartVoice).toHaveBeenCalled();
    });
  });

  it('shows listening state correctly', () => {
    const { useVoice } = require('../../../hooks/useVoice');
    useVoice.mockReturnValue({
      isListening: true,
      isProcessing: false,
      transcript: '',
      error: null,
      isSupported: true,
      startVoiceRecognition: jest.fn(),
      stopVoiceRecognition: jest.fn(),
      reset: jest.fn(),
    });

    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Switch to voice mode
    fireEvent.click(screen.getByText('Speak'));

    expect(screen.getByText('Listening...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Stop listening' })).toBeInTheDocument();
    expect(screen.getByText('Stop')).toBeInTheDocument();
  });

  it('shows processing state correctly', () => {
    const { useVoice } = require('../../../hooks/useVoice');
    useVoice.mockReturnValue({
      isListening: false,
      isProcessing: true,
      transcript: '',
      error: null,
      isSupported: true,
      startVoiceRecognition: jest.fn(),
      stopVoiceRecognition: jest.fn(),
      reset: jest.fn(),
    });

    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Switch to voice mode
    fireEvent.click(screen.getByText('Speak'));

    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  it('displays voice transcript', () => {
    const { useVoice } = require('../../../hooks/useVoice');
    useVoice.mockReturnValue({
      isListening: false,
      isProcessing: false,
      transcript: 'Hello from voice',
      error: null,
      isSupported: true,
      startVoiceRecognition: jest.fn(),
      stopVoiceRecognition: jest.fn(),
      reset: jest.fn(),
    });

    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Switch to voice mode
    fireEvent.click(screen.getByText('Speak'));

    expect(screen.getByText('"Hello from voice"')).toBeInTheDocument();
  });

  it('displays voice errors', () => {
    const { useVoice } = require('../../../hooks/useVoice');
    useVoice.mockReturnValue({
      isListening: false,
      isProcessing: false,
      transcript: '',
      error: 'Microphone access denied',
      isSupported: true,
      startVoiceRecognition: jest.fn(),
      stopVoiceRecognition: jest.fn(),
      reset: jest.fn(),
    });

    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Switch to voice mode
    fireEvent.click(screen.getByText('Speak'));

    expect(screen.getByText('Microphone access denied')).toBeInTheDocument();
  });

  it('handles voice not supported', () => {
    const { useVoice } = require('../../../hooks/useVoice');
    useVoice.mockReturnValue({
      isListening: false,
      isProcessing: false,
      transcript: '',
      error: null,
      isSupported: false,
      startVoiceRecognition: jest.fn(),
      stopVoiceRecognition: jest.fn(),
      reset: jest.fn(),
    });

    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Voice mode button should be disabled
    const speakButton = screen.getByText('Speak');
    expect(speakButton).toBeDisabled();
    expect(speakButton).toHaveClass('opacity-50', 'cursor-not-allowed');
  });

  it('switches to text mode when clicking microphone in text mode', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
      />
    );

    // Click voice button in text mode
    const voiceButton = screen.getByRole('button', { name: 'Switch to voice input' });
    fireEvent.click(voiceButton);

    // Should be in voice mode now
    expect(screen.getByText('Tap to speak')).toBeInTheDocument();
  });

  it('uses custom placeholder', () => {
    render(
      <ChatInput
        onSendMessage={mockOnSendMessage}
        onSendVoiceMessage={mockOnSendVoiceMessage}
        placeholder="Custom placeholder text"
      />
    );

    expect(screen.getByPlaceholderText('Custom placeholder text')).toBeInTheDocument();
  });
});