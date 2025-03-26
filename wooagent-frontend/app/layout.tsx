import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Toaster } from "sonner";

const inter = Inter({ subsets: ["latin"] });

// Navigation links
const navLinks = [
  { href: "/", label: "לוח בקרה", icon: "dashboard" },
  { href: "/agents", label: "סוכנים", icon: "robot" },
  { href: "/logs", label: "לוגים", icon: "log" },
  { href: "/trace", label: "צעדי ביצוע", icon: "trace" },
  { href: "/settings", label: "הגדרות", icon: "settings" }
];

export const metadata: Metadata = {
  title: "WooAgent - סוכן AI לניהול חנות WooCommerce",
  description: "ממשק ניהול לסוכן AI לניהול חנות WooCommerce",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="he" dir="rtl">
      <body className={inter.className}>
        {children}
        <Toaster position="top-left" expand={true} richColors />
      </body>
    </html>
  );
}
