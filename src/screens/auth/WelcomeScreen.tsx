import React from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Heart, MessageCircle, Users } from 'lucide-react';
import { Button } from '../../components/common/Button';
import { AuthLayout } from '../../components/common/Layout';

export const WelcomeScreen: React.FC = () => {
  const navigate = useNavigate();

  const features = [
    {
      icon: MessageCircle,
      title: 'Always Here to Listen',
      description: 'Chat anytime with your caring AI companion who remembers your conversations'
    },
    {
      icon: Heart,
      title: 'Your Wellbeing Matters',
      description: 'Track your mood and health with gentle, supportive check-ins'
    },
    {
      icon: Users,
      title: 'Stay Connected',
      description: 'Keep your family informed while maintaining your independence'
    }
  ];

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
        delayChildren: 0.3
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
    <AuthLayout>
      <motion.div
        className="w-full max-w-md mx-auto text-center"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Logo and welcome */}
        <motion.div
          variants={itemVariants}
          className="mb-12"
        >
          <motion.div
            className="w-24 h-24 bg-lavender-500 rounded-full flex items-center justify-center mx-auto mb-6"
            animate={{ 
              rotate: [0, 10, -10, 0],
              scale: [1, 1.05, 1]
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              repeatType: 'reverse'
            }}
          >
            <Heart size={40} className="text-white" />
          </motion.div>
          
          <h1 className="text-elder-h1 mb-4">
            Welcome to ElderWise
          </h1>
          
          <p className="text-elder-body text-lavender-600">
            Your caring AI companion for everyday support, conversation, and connection
          </p>
        </motion.div>

        {/* Features */}
        <motion.div
          variants={itemVariants}
          className="space-y-6 mb-12"
        >
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className="flex items-start space-x-4 text-left"
              variants={itemVariants}
            >
              <div className="w-12 h-12 bg-sage-100 rounded-elder flex items-center justify-center flex-shrink-0">
                <feature.icon size={24} className="text-sage-600" />
              </div>
              
              <div>
                <h3 className="text-elder-h3 mb-2">{feature.title}</h3>
                <p className="text-elder-body text-lavender-600">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Action buttons */}
        <motion.div
          variants={itemVariants}
          className="space-y-4"
        >
          <Button
            onClick={() => navigate('/setup')}
            size="xl"
            fullWidth
            className="text-xl-elder py-6"
          >
            Get Started
          </Button>
          
          <Button
            onClick={() => navigate('/login')}
            variant="ghost"
            size="lg"
            fullWidth
          >
            I already have an account
          </Button>
        </motion.div>

        {/* Footer */}
        <motion.div
          variants={itemVariants}
          className="mt-12 pt-8 border-t border-lavender-100"
        >
          <p className="text-elder-caption">
            Made with care for seniors and their families
          </p>
        </motion.div>
      </motion.div>
    </AuthLayout>
  );
};