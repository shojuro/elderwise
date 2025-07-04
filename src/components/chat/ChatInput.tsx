import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Mic, MicOff, Loader } from 'lucide-react';
import { Button } from '../common/Button';
import { useVoice } from '../../hooks/useVoice';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onSendVoiceMessage: (transcript: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export const ChatInput: React.FC<ChatInputProps> = ({
  onSendMessage,
  onSendVoiceMessage,
  disabled = false,
  placeholder = "Type your message or tap the microphone to speak...",
  maxLength = 500,
}) => {
  const [message, setMessage] = useState('');
  const [isTextMode, setIsTextMode] = useState(true);
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  
  const {
    isListening,
    isProcessing,
    transcript,
    error,
    isSupported,
    startVoiceRecognition,
    stopVoiceRecognition,
    reset,
  } = useVoice();

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [message]);

  // Handle voice transcript
  useEffect(() => {
    if (transcript && !isListening && !isProcessing) {
      onSendVoiceMessage(transcript);
      reset();
      setIsTextMode(true);
    }
  }, [transcript, isListening, isProcessing, onSendVoiceMessage, reset]);

  const handleSendText = () => {
    if (message.trim() && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendText();
    }
  };

  const handleVoiceToggle = async () => {
    if (!isSupported) {
      alert('Voice input is not supported in this browser');
      return;
    }

    if (isListening) {
      stopVoiceRecognition();
      setIsTextMode(true);
    } else {
      setIsTextMode(false);
      const success = await startVoiceRecognition();
      if (!success) {
        setIsTextMode(true);
      }
    }
  };

  const handleModeSwitch = () => {
    if (!isTextMode && isListening) {
      stopVoiceRecognition();
    }
    reset();
    setIsTextMode(!isTextMode);
  };

  const canSend = (isTextMode && message.trim()) || (!isTextMode && transcript.trim());

  return (
    <div className="bg-white border-t border-lavender-100 p-4 shadow-elder-lg">
      <div className="max-w-screen-xl mx-auto">
        {/* Mode selector */}
        <div className="flex justify-center mb-4">
          <div className="flex bg-lavender-100 rounded-elder p-1">
            <button
              onClick={handleModeSwitch}
              className={`px-4 py-2 rounded-elder text-sm-elder font-medium transition-all ${
                isTextMode
                  ? 'bg-white text-lavender-800 shadow-elder'
                  : 'text-lavender-600 hover:text-lavender-800'
              }`}
            >
              Type
            </button>
            <button
              onClick={handleModeSwitch}
              disabled={!isSupported}
              className={`px-4 py-2 rounded-elder text-sm-elder font-medium transition-all ${
                !isTextMode
                  ? 'bg-white text-lavender-800 shadow-elder'
                  : 'text-lavender-600 hover:text-lavender-800'
              } ${!isSupported ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              Speak
            </button>
          </div>
        </div>

        <AnimatePresence mode="wait">
          {isTextMode ? (
            // Text input mode
            <motion.div
              key="text-mode"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="flex items-end space-x-3"
            >
              <div className="flex-1">
                <textarea
                  ref={textareaRef}
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={placeholder}
                  disabled={disabled}
                  maxLength={maxLength}
                  rows={1}
                  className="input-elder resize-none min-h-[60px] max-h-32"
                />
                
                <div className="flex justify-between items-center mt-2 px-2">
                  <span className="text-elder-caption">
                    {message.length}/{maxLength}
                  </span>
                  
                  {isSupported && (
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleVoiceToggle}
                      icon={Mic}
                      ariaLabel="Switch to voice input"
                    />
                  )}
                </div>
              </div>

              <Button
                onClick={handleSendText}
                disabled={!message.trim() || disabled}
                icon={Send}
                size="lg"
                ariaLabel="Send message"
                className="flex-shrink-0"
              />
            </motion.div>
          ) : (
            // Voice input mode
            <motion.div
              key="voice-mode"
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="flex flex-col items-center space-y-6"
            >
              {/* Voice indicator */}
              <motion.div
                className={`voice-indicator ${
                  isListening 
                    ? 'bg-coral-500 shadow-coral-300' 
                    : isProcessing 
                    ? 'bg-sage-500 shadow-sage-300'
                    : 'bg-lavender-500 shadow-lavender-300'
                }`}
                animate={isListening ? {
                  scale: [1, 1.1, 1],
                  boxShadow: ['0 0 0 0 rgba(255, 107, 122, 0.7)', '0 0 0 20px rgba(255, 107, 122, 0)', '0 0 0 0 rgba(255, 107, 122, 0)']
                } : {}}
                transition={{ duration: 1.5, repeat: isListening ? Infinity : 0 }}
              >
                {isProcessing ? (
                  <Loader size={40} className="text-white animate-spin" />
                ) : (
                  <motion.div
                    animate={isListening ? { scale: [1, 1.2, 1] } : {}}
                    transition={{ duration: 0.5, repeat: isListening ? Infinity : 0 }}
                  >
                    {isListening ? (
                      <MicOff size={40} className="text-white" />
                    ) : (
                      <Mic size={40} className="text-white" />
                    )}
                  </motion.div>
                )}
              </motion.div>

              {/* Status text */}
              <div className="text-center">
                <p className="text-elder-h3 mb-2">
                  {isListening 
                    ? 'Listening...' 
                    : isProcessing 
                    ? 'Processing...' 
                    : 'Tap to speak'
                  }
                </p>
                
                {error && (
                  <p className="text-coral-600 text-sm-elder">{error}</p>
                )}
                
                {transcript && (
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="mt-4 p-4 bg-lavender-50 rounded-elder max-w-md"
                  >
                    <p className="text-elder-body text-lavender-800">
                      "{transcript}"
                    </p>
                  </motion.div>
                )}
              </div>

              {/* Voice controls */}
              <div className="flex space-x-4">
                <Button
                  onClick={handleVoiceToggle}
                  disabled={disabled || isProcessing}
                  variant={isListening ? "emergency" : "primary"}
                  size="lg"
                  icon={isListening ? MicOff : Mic}
                  ariaLabel={isListening ? "Stop listening" : "Start listening"}
                >
                  {isListening ? 'Stop' : 'Start'}
                </Button>

                <Button
                  onClick={handleModeSwitch}
                  variant="ghost"
                  size="lg"
                  ariaLabel="Switch to text input"
                >
                  Type instead
                </Button>
              </div>

              {/* Voice waveform during listening */}
              {isListening && (
                <motion.div
                  className="voice-waveform"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                >
                  {Array.from({ length: 5 }).map((_, i) => (
                    <motion.div
                      key={i}
                      animate={{
                        height: [4, 20, 4],
                      }}
                      transition={{
                        duration: 0.5,
                        repeat: Infinity,
                        delay: i * 0.1,
                      }}
                    />
                  ))}
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};