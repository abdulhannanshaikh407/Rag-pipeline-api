/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        'surface-dim': '#080d1a',
        'surface': '#0f1629',
        'surface-2': '#162035',
        'primary': '#6C63FF',
        'primary-container': '#3622ca',
      },
    },
  },
  plugins: [],
};
