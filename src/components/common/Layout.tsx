import React from 'react';
import { motion } from 'framer-motion';
import { BottomNavigation, TopNavigation } from './Navigation';
import { useAppStore } from '../../store';

interface LayoutProps {
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  showNavigation?: boolean;
  showTopNav?: boolean;
  showBack?: boolean;
  onBack?: () => void;
  rightAction?: React.ReactNode;
  className?: string;
  fullHeight?: boolean;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  title,
  subtitle,
  showNavigation = true,
  showTopNav = false,
  showBack = false,
  onBack,
  rightAction,
  className = '',
  fullHeight = false,
}) => {
  const { user, preferences } = useAppStore();

  const pageVariants = {
    initial: { opacity: 0, x: 20 },
    in: { opacity: 1, x: 0 },
    out: { opacity: 0, x: -20 }
  };

  const pageTransition = {
    type: 'tween',
    ease: 'anticipate',
    duration: 0.3
  };

  return (
    <div className={`min-h-screen bg-cream-100 ${preferences.theme === 'high-contrast' ? 'contrast-more' : ''}`}>
      {/* Top Navigation */}
      {showTopNav && title && (
        <TopNavigation
          title={title}
          subtitle={subtitle}
          showBack={showBack}
          onBack={onBack}
          rightAction={rightAction}
        />
      )}

      {/* Main Content */}
      <motion.main
        id="main-content"
        tabIndex={-1}
        className={`
          ${fullHeight ? 'h-screen' : 'min-h-screen'}
          ${showNavigation ? 'pb-20' : ''}
          ${showTopNav ? 'pt-0' : 'pt-safe'}
          ${className}
        `.trim()}
        initial="initial"
        animate="in"
        exit="out"
        variants={pageVariants}
        transition={pageTransition}
      >
        <div className="max-w-screen-xl mx-auto px-4">
          {children}
        </div>
      </motion.main>

      {/* Bottom Navigation */}
      {showNavigation && user && (
        <BottomNavigation />
      )}
    </div>
  );
};

// Specialized layouts for different user types
export const ElderlyLayout: React.FC<{
  children: React.ReactNode;
  title?: string;
  className?: string;
}> = ({ children, title, className = '' }) => {
  return (
    <Layout
      showNavigation={true}
      showTopNav={!!title}
      title={title}
      className={`${className} text-2xl`} // Larger text for elderly users
    >
      {children}
    </Layout>
  );
};

export const FamilyLayout: React.FC<{
  children: React.ReactNode;
  title?: string;
  subtitle?: string;
  showBack?: boolean;
  onBack?: () => void;
  rightAction?: React.ReactNode;
  className?: string;
}> = ({ children, title, subtitle, showBack, onBack, rightAction, className = '' }) => {
  return (
    <Layout
      showNavigation={true}
      showTopNav={!!title}
      title={title}
      subtitle={subtitle}
      showBack={showBack}
      onBack={onBack}
      rightAction={rightAction}
      className={className}
    >
      {children}
    </Layout>
  );
};

// Auth layout (no navigation)
export const AuthLayout: React.FC<{
  children: React.ReactNode;
  className?: string;
}> = ({ children, className = '' }) => {
  return (
    <Layout
      showNavigation={false}
      showTopNav={false}
      fullHeight={true}
      className={`flex items-center justify-center ${className}`}
    >
      {children}
    </Layout>
  );
};

// Modal layout for full-screen modals
export const ModalLayout: React.FC<{
  children: React.ReactNode;
  title?: string;
  onClose?: () => void;
  className?: string;
}> = ({ children, title, onClose, className = '' }) => {
  return (
    <motion.div
      className={`fixed inset-0 z-50 bg-cream-100 ${className}`}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      transition={{ duration: 0.3 }}
    >
      {title && (
        <TopNavigation
          title={title}
          showBack={true}
          onBack={onClose}
        />
      )}
      <div className={`${title ? 'pt-16' : 'pt-safe'} h-full overflow-y-auto`}>
        {children}
      </div>
    </motion.div>
  );
};