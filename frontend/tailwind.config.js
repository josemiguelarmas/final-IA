import defaultTheme from 'tailwindcss/defaultTheme';

/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        icesi: {
          blue: "#0047BA",
          dark: "#0C2340",
          light: "#E6EFFD",
          amber: "#FFB81C"
        },
        // Superficies y texto: neutros con tinte azul, alineados al azul institucional
        canvas: "#F4F6F9",
        paper: "#FFFFFF",
        rule: { DEFAULT: "#E2E6EC", strong: "#C9D0DA" },
        ink: { DEFAULT: "#14202E", soft: "#3B4756", muted: "#5A6675" },
        navy: "#0C2340",
        brand: { DEFAULT: "#0047BA", dark: "#00338A", tint: "#E8F0FC" },
        // Clasificación de notificaciones (todos >= 4.5:1 sobre blanco)
        act: { DEFAULT: "#A32A2A", tint: "#FBEEEE" },
        review: { DEFAULT: "#855300", tint: "#FBF4E3" },
        info: { DEFAULT: "#2A6A4C", tint: "#EAF4EE" },
      },
      fontFamily: {
        sans: ['"Public Sans Variable"', ...defaultTheme.fontFamily.sans],
        serif: ['"Source Serif 4 Variable"', ...defaultTheme.fontFamily.serif],
      },
    },
  },
  plugins: [],
}
