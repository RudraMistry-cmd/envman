/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        surface: {
          DEFAULT: '#18181b',
          elevated: '#27272a',
          muted: '#3f3f46',
        },
        glow: {
          blue: 'rgba(59, 130, 246, 0.15)',
          violet: 'rgba(139, 92, 246, 0.15)',
          green: 'rgba(34, 197, 94, 0.12)',
          red: 'rgba(239, 68, 68, 0.12)',
        },
      },
      boxShadow: {
        'glow-sm': '0 0 20px rgba(59, 130, 246, 0.15)',
        'glow': '0 0 40px rgba(59, 130, 246, 0.15)',
        'glow-lg': '0 0 60px rgba(59, 130, 246, 0.2)',
        'glow-violet': '0 0 40px rgba(139, 92, 246, 0.15)',
        'glow-green': '0 0 30px rgba(34, 197, 94, 0.12)',
        'glow-red': '0 0 30px rgba(239, 68, 68, 0.12)',
        'glass': '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255,255,255,0.05)',
      },
      borderRadius: {
        'card': '14px',
      },
      animation: {
        'fade-in': 'fadeIn 500ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-up': 'slideUp 500ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'slide-down': 'slideDown 300ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'scale-in': 'scaleIn 400ms cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
        'check-draw': 'checkDraw 400ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'step-enter': 'stepEnter 400ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'screen-enter': 'screenEnter 400ms cubic-bezier(0.16, 1, 0.3, 1) forwards',
        'spin-slow': 'spin 3s linear infinite',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(16px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideDown: {
          '0%': { opacity: '0', transform: 'translateY(-8px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        scaleIn: {
          '0%': { opacity: '0', transform: 'scale(0.8)' },
          '100%': { opacity: '1', transform: 'scale(1)' },
        },
        pulseGlow: {
          '0%, 100%': { opacity: '0.4', transform: 'scale(1)' },
          '50%': { opacity: '0.8', transform: 'scale(1.05)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        checkDraw: {
          '0%': { strokeDashoffset: '24' },
          '100%': { strokeDashoffset: '0' },
        },
        stepEnter: {
          '0%': { opacity: '0', transform: 'translateX(-12px)' },
          '100%': { opacity: '1', transform: 'translateX(0)' },
        },
        screenEnter: {
          '0%': { opacity: '0', transform: 'translateY(8px) scale(0.98)' },
          '100%': { opacity: '1', transform: 'translateY(0) scale(1)' },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'SFMono-Regular', 'monospace'],
      },
    },
  },
  plugins: [],
}
