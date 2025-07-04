import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { formatDistanceToNow } from 'date-fns';
import { 
  MessageCircle, 
  Heart, 
  Memory, 
  Phone, 
  Sun, 
  Moon,
  Cloud,
  ChevronRight,
  Calendar,
  Clock
} from 'lucide-react';
import { ElderlyLayout } from '../../components/common/Layout';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { useAppStore } from '../../store';

export const HomeScreen: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAppStore();
  
  const currentHour = new Date().getHours();
  const isEvening = currentHour >= 18;
  const isMorning = currentHour < 12;

  const getGreeting = () => {
    if (isMorning) return 'Good morning';
    if (currentHour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getGreetingIcon = () => {
    if (isMorning) return Sun;
    if (isEvening) return Moon;
    return Cloud;
  };

  const quickActions = [
    {
      title: 'Start Chatting',
      subtitle: 'Talk with ElderWise',
      icon: MessageCircle,
      color: 'lavender',
      path: '/chat',
      primary: true
    },
    {
      title: 'Health Check',
      subtitle: 'How are you feeling?',
      icon: Heart,
      color: 'sage',
      path: '/health'
    },
    {
      title: 'Memory Lane',
      subtitle: 'Browse past conversations',
      icon: Memory,
      color: 'lavender',
      path: '/memories'
    },
    {
      title: 'Emergency Help',
      subtitle: 'Quick access to help',
      icon: Phone,
      color: 'coral',
      path: '/emergency'
    }
  ];

  const todaysTips = [
    "Remember to take your morning medication",
    "Try to get some sunlight today",
    "Stay hydrated throughout the day",
    "Take breaks and rest when needed"
  ];

  const GreetingIcon = getGreetingIcon();

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        type: 'spring',
        stiffness: 500,
        damping: 30
      }
    }
  };

  return (
    <ElderlyLayout>
      <motion.div
        className="min-h-screen pb-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header with greeting */}
        <motion.div
          variants={itemVariants}
          className="text-center mb-8 pt-8"
        >
          <motion.div
            className="w-16 h-16 bg-gradient-to-br from-lavender-400 to-lavender-600 rounded-full flex items-center justify-center mx-auto mb-4"
            animate={{ 
              rotate: [0, 5, -5, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{
              duration: 4,
              repeat: Infinity,
              repeatType: 'reverse'
            }}
          >
            <GreetingIcon size={28} className="text-white" />
          </motion.div>
          
          <h1 className="text-elder-h1 mb-2">
            {getGreeting()}, {user?.name || 'Friend'}!
          </h1>
          
          <div className="flex items-center justify-center text-elder-body text-lavender-600">
            <Calendar size={18} className="mr-2" />
            <span>{new Date().toLocaleDateString('en-US', { 
              weekday: 'long', 
              month: 'long', 
              day: 'numeric' 
            })}</span>
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants} className="mb-8">
          <h2 className="text-elder-h2 mb-4 px-4">Quick Actions</h2>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 px-4">
            {quickActions.map((action, index) => (
              <motion.div
                key={action.title}
                variants={itemVariants}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Card
                  hover
                  onClick={() => navigate(action.path)}
                  className={`
                    ${action.primary ? 'bg-gradient-to-br from-lavender-50 to-lavender-100 border-lavender-200' : ''}
                    cursor-pointer transition-all duration-200
                  `}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                      <div className={`
                        w-12 h-12 rounded-elder flex items-center justify-center
                        ${action.color === 'lavender' ? 'bg-lavender-500' : ''}
                        ${action.color === 'sage' ? 'bg-sage-500' : ''}
                        ${action.color === 'coral' ? 'bg-coral-500' : ''}
                      `}>
                        <action.icon size={24} className="text-white" />
                      </div>
                      
                      <div>
                        <h3 className="text-elder-h3">{action.title}</h3>
                        <p className="text-elder-caption">{action.subtitle}</p>
                      </div>
                    </div>
                    
                    <ChevronRight size={20} className="text-lavender-400" />
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Today's Wellness Tips */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">Today's Wellness Tips</h2>
          
          <Card className="bg-gradient-to-br from-sage-50 to-sage-100 border-sage-200">
            <div className="space-y-3">
              {todaysTips.map((tip, index) => (
                <motion.div
                  key={index}
                  className="flex items-start space-x-3"
                  variants={itemVariants}
                >
                  <div className="w-6 h-6 bg-sage-500 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-white text-xs font-bold">{index + 1}</span>
                  </div>
                  <p className="text-elder-body text-sage-800">{tip}</p>
                </motion.div>
              ))}
            </div>
          </Card>
        </motion.div>

        {/* Recent Activity */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">Recent Activity</h2>
          
          <Card>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-lavender-500 rounded-full flex items-center justify-center">
                    <MessageCircle size={20} className="text-white" />
                  </div>
                  <div>
                    <p className="text-elder-body">Last conversation</p>
                    <p className="text-elder-caption">
                      {formatDistanceToNow(new Date(Date.now() - 2 * 60 * 60 * 1000), { addSuffix: true })}
                    </p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/chat')}
                >
                  Continue
                </Button>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-sage-500 rounded-full flex items-center justify-center">
                    <Heart size={20} className="text-white" />
                  </div>
                  <div>
                    <p className="text-elder-body">Mood check-in</p>
                    <p className="text-elder-caption">Feeling good today</p>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigate('/health')}
                >
                  Update
                </Button>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Weather Widget */}
        <motion.div variants={itemVariants} className="px-4">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-elder-h3 text-blue-800">Today's Weather</h3>
                <p className="text-elder-body text-blue-700">Partly cloudy, 72°F</p>
                <p className="text-elder-caption text-blue-600">Perfect for a walk!</p>
              </div>
              <div className="w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center">
                <Cloud size={28} className="text-white" />
              </div>
            </div>
          </Card>
        </motion.div>

        {/* Emergency button (always visible) */}
        <motion.div
          variants={itemVariants}
          className="fixed bottom-24 right-4 z-30"
        >
          <Button
            variant="emergency"
            size="lg"
            onClick={() => navigate('/emergency')}
            icon={Phone}
            className="rounded-full w-16 h-16 shadow-elder-xl"
            ariaLabel="Emergency help"
          />
        </motion.div>
      </motion.div>
    </ElderlyLayout>
  );
};