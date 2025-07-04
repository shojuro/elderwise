import React, { useEffect, useRef, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { Clock, Settings, MoreVertical } from 'lucide-react';
import { ElderlyLayout } from '../../components/common/Layout';
import { Button } from '../../components/common/Button';
import { ChatMessage, TypingIndicator } from '../../components/chat/ChatMessage';
import { ChatInput } from '../../components/chat/ChatInput';
import { useChat } from '../../hooks/useChat';
import { useAppStore } from '../../store';
import { LoadingSpinner } from '../../components/common/LoadingSpinner';

const CONVERSATION_STARTERS = [
  "How are you feeling today?",
  "Tell me about your morning",
  "What's on your mind?",
  "How did you sleep last night?",
  "What would you like to talk about?"
];

export const ChatScreen: React.FC = () => {
  const { user } = useAppStore();
  const { 
    messages, 
    isTyping, 
    isLoading, 
    sendMessage, 
    sendVoiceMessage, 
    clearConversation,
    error 
  } = useChat();
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [showStarters, setShowStarters] = useState(false);
  const [currentTime, setCurrentTime] = useState(new Date());

  // Update time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);

    return () => clearInterval(timer);
  }, []);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ 
      behavior: 'smooth',
      block: 'end'
    });
  }, [messages, isTyping]);

  // Show conversation starters if no messages
  useEffect(() => {
    setShowStarters(messages.length === 0);
  }, [messages.length]);

  const handleSendMessage = (message: string) => {
    setShowStarters(false);
    sendMessage(message);
  };

  const handleSendVoiceMessage = (transcript: string) => {
    setShowStarters(false);
    sendVoiceMessage(transcript);
  };

  const handleStarterClick = (starter: string) => {
    handleSendMessage(starter);
  };

  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  if (!user) {
    return (
      <ElderlyLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" text="Loading your profile..." />
        </div>
      </ElderlyLayout>
    );
  }

  return (
    <ElderlyLayout>
      <div className="flex flex-col h-screen">
        {/* Header */}
        <motion.header
          className="bg-white border-b border-lavender-100 shadow-elder p-4"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-elder-h2">
                {getGreeting()}, {user.name}
              </h1>
              <div className="flex items-center text-elder-caption mt-1">
                <Clock size={16} className="mr-1" />
                <span>
                  {currentTime.toLocaleTimeString([], { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </span>
              </div>
            </div>

            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="sm"
                icon={Settings}
                ariaLabel="Settings"
              />
              <Button
                variant="ghost"
                size="sm"
                icon={MoreVertical}
                ariaLabel="More options"
              />
            </div>
          </div>
        </motion.header>

        {/* Messages area */}
        <div className="flex-1 overflow-y-auto p-4 pb-20">
          <div className="max-w-4xl mx-auto">
            {/* Welcome message for new users */}
            {messages.length === 0 && (
              <motion.div
                className="text-center mb-8"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.3 }}
              >
                <div className="w-20 h-20 bg-lavender-500 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-xl">EW</span>
                </div>
                <h2 className="text-elder-h2 mb-4">
                  Hello {user.name}! I'm ElderWise, your caring companion.
                </h2>
                <p className="text-elder-body text-lavender-600 max-w-md mx-auto">
                  I'm here to listen, chat, and support you throughout your day. 
                  How can I help you today?
                </p>
              </motion.div>
            )}

            {/* Conversation starters */}
            <AnimatePresence>
              {showStarters && (
                <motion.div
                  className="mb-8"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ delay: 0.5 }}
                >
                  <p className="text-elder-h3 text-center mb-4">
                    Or try one of these:
                  </p>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl mx-auto">
                    {CONVERSATION_STARTERS.map((starter, index) => (
                      <motion.div
                        key={starter}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.6 + index * 0.1 }}
                      >
                        <Button
                          variant="ghost"
                          onClick={() => handleStarterClick(starter)}
                          className="w-full text-left justify-start p-4 h-auto"
                        >
                          <span className="text-base-elder">{starter}</span>
                        </Button>
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error message */}
            {error && (
              <motion.div
                className="mb-4 p-4 bg-coral-50 border border-coral-200 rounded-elder"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
              >
                <p className="text-coral-700 text-base-elder">
                  {error}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => window.location.reload()}
                  className="mt-2"
                >
                  Try again
                </Button>
              </motion.div>
            )}

            {/* Chat messages */}
            <div className="space-y-1">
              <AnimatePresence>
                {messages.map((message) => (
                  <ChatMessage
                    key={message.id}
                    message={message}
                    isLatest={message.id === messages[messages.length - 1]?.id}
                  />
                ))}
              </AnimatePresence>

              {/* Typing indicator */}
              <AnimatePresence>
                {isTyping && (
                  <TypingIndicator />
                )}
              </AnimatePresence>
            </div>

            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input area */}
        <div className="fixed bottom-20 left-0 right-0 z-30">
          <ChatInput
            onSendMessage={handleSendMessage}
            onSendVoiceMessage={handleSendVoiceMessage}
            disabled={isLoading}
          />
        </div>

        {/* Quick actions overlay */}
        {messages.length > 5 && (
          <motion.div
            className="fixed top-20 right-4 z-30"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Button
              variant="ghost"
              size="sm"
              onClick={clearConversation}
              className="bg-white shadow-elder"
            >
              New Chat
            </Button>
          </motion.div>
        )}
      </div>
    </ElderlyLayout>
  );
};