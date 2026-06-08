import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Paleta "terminal de trading": negro, verde, blanco.
        term: {
          bg: "#0a0e0d",        // fondo principal
          panel: "#101614",     // paneles
          border: "#1c2b25",    // bordes
          green: "#10b981",     // verde principal (positivo / value)
          greenDim: "#0f8a63",
          red: "#ef4444",       // negativo / riesgo alto
          amber: "#f59e0b",     // alerta / riesgo medio
          text: "#e6f1ec",      // texto claro
          muted: "#6b8079",     // texto secundario
        },
      },
      fontFamily: {
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      boxShadow: {
        glow: "0 0 18px rgba(16,185,129,0.15)",
      },
    },
  },
  plugins: [],
};

export default config;
