/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: { extend: { colors: { moneta: { black: '#000000', surface: '#202020', white: '#FFFFFF', soft: '#9BE49B', green: '#2BE82A' } }, fontFamily: { sans: ['Inter', 'sans-serif'] } } },
  plugins: [],
}
