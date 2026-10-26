"use client";

import Link from "next/link";
import { GuestOnly } from "@/components/auth/GuestOnly";
import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <GuestOnly>
      <main className="login-screen">
        <div className="card login-card">
          <h1 className="login-title">Order Manager</h1>
          <p className="login-subtitle">Sign in to open the dashboard</p>
          <LoginForm />
          <p className="auth-switch">
            No account yet? <Link href="/register">Register</Link>
          </p>
        </div>
      </main>
    </GuestOnly>
  );
}
