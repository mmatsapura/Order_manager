// Service analog
"use client";

import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { setToken, clearToken } from "@/lib/auth";
import type { LoginRequest, TokenResponse } from "@/types/auth";

export function useAuth() {
    const router = useRouter();

    async function login(body: LoginRequest) {
        const res = await api("/auth/login", {
            method: "POST",
            body: JSON.stringify(body),
            });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.detail ?? "Login failed");
        }
        const data: TokenResponse = await res.json();
        setToken(data.access_token);
        router.push("/orders");
      }

    async function logout() {
        try {
            await api("/auth/logout", { method:"POST"});
        } finally {
            clearToken();
            router.push("/login");
        }
        
    }
        return { login, logout };
    }