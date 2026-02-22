/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50:  '#f0f5f1',
          100: '#d6e8d9',
          200: '#add1b3',
          500: '#2d6a4f',
          600: '#1f5240',
          700: '#163d30',
        }
      }
    },
  },
  plugins: [],
}