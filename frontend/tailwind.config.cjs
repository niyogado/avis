/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          dark: '#0E0E0C',
          light: '#FAFAF8'
        },
        panel: {
          dark: '#191915',
          light: '#FFFFFF'
        },
        text: {
          primary: '#F3F1E9',
          muted: 'rgba(243, 241, 233, 0.6)'
        },
        textLight: {
          primary: '#15150F',
          muted: 'rgba(21, 21, 15, 0.6)'
        },
        border: {
          dark: 'rgba(243, 241, 233, 0.12)',
          light: 'rgba(21, 21, 15, 0.12)'
        },
        accent: {
          DEFAULT: '#D96A1C',
          hover: 'rgba(217, 106, 28, 0.85)',
          glow: 'rgba(217, 106, 28, 0.25)'
        }
      },
      spacing: {
        sidebar: '260px'
      }
    },
  },
  plugins: [],
}
