const TOKEN_KEY = "access_token";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY); // get "access_token key from localStorage"
}

export function setToken(token: string): void {
  localStorage.setItem(TOKEN_KEY, token); // set "access_token" to localStorage
}

export function clearToken(): void {
  localStorage.removeItem(TOKEN_KEY);
}
