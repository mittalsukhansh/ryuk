import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ryuk — Intent before payment",
  description:
    "AI can choose. You stay in control. Evidence-backed commerce with deterministic financial authority.",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
