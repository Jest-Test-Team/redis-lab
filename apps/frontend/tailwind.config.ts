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
        // Nothing X (from nothing-x-macos-main): black, dark grey surface, white/80% text
        nothing: {
          bg: "#000000",
          surface: "#1c1c1f",
          surfaceHover: "#252528",
          border: "#2a2a2e",
          text: "#ffffff",
          textMuted: "rgba(255,255,255,0.8)",
          muted: "#a1a1a6",
          pill: "#c2c2c4",
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
