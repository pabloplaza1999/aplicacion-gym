/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans:    ['Barlow', 'sans-serif'],
        display: ['Bebas Neue', 'sans-serif'],
        mono:    ['JetBrains Mono', 'monospace'],
      },
      colors: {
        brand: {
          50:  '#fff1f1',
          100: '#ffe0e0',
          400: '#f87171',
          500: '#E02020',
          600: '#CC1B1B',
          700: '#a01515',
          900: '#5c0a0a',
        },
        energy: {
          400: '#fb923c',
          500: '#f97316',
        },
        success: {
          400: '#4ade80',
          500: '#22c55e',
        },
        surface: {
          DEFAULT: '#0A0A0F',
          card:    '#111118',
          raised:  '#1A1A24',
          border:  '#252532',
          muted:   '#35353F',
        }
      },
      boxShadow: {
        'brand-sm':   '0 0 12px rgba(224,32,32,0.25)',
        'brand-md':   '0 0 24px rgba(224,32,32,0.35)',
        'success-sm': '0 0 10px rgba(34,197,94,0.20)',
        'energy-sm':  '0 0 10px rgba(249,115,22,0.20)',
        'card-hover': '0 4px 24px rgba(0,0,0,0.40)',
      },
      animation: {
        'fade-up': 'fade-up 0.35s ease-out',
      },
      keyframes: {
        'fade-up': {
          from: { transform: 'translateY(6px)', opacity: '0' },
          to:   { transform: 'translateY(0)',   opacity: '1' },
        },
      }
    }
  },
  plugins: []
}
