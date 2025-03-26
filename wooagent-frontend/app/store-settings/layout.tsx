import React from "react";
import Sidebar from "@/components/shared/Sidebar";

export default function StoreSettingsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
} 