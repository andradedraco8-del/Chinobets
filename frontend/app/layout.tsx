import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ProTipster AI · Terminal de análisis deportivo",
  description:
    "Análisis y pronósticos deportivos profesionales con detección de value bets, IA y gestión de bankroll.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-term-bg font-sans text-term-text antialiased">
        {children}
      </body>
    </html>
  );
}
