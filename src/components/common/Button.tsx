import React from 'react';
import { motion } from 'framer-motion';
import { LucideIcon } from 'lucide-react';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'emergency' | 'ghost' | 'outline';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  disabled?: boolean;
  loading?: boolean;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  fullWidth?: boolean;
  className?: string;
  type?: 'button' | 'submit' | 'reset';
  ariaLabel?: string;
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  icon: Icon,
  iconPosition = 'left',
  fullWidth = false,
  className = '',
  type = 'button',
  ariaLabel,
}) => {
  const baseClasses = 'btn-elder inline-flex items-center justify-center font-semibold transition-all duration-200 ease-in-out focus:outline-none focus:ring-4 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'btn-primary',
    secondary: 'btn-secondary',
    emergency: 'btn-emergency',
    ghost: 'btn-ghost',
    outline: 'bg-transparent border-2 border-lavender-300 text-lavender-700 hover:bg-lavender-50 focus:ring-lavender-300',
  };

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm-elder min-h-[48px]',
    md: 'px-6 py-3 text-base-elder min-h-[60px]',
    lg: 'px-8 py-4 text-lg-elder min-h-[72px]',
    xl: 'px-10 py-5 text-xl-elder min-h-[84px]',
  };

  const classes = `
    ${baseClasses}
    ${variantClasses[variant]}
    ${sizeClasses[size]}
    ${fullWidth ? 'w-full' : ''}
    ${className}
  `.trim();

  const iconSize = size === 'sm' ? 20 : size === 'md' ? 24 : size === 'lg' ? 28 : 32;

  return (
    <motion.button
      type={type}
      className={classes}
      onClick={onClick}
      disabled={disabled || loading}
      aria-label={ariaLabel}
      whileHover={!disabled ? { scale: 1.02 } : {}}
      whileTap={!disabled ? { scale: 0.98 } : {}}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
    >
      {loading ? (
        <div className="loading-dots mr-2">
          <div></div>
          <div></div>
          <div></div>
        </div>
      ) : Icon && iconPosition === 'left' ? (
        <Icon size={iconSize} className="mr-2 flex-shrink-0" />
      ) : null}
      
      <span className="flex-1 text-center">{children}</span>
      
      {!loading && Icon && iconPosition === 'right' && (
        <Icon size={iconSize} className="ml-2 flex-shrink-0" />
      )}
    </motion.button>
  );
};