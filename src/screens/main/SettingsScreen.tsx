import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  Settings, 
  User, 
  Bell, 
  Volume2, 
  Accessibility, 
  Moon, 
  Sun,
  Smartphone,
  Shield,
  LogOut,
  ChevronRight,
  Check,
  X
} from 'lucide-react';
import { ElderlyLayout } from '../../components/common/Layout';
import { Card } from '../../components/common/Card';
import { Button } from '../../components/common/Button';
import { Modal } from '../../components/common/Modal';
import { useAppStore } from '../../store';

interface SettingItem {
  id: string;
  title: string;
  description: string;
  icon: React.ComponentType<any>;
  type: 'toggle' | 'select' | 'button';
  value?: boolean | string;
  options?: string[];
  action?: () => void;
}

export const SettingsScreen: React.FC = () => {
  const { user, logout } = useAppStore();
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [isVoiceEnabled, setIsVoiceEnabled] = useState(true);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [highContrastMode, setHighContrastMode] = useState(false);
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  const generalSettings: SettingItem[] = [
    {
      id: 'voice',
      title: 'Voice Assistant',
      description: 'Enable voice commands and responses',
      icon: Volume2,
      type: 'toggle',
      value: isVoiceEnabled,
      action: () => setIsVoiceEnabled(!isVoiceEnabled)
    },
    {
      id: 'notifications',
      title: 'Notifications',
      description: 'Receive reminders and alerts',
      icon: Bell,
      type: 'toggle',
      value: notificationsEnabled,
      action: () => setNotificationsEnabled(!notificationsEnabled)
    },
    {
      id: 'theme',
      title: 'Dark Mode',
      description: 'Use dark colors to reduce eye strain',
      icon: isDarkMode ? Moon : Sun,
      type: 'toggle',
      value: isDarkMode,
      action: () => setIsDarkMode(!isDarkMode)
    }
  ];

  const accessibilitySettings: SettingItem[] = [
    {
      id: 'contrast',
      title: 'High Contrast',
      description: 'Increase text and button contrast',
      icon: Accessibility,
      type: 'toggle',
      value: highContrastMode,
      action: () => setHighContrastMode(!highContrastMode)
    },
    {
      id: 'text-size',
      title: 'Text Size',
      description: 'Adjust text size for better readability',
      icon: Smartphone,
      type: 'select',
      value: 'Large',
      options: ['Small', 'Medium', 'Large', 'Extra Large']
    }
  ];

  const accountSettings: SettingItem[] = [
    {
      id: 'profile',
      title: 'Profile Settings',
      description: 'Update your personal information',
      icon: User,
      type: 'button',
      action: () => {
        // Navigate to profile settings
      }
    },
    {
      id: 'privacy',
      title: 'Privacy & Security',
      description: 'Manage your privacy settings',
      icon: Shield,
      type: 'button',
      action: () => {
        // Navigate to privacy settings
      }
    },
    {
      id: 'logout',
      title: 'Sign Out',
      description: 'Sign out of your account',
      icon: LogOut,
      type: 'button',
      action: () => setShowLogoutModal(true)
    }
  ];

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

  const renderSettingItem = (item: SettingItem) => {
    const Icon = item.icon;
    
    return (
      <motion.div
        key={item.id}
        variants={itemVariants}
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
      >
        <Card
          onClick={item.action}
          className="cursor-pointer hover:border-lavender-300 transition-colors"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-lavender-500 rounded-elder flex items-center justify-center">
                <Icon size={24} className="text-white" />
              </div>
              
              <div className="flex-1">
                <h3 className="text-elder-h3">{item.title}</h3>
                <p className="text-elder-caption">{item.description}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {item.type === 'toggle' && (
                <div className={`
                  w-14 h-8 rounded-full p-1 transition-colors
                  ${item.value ? 'bg-sage-500' : 'bg-lavender-200'}
                `}>
                  <div className={`
                    w-6 h-6 rounded-full bg-white transition-transform
                    ${item.value ? 'translate-x-6' : 'translate-x-0'}
                  `}>
                    {item.value && (
                      <Check size={16} className="text-sage-500 p-1" />
                    )}
                  </div>
                </div>
              )}
              
              {item.type === 'select' && (
                <div className="flex items-center space-x-2">
                  <span className="text-elder-body">{item.value}</span>
                  <ChevronRight size={20} className="text-lavender-400" />
                </div>
              )}
              
              {item.type === 'button' && (
                <ChevronRight size={20} className="text-lavender-400" />
              )}
            </div>
          </div>
        </Card>
      </motion.div>
    );
  };

  return (
    <ElderlyLayout title="Settings">
      <motion.div
        className="min-h-screen pb-8"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {/* Header */}
        <motion.div
          variants={itemVariants}
          className="text-center mb-8 pt-4"
        >
          <motion.div
            className="w-16 h-16 bg-lavender-500 rounded-full flex items-center justify-center mx-auto mb-4"
            animate={{ 
              rotate: [0, 360],
            }}
            transition={{
              duration: 20,
              repeat: Infinity,
              ease: 'linear'
            }}
          >
            <Settings size={28} className="text-white" />
          </motion.div>
          
          <h1 className="text-elder-h1 mb-2">Settings</h1>
          <p className="text-elder-body text-lavender-600">
            Customize your ElderWise experience
          </p>
        </motion.div>

        {/* User Info */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <Card className="bg-gradient-to-r from-sage-50 to-lavender-50 border-sage-200">
            <div className="flex items-center space-x-4">
              <div className="w-16 h-16 bg-sage-500 rounded-full flex items-center justify-center">
                <User size={32} className="text-white" />
              </div>
              
              <div>
                <h2 className="text-elder-h2">{user?.name || 'User'}</h2>
                <p className="text-elder-body text-lavender-600">
                  {user?.email || 'user@example.com'}
                </p>
                <p className="text-elder-caption text-sage-600">
                  Member since {user?.createdAt ? new Date(user.createdAt).getFullYear() : '2024'}
                </p>
              </div>
            </div>
          </Card>
        </motion.div>

        {/* General Settings */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">General</h2>
          
          <div className="space-y-3">
            {generalSettings.map(renderSettingItem)}
          </div>
        </motion.div>

        {/* Accessibility Settings */}
        <motion.div variants={itemVariants} className="mb-8 px-4">
          <h2 className="text-elder-h2 mb-4">Accessibility</h2>
          
          <div className="space-y-3">
            {accessibilitySettings.map(renderSettingItem)}
          </div>
        </motion.div>

        {/* Account Settings */}
        <motion.div variants={itemVariants} className="px-4">
          <h2 className="text-elder-h2 mb-4">Account</h2>
          
          <div className="space-y-3">
            {accountSettings.map(renderSettingItem)}
          </div>
        </motion.div>
      </motion.div>

      {/* Logout Confirmation Modal */}
      <Modal
        isOpen={showLogoutModal}
        onClose={() => setShowLogoutModal(false)}
        title="Sign Out"
      >
        <div className="text-center space-y-6">
          <div className="w-16 h-16 bg-coral-500 rounded-full flex items-center justify-center mx-auto">
            <LogOut size={32} className="text-white" />
          </div>
          
          <div>
            <h3 className="text-elder-h2 mb-2">Are you sure?</h3>
            <p className="text-elder-body text-lavender-600">
              You will be signed out of your account and will need to sign in again to access ElderWise.
            </p>
          </div>

          <div className="space-y-3">
            <Button
              variant="secondary"
              size="xl"
              fullWidth
              onClick={() => {
                logout();
                setShowLogoutModal(false);
              }}
              icon={LogOut}
            >
              Yes, Sign Out
            </Button>
            
            <Button
              variant="ghost"
              size="lg"
              fullWidth
              onClick={() => setShowLogoutModal(false)}
              icon={X}
            >
              Cancel
            </Button>
          </div>
        </div>
      </Modal>
    </ElderlyLayout>
  );
};