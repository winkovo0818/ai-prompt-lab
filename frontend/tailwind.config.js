/** @type {import('tailwindcss').Config} */
import colors from 'tailwindcss/colors'

export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Professional SaaS Palette (Modern & Grounded)
        brand: {
          50: '#f8fafc',
          100: '#f1f5f9',
          200: '#e2e8f0',
          300: '#cbd5e1',
          400: '#94a3b8',
          500: '#64748b', // Main secondary
          600: '#475569',
          700: '#334155',
          800: '#1e293b',
          900: '#0f172a',
          950: '#020617',
          primary: {
            DEFAULT: '#0f172a', // Deep dark for high contrast
            hover: '#1e293b',
          },
          accent: {
            DEFAULT: '#3b82f6', // Bright blue for action
            soft: '#eff6ff',
          }
        },
        // Neutral zinc for technical feel
        neutral: colors.zinc,
        
        // Semantic colors
        success: '#10b981',
        warning: '#f59e0b',
        danger: '#ef4444', 
        info: '#3b82f6',
      },
      fontFamily: {
        sans: ['"Inter"', '"Geist"', 'system-ui', '-apple-system', 'sans-serif'],
        mono: ['"JetBrains Mono"', '"IBM Plex Mono"', 'monospace'],
      },
      borderRadius: {
        'sm': '4px',
        'DEFAULT': '8px',
        'md': '10px',
        'lg': '12px',
        'xl': '16px',
        '2xl': '24px',
      },
      boxShadow: {
        'subtle': '0 1px 2px rgba(0, 0, 0, 0.05)',
        'soft': '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05)',
        'premium': '0 10px 15px -3px rgba(0, 0, 0, 0.04), 0 4px 6px -2px rgba(0, 0, 0, 0.02)',
        'modal': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
        'ring': '0 0 0 2px rgba(15, 23, 42, 0.1)',
      },
      backgroundImage: {
        'brand-gradient': 'linear-gradient(135deg, #0f172a 0%, #334155 100%)',
      }
    },
  },
  plugins: [],
}
