/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        acidtech: {
          primary: '#667eea',
          secondary: '#764ba2',
          accent: '#f093fb',
          dark: '#2d3748',
          light: '#f7fafc'
        }
      }
    },
  },
  plugins: [],
  safelist: [
    'bg-acidtech-primary',
    'bg-acidtech-secondary',
    'text-acidtech-primary'
  ]
}

