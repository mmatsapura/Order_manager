"use client";

import { LoginForm } from "@/components/auth/LoginForm";

export default function LoginPage() {
  return (
    <main className="login-screen">
      <div className="card login-card">
        <h1 className="login-title">Order Manager</h1>
        <p className="login-subtitle">Sign in to open the dashboard</p>
        <LoginForm />
      </div>
    </main>
  );
}
