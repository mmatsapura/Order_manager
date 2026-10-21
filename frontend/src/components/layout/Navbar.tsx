"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useAuth } from "@/hooks/useAuth";
import { getToken } from "@/lib/auth";

export function Navbar() {
  const { logout } = useAuth();
  const [hasToken, setHasToken] = useState(false);

  useEffect(() => {
    setHasToken(Boolean(getToken()));
  }, []);

  return (
    <nav className="nav">
      <div className="nav-inner">
        <span className="nav-brand">Order Manager</span>
        <Link href="/orders" className="nav-link">
          Orders
        </Link>
        <Link href="/orders/new" className="nav-link">
          New order
        </Link>
        <Link href="/analytics" className="nav-link">
          Analytics
        </Link>
        <Link href="/health" className="nav-link">
          Health
        </Link>
        {hasToken ? (
          <button type="button" className="nav-link nav-login" onClick={() => logout()}>
            Logout
          </button>
        ) : (
          <Link href="/login" className="nav-link nav-login">
            Login
          </Link>
        )}
      </div>
    </nav>
  );
}
