/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Elderly-friendly color palette
        lavender: {
          50: '#F8F6FB',
          100: '#E8E0F0',
          200: '#C8B8DB',
          300: '#9B7EBD',
          400: '#8A68AC',
          500: '#7952A0',
          600: '#6A4490',
          700: '#5B3680',
          800: '#4C2E6B',
          900: '#3D2556',
        },
        cream: {
          50: '#FDFCFA',
          100: '#FBF7F0',
          200: '#F7F0E8',
          300: '#F2E7D9',
          400: '#EDDCC8',
          500: '#E7D0B6',
          600: '#DFC2A3',
          700: '#D5B28F',
          800: '#C9A07A',
          900: '#BB8C64',
        },
        sage: {
          50: '#F5F7F2',
          100: '#E8ECE0',
          200: '#D2D9C3',
          300: '#B5C29E',
          400: '#9BAA7C',
          500: '#87A96B',
          600: '#739257',
          700: '#5F7A47',
          800: '#4E6339',
          900: '#3F502D',
        },
        coral: {
          50: '#FFF2F4',
          100: '#FFE0E5',
          200: '#FFC7CF',
          300: '#FF9EAF',
          400: '#FF8B94',
          500: '#FF6B7A',
          600: '#FF4D60',
          700: '#E6334A',
          800: '#CC1F38',
          900: '#B30F2A',
        },
        // Accessibility colors
        highContrast: {
          dark: '#000000',
          light: '#FFFFFF',
        }
      },
      fontSize: {
        // Elderly-friendly font sizes
        'xs-elder': ['18px', { lineHeight: '24px' }],
        'sm-elder': ['20px', { lineHeight: '28px' }],
        'base-elder': ['24px', { lineHeight: '32px' }],
        'lg-elder': ['28px', { lineHeight: '36px' }],
        'xl-elder': ['32px', { lineHeight: '40px' }],
        '2xl-elder': ['36px', { lineHeight: '44px' }],
        '3xl-elder': ['40px', { lineHeight: '48px' }],
        '4xl-elder': ['48px', { lineHeight: '56px' }],
      },
      spacing: {
        // Large touch targets
        'touch-sm': '48px',
        'touch-md': '60px',
        'touch-lg': '80px',
        'touch-xl': '100px',
      },
      animation: {
        'gentle-pulse': 'gentle-pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slide-up 0.3s ease-out',
        'slide-down': 'slide-down 0.3s ease-out',
        'fade-in': 'fade-in 0.2s ease-out',
        'scale-in': 'scale-in 0.2s ease-out',
        'float': 'float 3s ease-in-out infinite',
      },
      keyframes: {
        'gentle-pulse': {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0.7' },
        },
        'slide-up': {
          '0%': { transform: 'translateY(100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'slide-down': {
          '0%': { transform: 'translateY(-100%)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'fade-in': {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
        'float': {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
      },
      fontFamily: {
        'elder': ['Atkinson Hyperlegible', 'Inter', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'elder': '12px',
        'elder-lg': '16px',
        'elder-xl': '20px',
      },
      boxShadow: {
        'elder': '0 4px 6px -1px rgba(155, 126, 189, 0.1), 0 2px 4px -1px rgba(155, 126, 189, 0.06)',
        'elder-lg': '0 10px 15px -3px rgba(155, 126, 189, 0.1), 0 4px 6px -2px rgba(155, 126, 189, 0.05)',
        'elder-xl': '0 20px 25px -5px rgba(155, 126, 189, 0.1), 0 10px 10px -5px rgba(155, 126, 189, 0.04)',
      },
    },
  },
  plugins: [],
}