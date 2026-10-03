import type { Metadata } from "next";
import "./globals.css";
import "./cream-lavender.css";
import { DemoProvider } from "@/components/demo-context";

export const metadata: Metadata = {
  title: "Cukier w biegu — ten sam bieg, większy kontekst",
  description:
    "Połącz historię biegu z odczytami glukozy. Fakty, kontekst i pytania do lekarza. Prototyp HackYeah 2026 z danymi syntetycznymi.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="pl">
      <body>
        <DemoProvider>{children}</DemoProvider>
      </body>
    </html>
  );
}
