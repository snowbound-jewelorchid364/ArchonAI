import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ARCHON - AI Architecture Co-Pilot",
  description: "Autonomous AI architecture reviews for startups",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50 text-gray-900 antialiased">
        {children}
      </body>
    </html>
  );
}
