/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: {
            50: '#f0f4f9',
            100: '#d9e2ec',
            500: '#1d3557',
            800: '#0b2545',
            900: '#06172e',
          },
          saffron: {
            50: '#fff4e6',
            100: '#ffe3c2',
            500: '#e65100',
            600: '#d84315',
            700: '#bf360c',
          },
          green: {
            50: '#e8f5e9',
            100: '#c8e6c9',
            600: '#2e7d32',
            700: '#1b5e20',
          },
          cream: '#faf8f5',
          ash: '#f4f6f9',
          border: '#e2e8f0',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
};
