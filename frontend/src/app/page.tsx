"use client";

import Link from "next/link";
import { GuestOnly } from "@/components/auth/GuestOnly";

export default function Home() {
  return (
    <GuestOnly>
      <main className="login-screen">
        <div className="card login-card home-card">
          <h1 className="login-title">Order Manager</h1>
          <p className="login-subtitle">Sign in or create an account</p>
          <div className="home-actions">
            <Link href="/login" className="btn-primary">
              Login
            </Link>
            <Link href="/register" className="btn-secondary">
              Register
            </Link>
          </div>
        </div>
      </main>
    </GuestOnly>
  );
}
