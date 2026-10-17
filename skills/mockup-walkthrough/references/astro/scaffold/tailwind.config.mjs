/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: 'var(--token-color-primary)',
      },
      spacing: {
        sm: 'var(--token-spacing-sm)',
      },
    },
  },
  plugins: [],
};
