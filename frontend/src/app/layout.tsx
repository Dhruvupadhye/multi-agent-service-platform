import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/layout/app-shell";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Multi-Agent Service Platform",
  description:
    "Autonomous AI-powered office assistant for emails, documents, calendar, and task orchestration.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="h-full">
      <body className={`${inter.className} min-h-screen bg-slate-50 dark:bg-slate-950`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
