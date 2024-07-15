/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["templates/**/*.{html,js}"],
  theme: {
    extend: {
      fontFamily: {
        "megrim": ["Megrim", "cursive"],
        "raleway": ["Raleway", "sans-serif"]
      }
    },
  },
  plugins: [],
}

