/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        pharmacy: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },
        slate: {
          850: '#172033',
          950: '#0b0f19',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
      },
      boxShadow: {
        'glow-emerald': '0 0 20px -5px rgba(16, 185, 129, 0.3)',
        'glow-rose': '0 0 20px -5px rgba(244, 63, 94, 0.3)',
        'glow-amber': '0 0 20px -5px rgba(245, 158, 11, 0.3)',
        'glow-blue': '0 0 20px -5px rgba(59, 130, 246, 0.3)',
      }
    },
  },
  plugins: [],
}
