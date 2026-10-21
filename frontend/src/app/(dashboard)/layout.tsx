import type { ReactNode } from "react";
import { AuthGuard } from "@/components/layout/AuthGuard";
import { Navbar } from "@/components/layout/Navbar";

export default function DashboardLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <AuthGuard>
      <div className="dashboard">
        <Navbar />
        {children}
      </div>
    </AuthGuard>
  );
}
