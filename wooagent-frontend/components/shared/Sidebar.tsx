"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

interface MenuItem {
  href: string;
  label: string;
  icon: string;
}

const menuItems: MenuItem[] = [
  { href: "/dashboard", label: "דשבורד", icon: "🏠" },
  { href: "/chat", label: "צ'אט", icon: "💬" },
  { href: "/store-settings", label: "הגדרות חנות", icon: "🛒" },
  { href: "/agent-settings", label: "הגדרות סוכן", icon: "⚙️" },
  { href: "/training", label: "אימון", icon: "🧠" },
  { href: "/logs", label: "לוגים", icon: "📋" },
  { href: "/trace", label: "צעדי ביצוע", icon: "🔍" },
  { href: "/analytics", label: "אנליטיקה", icon: "📊" },
  { href: "/backup", label: "גיבוי ושחזור", icon: "💾" },
  { href: "/help", label: "עזרה", icon: "❓" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="h-screen border-l p-4 space-y-4 w-64 bg-background">
      <div className="text-2xl font-bold py-4 text-center">WooAgent</div>
      <nav className="space-y-2">
        {menuItems.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors text-muted-foreground",
                isActive ? "bg-secondary text-foreground" : "hover:bg-secondary/50"
              )}
            >
              <span role="img" aria-label={item.label}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>
    </div>
  );
} 