import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{js,ts,jsx,tsx}", "./components/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        mono: ["var(--font-jetbrains)", "ui-monospace", "monospace"],
      },
      colors: {
        terminal: {
          bg: "#0d0d0f",
          green: "#00ff88",
          cyan: "#00d4ff",
          amber: "#ffb800",
          red: "#ff3366",
        },
      },
    },
  },
  plugins: [],
};
export default config;
