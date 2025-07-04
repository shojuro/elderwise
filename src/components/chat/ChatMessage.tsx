import React from 'react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { Volume2, VolumeX } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '../../types';
import { useVoiceResponse } from '../../hooks/useVoice';
import { Button } from '../common/Button';

interface ChatMessageProps {
  message: ChatMessageType;
  isLatest?: boolean;
  showTimestamp?: boolean;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  isLatest = false,
  showTimestamp = true,
}) => {
  const { speakMessage, stopSpeaking, isEnabled } = useVoiceResponse();
  const [isSpeaking, setIsSpeaking] = React.useState(false);

  const isUser = message.sender === 'user';
  const isAI = message.sender === 'ai';

  const handleSpeak = async () => {
    if (isSpeaking) {
      stopSpeaking();
      setIsSpeaking(false);
    } else {
      setIsSpeaking(true);
      try {
        await speakMessage(message.content);
      } finally {
        setIsSpeaking(false);
      }
    }
  };

  const messageVariants = {
    hidden: { opacity: 0, y: 20, scale: 0.95 },
    visible: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: {
        type: 'spring',
        stiffness: 500,
        damping: 30,
      },
    },
  };

  return (
    <motion.div
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
      variants={messageVariants}
      initial="hidden"
      animate="visible"
      layout
    >
      <div className={`max-w-[80%] ${isUser ? 'order-2' : 'order-1'}`}>
        {/* Avatar for AI messages */}
        {isAI && (
          <div className="flex items-start space-x-3">
            <motion.div
              className="w-10 h-10 bg-lavender-500 rounded-full flex items-center justify-center flex-shrink-0"
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.1 }}
            >
              <span className="text-white font-semibold text-sm">EW</span>
            </motion.div>
            
            <div className="flex-1">
              <div className={`chat-bubble-ai ${message.metadata?.category === 'error' ? 'border-coral-200 bg-coral-50' : ''}`}>
                <p className="text-elder-body whitespace-pre-wrap">
                  {message.content}
                </p>
                
                {/* Voice playback button for AI messages */}
                {isEnabled && (
                  <div className="mt-3 flex justify-end">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleSpeak}
                      icon={isSpeaking ? VolumeX : Volume2}
                      ariaLabel={isSpeaking ? 'Stop speaking' : 'Read message aloud'}
                      className="text-lavender-600 hover:text-lavender-800"
                    />
                  </div>
                )}
              </div>
              
              {showTimestamp && (
                <p className="text-elder-caption mt-2 px-1">
                  {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
                </p>
              )}
            </div>
          </div>
        )}

        {/* User messages */}
        {isUser && (
          <div className="flex flex-col items-end">
            <div className="chat-bubble-user">
              <p className="text-white text-elder-body whitespace-pre-wrap">
                {message.content}
              </p>
              
              {message.type === 'voice' && (
                <div className="mt-2 flex items-center text-lavender-100">
                  <Volume2 size={16} className="mr-1" />
                  <span className="text-xs">Voice message</span>
                </div>
              )}
            </div>
            
            {showTimestamp && (
              <p className="text-elder-caption mt-2 px-1">
                {formatDistanceToNow(new Date(message.timestamp), { addSuffix: true })}
              </p>
            )}
          </div>
        )}

        {/* Message importance indicator */}
        {message.metadata?.important && (
          <motion.div
            className="mt-2 flex items-center text-sage-600"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
          >
            <div className="w-2 h-2 bg-sage-500 rounded-full mr-2" />
            <span className="text-xs-elder">Important memory</span>
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

// Loading message component for when AI is typing
export const TypingIndicator: React.FC = () => {
  return (
    <motion.div
      className="flex justify-start mb-4"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
    >
      <div className="flex items-start space-x-3">
        <div className="w-10 h-10 bg-lavender-500 rounded-full flex items-center justify-center">
          <span className="text-white font-semibold text-sm">EW</span>
        </div>
        
        <div className="chat-bubble-ai">
          <div className="flex items-center space-x-1">
            <span className="text-elder-body">ElderWise is thinking</span>
            <div className="loading-dots ml-2">
              <div />
              <div />
              <div />
            </div>
          </div>
        </div>
      </div>
    </motion.div>
  );
};