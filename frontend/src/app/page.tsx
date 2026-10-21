"use client";

import Link from "next/link";
import { HealthPanel } from "@/components/health/HealthPanel";

export default function Home() {
  return (
    <main className="login-screen">
      <div className="card login-card home-card">
        <h1 className="login-title">Order Manager</h1>
        <p className="login-subtitle">Orders, queue and analytics</p>
        <div className="home-actions">
          <Link href="/login" className="btn-primary">
            Login
          </Link>
          <Link href="/orders" className="btn-secondary">
            Orders
          </Link>
          <Link href="/analytics" className="btn-secondary">
            Analytics
          </Link>
        </div>
        <HealthPanel />
      </div>
    </main>
  );
}
