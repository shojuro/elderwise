import React, { forwardRef } from 'react';
import { LucideIcon } from 'lucide-react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: LucideIcon;
  iconPosition?: 'left' | 'right';
  helperText?: string;
  fullWidth?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(({
  label,
  error,
  icon: Icon,
  iconPosition = 'left',
  helperText,
  fullWidth = false,
  className = '',
  ...props
}, ref) => {
  const inputClasses = `
    input-elder
    ${error ? 'border-coral-500 focus:border-coral-500' : ''}
    ${Icon ? (iconPosition === 'left' ? 'pl-12' : 'pr-12') : ''}
    ${fullWidth ? 'w-full' : ''}
    ${className}
  `.trim();

  const iconSize = 24;

  return (
    <div className={`${fullWidth ? 'w-full' : ''}`}>
      {label && (
        <label className="block text-elder-h3 mb-2">
          {label}
        </label>
      )}
      
      <div className="relative">
        {Icon && (
          <div className={`absolute inset-y-0 ${iconPosition === 'left' ? 'left-0' : 'right-0'} flex items-center ${iconPosition === 'left' ? 'pl-4' : 'pr-4'} pointer-events-none`}>
            <Icon 
              size={iconSize} 
              className={`${error ? 'text-coral-500' : 'text-lavender-400'}`}
            />
          </div>
        )}
        
        <input
          ref={ref}
          className={inputClasses}
          {...props}
        />
      </div>
      
      {error && (
        <p className="mt-2 text-sm-elder text-coral-600" role="alert">
          {error}
        </p>
      )}
      
      {helperText && !error && (
        <p className="mt-2 text-elder-caption">
          {helperText}
        </p>
      )}
    </div>
  );
});