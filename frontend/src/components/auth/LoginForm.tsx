"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "@/hooks/useAuth";
import type { LoginRequest } from "@/types/auth";

export function LoginForm() {
  const { login } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const { register, handleSubmit, formState } = useForm<LoginRequest>();

  async function onSubmit(values: LoginRequest) {
    setError(null);
    try {
      await login(values);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="form">
      {error && <p className="alert-error">{error}</p>}
      <label className="field">
        Email
        <input
          type="email"
          placeholder="you@example.com"
          className="control"
          {...register("email", { required: true })}
        />
      </label>
      <label className="field">
        Password
        <input
          type="password"
          placeholder="••••••••"
          className="control"
          {...register("password", { required: true })}
        />
      </label>
      <button type="submit" disabled={formState.isSubmitting} className="btn-primary">
        {formState.isSubmitting ? "Signing in..." : "Login"}
      </button>
    </form>
  );
}
