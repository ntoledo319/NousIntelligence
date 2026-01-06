const defaultTheme = require('tailwindcss/defaultTheme');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.html",
    "./static/js/**/*.js"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Nunito', 'Inter', ...defaultTheme.fontFamily.sans],
        serif: ['Lora', ...defaultTheme.fontFamily.serif],
      },
      colors: {
        primary: {
          DEFAULT: '#8da399', // Sage Green
          dark: '#6b8278',
          light: '#b4c5bc',
        },
        secondary: {
          DEFAULT: '#d6cbb6', // Warm Sand
          dark: '#b5aa94',
          light: '#e8e1d3',
        },
        brand: {
          light: '#b4c5bc', 
          DEFAULT: '#8da399',
          dark: '#6b8278',
        }
      },
      keyframes: {
        'fade-in-up': {
          '0%': {
            opacity: '0',
            transform: 'translateY(10px)'
          },
          '100%': {
            opacity: '1',
            transform: 'translateY(0)'
          },
        }
      },
      animation: {
        'fade-in-up': 'fade-in-up 0.3s ease-out'
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('tailwind-scrollbar'),
  ],
}