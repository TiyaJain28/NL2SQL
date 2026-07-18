/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef4ff",
          100: "#dbe6ff",
          500: "#3b6fed",
          600: "#2c56c9",
          700: "#22449e",
        },
      },
    },
  },
  plugins: [],
};
