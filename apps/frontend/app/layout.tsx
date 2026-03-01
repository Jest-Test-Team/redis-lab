import type { Metadata } from "next";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  variable: "--font-jetbrains",
});

export const metadata: Metadata = {
  title: "蜃景交易所 | Mirage Exchange",
  description: "極端高併發虛擬情報拍賣 — 研究用",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-TW" className={jetbrains.variable}>
      <body className="min-h-screen terminal-scan antialiased">
        {children}
      </body>
    </html>
  );
}
