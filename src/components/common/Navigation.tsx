import React from 'react';
import { motion } from 'framer-motion';
import { useLocation, useNavigate } from 'react-router-dom';
import { 
  MessageCircle, 
  Memory, 
  Heart, 
  Users, 
  Settings,
  Phone,
  Home,
  Calendar,
  User
} from 'lucide-react';
import { useAppStore } from '../../store';

interface NavigationItem {
  id: string;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  path: string;
  badge?: number;
  roles?: string[];
}

const elderlyNavItems: NavigationItem[] = [
  {
    id: 'home',
    label: 'Home',
    icon: Home,
    path: '/',
  },
  {
    id: 'chat',
    label: 'Chat',
    icon: MessageCircle,
    path: '/chat',
  },
  {
    id: 'memories',
    label: 'Memories',
    icon: Memory,
    path: '/memories',
  },
  {
    id: 'health',
    label: 'Health',
    icon: Heart,
    path: '/health',
  },
  {
    id: 'emergency',
    label: 'Help',
    icon: Phone,
    path: '/emergency',
  },
];

const familyNavItems: NavigationItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: Home,
    path: '/family',
  },
  {
    id: 'monitoring',
    label: 'Monitoring',
    icon: Heart,
    path: '/family/monitoring',
  },
  {
    id: 'memories',
    label: 'Memories',
    icon: Memory,
    path: '/family/memories',
  },
  {
    id: 'calendar',
    label: 'Calendar',
    icon: Calendar,
    path: '/family/calendar',
  },
  {
    id: 'profile',
    label: 'Profile',
    icon: User,
    path: '/family/profile',
  },
];

interface BottomNavigationProps {
  className?: string;
}

export const BottomNavigation: React.FC<BottomNavigationProps> = ({ className = '' }) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAppStore();

  const navItems = user?.role === 'family' ? familyNavItems : elderlyNavItems;

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <motion.nav
      className={`
        fixed bottom-0 left-0 right-0 z-40
        bg-white border-t border-lavender-100 shadow-elder-xl
        ${className}
      `.trim()}
      initial={{ y: 100 }}
      animate={{ y: 0 }}
      transition={{ type: 'spring', stiffness: 400, damping: 25 }}
    >
      <div className="flex items-center justify-around px-2 py-2 max-w-screen-xl mx-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path || 
                          (item.path !== '/' && location.pathname.startsWith(item.path));
          
          return (
            <motion.button
              key={item.id}
              onClick={() => handleNavigation(item.path)}
              className={`
                nav-item relative flex-1 max-w-[80px]
                ${isActive ? 'active' : ''}
              `}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              transition={{ type: 'spring', stiffness: 400, damping: 17 }}
            >
              <div className="relative">
                <item.icon 
                  size={28} 
                  className={`mx-auto mb-1 ${isActive ? 'text-lavender-800' : 'text-lavender-600'}`}
                />
                
                {item.badge && item.badge > 0 && (
                  <motion.div
                    className="absolute -top-1 -right-1 bg-coral-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ type: 'spring', stiffness: 500, damping: 20 }}
                  >
                    {item.badge > 99 ? '99+' : item.badge}
                  </motion.div>
                )}
              </div>
              
              <span className={`text-xs-elder font-medium ${isActive ? 'text-lavender-800' : 'text-lavender-600'}`}>
                {item.label}
              </span>

              {isActive && (
                <motion.div
                  className="absolute -top-2 left-1/2 w-12 h-1 bg-lavender-500 rounded-full"
                  layoutId="activeTab"
                  initial={{ opacity: 0, scale: 0.8 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                  style={{ x: '-50%' }}
                />
              )}
            </motion.button>
          );
        })}
      </div>
    </motion.nav>
  );
};

// Top navigation for specific screens
interface TopNavigationProps {
  title: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightAction?: React.ReactNode;
  className?: string;
}

export const TopNavigation: React.FC<TopNavigationProps> = ({
  title,
  subtitle,
  showBack = false,
  onBack,
  rightAction,
  className = '',
}) => {
  const navigate = useNavigate();

  const handleBack = () => {
    if (onBack) {
      onBack();
    } else {
      navigate(-1);
    }
  };

  return (
    <motion.header
      className={`
        bg-cream-50 border-b border-lavender-100 px-4 py-4 shadow-elder
        ${className}
      `.trim()}
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div className="flex items-center justify-between max-w-screen-xl mx-auto">
        <div className="flex items-center">
          {showBack && (
            <motion.button
              onClick={handleBack}
              className="mr-4 p-2 rounded-elder text-lavender-700 hover:bg-lavender-100"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="m15 18-6-6 6-6"/>
              </svg>
            </motion.button>
          )}
          
          <div>
            <h1 className="text-elder-h2">{title}</h1>
            {subtitle && (
              <p className="text-elder-caption mt-1">{subtitle}</p>
            )}
          </div>
        </div>

        {rightAction && (
          <div className="flex-shrink-0">
            {rightAction}
          </div>
        )}
      </div>
    </motion.header>
  );
};