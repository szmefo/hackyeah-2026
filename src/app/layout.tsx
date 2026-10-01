import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "HackYeah 2026 | Starter",
  description: "Neutral workspace prepared before the HackYeah task reveal.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pl">
      <body>{children}</body>
    </html>
  );
}
