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
        nothing: {
          bg: "#0a0a0a",
          surface: "#141414",
          border: "#262626",
          text: "#f5f5f5",
          muted: "#a3a3a3",
        },
      },
      minHeight: {
        touch: "44px",
      },
    },
  },
  plugins: [],
};
export default config;
