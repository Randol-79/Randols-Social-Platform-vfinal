/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    // Mobile-first breakpoints
    screens: {
      'xs': '375px',
      'sm': '640px',
      'md': '768px',
      'lg': '1024px',
      'xl': '1280px',
      '2xl': '1536px',
      // Touch device detection
      'touch': { 'raw': '(hover: none)' },
      'pointer': { 'raw': '(hover: hover)' },
      // Orientation
      'portrait': { 'raw': '(orientation: portrait)' },
      'landscape': { 'raw': '(orientation: landscape)' },
      // Safe areas for notched devices
      'safe-top': { 'raw': '(padding-top: env(safe-area-inset-top))' },
      'safe-bottom': { 'raw': '(padding-bottom: env(safe-area-inset-bottom))' },
    },
    extend: {
      // Touch-friendly sizing
      spacing: {
        'safe-top': 'env(safe-area-inset-top)',
        'safe-bottom': 'env(safe-area-inset-bottom)',
        'safe-left': 'env(safe-area-inset-left)',
        'safe-right': 'env(safe-area-inset-right)',
        'touch': '44px', // Minimum touch target size
        'touch-lg': '48px',
      },
      // Minimum touch target sizes
      minHeight: {
        'touch': '44px',
        'touch-lg': '48px',
      },
      minWidth: {
        'touch': '44px',
        'touch-lg': '48px',
      },
      colors: {
        // Louisiana-inspired color palette
        cajun: {
          red: '#C0152F',
          'red-dark': '#8B0D21',
          'red-light': '#E8435A',
        },
        roux: {
          DEFAULT: '#A84B2F',
          light: '#C96A4A',
          dark: '#7A3520',
          chocolate: '#5C3317',
        },
        bayou: {
          DEFAULT: '#32808D',
          light: '#4BA3B2',
          dark: '#245D67',
          deep: '#1A4750',
        },
        gold: {
          louisiana: '#D4AF37',
          light: '#E8C962',
          dark: '#B8941F',
        },
        cream: {
          DEFAULT: '#F5F0E6',
          warm: '#FDF8EE',
          dark: '#E8E0D0',
        },
        marsh: {
          DEFAULT: '#4A7C59',
          light: '#6B9B78',
          dark: '#3A6147',
        },
        night: {
          DEFAULT: '#2C1810',
          light: '#4A2E24',
          dark: '#1A0E0A',
        },
      },
      fontFamily: {
        display: ['Playfair Display', 'serif'],
        body: ['Source Sans Pro', 'sans-serif'],
        accent: ['Dancing Script', 'cursive'],
      },
      backgroundImage: {
        'cajun-gradient': 'linear-gradient(135deg, #C0152F 0%, #A84B2F 100%)',
        'bayou-gradient': 'linear-gradient(135deg, #32808D 0%, #245D67 100%)',
        'gold-gradient': 'linear-gradient(135deg, #D4AF37 0%, #B8941F 100%)',
        'night-gradient': 'linear-gradient(180deg, #2C1810 0%, #1A0E0A 100%)',
      },
      boxShadow: {
        'cajun': '0 4px 20px -2px rgba(192, 21, 47, 0.25)',
        'bayou': '0 4px 20px -2px rgba(50, 128, 141, 0.25)',
        'gold': '0 4px 20px -2px rgba(212, 175, 55, 0.25)',
        'warm': '0 4px 20px -2px rgba(168, 75, 47, 0.15)',
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-out',
        'slide-up': 'slideUp 0.5s ease-out',
        'slide-in-right': 'slideInRight 0.3s ease-out',
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-gentle': 'bounceGentle 2s infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideInRight: {
          '0%': { opacity: '0', transform: 'translateX(20px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        bounceGentle: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-5px)' },
        },
      },
    },
  },
  plugins: [],
  // Future-proofing
  future: {
    hoverOnlyWhenSupported: true,
  },
}
