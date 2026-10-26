import { getToken } from "@/lib/auth";

const API = process.env.NEXT_PUBLIC_API_URL;

// wrappers over regular fetch + api_json to avoid code duplicates in every query to api

export async function api(path: string, init?: RequestInit): Promise<Response> {
  const token = getToken();
  return fetch(`${API}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
}

export async function apiJson<T>(path: string, init?: RequestInit): Promise<T> { // <> can set type we expect from ts
  const res = await api(path, init);
  if (!res.ok) {
    const body = await res.json().catch(() => ({})); // error handler for promises
    const detail = typeof body?.detail === "string" ? body.detail : `HTTP ${res.status}`;
    throw new Error(detail);
  }
  return res.json();
}
