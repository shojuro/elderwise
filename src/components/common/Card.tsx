import React from 'react';
import { motion } from 'framer-motion';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg' | 'xl';
  shadow?: 'sm' | 'md' | 'lg' | 'xl';
}

export const Card: React.FC<CardProps> = ({
  children,
  className = '',
  onClick,
  hover = false,
  padding = 'md',
  shadow = 'md',
}) => {
  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
    xl: 'p-10',
  };

  const shadowClasses = {
    sm: 'shadow-elder',
    md: 'shadow-elder-lg',
    lg: 'shadow-elder-xl',
    xl: 'shadow-2xl',
  };

  const baseClasses = `
    card-elder
    ${paddingClasses[padding]}
    ${shadowClasses[shadow]}
    ${onClick ? 'cursor-pointer' : ''}
    ${hover ? 'hover:shadow-elder-lg hover:scale-105' : ''}
    ${className}
  `.trim();

  const Component = onClick ? motion.div : 'div';

  return (
    <Component
      className={baseClasses}
      onClick={onClick}
      {...(onClick ? {
        whileHover: { scale: 1.02 },
        whileTap: { scale: 0.98 },
        transition: { type: 'spring', stiffness: 400, damping: 17 },
      } : {})}
    >
      {children}
    </Component>
  );
};