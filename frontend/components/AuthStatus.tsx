"use client";

import { useEffect, useState } from "react";
import { getAuth, logout } from "@/lib/auth";

export default function AuthStatus() {
  const [email, setEmail] = useState<string | null>(null);
  const [role, setRole] = useState<string | null>(null);

  useEffect(() => {
    const sync = () => {
      const a = getAuth();
      setEmail(a.email);
      setRole(a.role);
    };
    sync();
    window.addEventListener("auth-changed", sync);
    return () => window.removeEventListener("auth-changed", sync);
  }, []);

  if (!email) {
    return (
      <a
        href="/login"
        className="pill bg-term-green/15 text-term-green hover:bg-term-green/25"
      >
        Iniciar sesión
      </a>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <span className="pill bg-term-border uppercase text-term-muted">{role || "free"}</span>
      <span className="hidden font-mono text-xs text-term-text sm:inline">{email}</span>
      <button
        onClick={logout}
        className="pill bg-term-red/15 text-term-red hover:bg-term-red/25"
      >
        Salir
      </button>
    </div>
  );
}
