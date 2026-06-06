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
        surface: {
          DEFAULT: '#08080A',
          card:    '#111115',
          raised:  '#18181E',
          border:  '#252530',
          muted:   '#35353F',
        }
      },
      boxShadow: {
        'brand-sm': '0 0 12px rgba(224,32,32,0.25)',
        'brand-md': '0 0 24px rgba(224,32,32,0.35)',
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
