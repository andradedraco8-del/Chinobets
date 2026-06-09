"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { login, register } from "@/lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("demo@protipster.ai");
  const [password, setPassword] = useState("demo1234");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    const res =
      mode === "login"
        ? await login(email, password)
        : await register(email, password, fullName);
    setLoading(false);
    if (res.ok) {
      router.push("/");
    } else {
      setError(res.error || "Error desconocido");
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-term-bg px-4">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="mb-6 flex items-center justify-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded bg-term-green/15 font-mono text-xl text-term-green shadow-glow">
            ▲
          </div>
          <div className="font-mono text-xl font-bold tracking-wider text-term-text">
            ProTipster<span className="text-term-green"> AI</span>
          </div>
        </div>

        <div className="panel p-6">
          {/* Pestañas */}
          <div className="mb-5 flex rounded border border-term-border p-1 font-mono text-xs uppercase">
            <button
              onClick={() => setMode("login")}
              className={`flex-1 rounded py-2 ${mode === "login" ? "bg-term-green/20 text-term-green" : "text-term-muted"}`}
            >
              Iniciar sesión
            </button>
            <button
              onClick={() => setMode("register")}
              className={`flex-1 rounded py-2 ${mode === "register" ? "bg-term-green/20 text-term-green" : "text-term-muted"}`}
            >
              Crear cuenta
            </button>
          </div>

          <form onSubmit={submit} className="space-y-4">
            {mode === "register" && (
              <Field label="Nombre">
                <input
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="input"
                  placeholder="Tu nombre"
                />
              </Field>
            )}
            <Field label="Email">
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="tucorreo@ejemplo.com"
              />
            </Field>
            <Field label="Contraseña">
              <input
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="••••••••"
              />
            </Field>

            {error && (
              <div className="rounded border border-term-red/40 bg-term-red/10 p-2 text-xs text-term-red">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded bg-term-green/20 py-2.5 font-mono text-sm font-bold uppercase tracking-wider text-term-green hover:bg-term-green/30 disabled:opacity-50"
            >
              {loading ? "Procesando…" : mode === "login" ? "Entrar" : "Crear cuenta y entrar"}
            </button>
          </form>

          {mode === "login" && (
            <p className="mt-4 text-center text-[11px] text-term-muted">
              Cuenta de prueba: <span className="text-term-green">demo@protipster.ai</span> / demo1234
            </p>
          )}
        </div>

        <a href="/" className="ticker mt-4 block text-center hover:text-term-green">
          ← continuar sin iniciar sesión
        </a>
      </div>

      <style jsx>{`
        .input {
          width: 100%;
          border-radius: 0.375rem;
          border: 1px solid #1c2b25;
          background: #0a0e0d;
          padding: 0.6rem 0.75rem;
          font-family: monospace;
          color: #e6f1ec;
          outline: none;
        }
        .input:focus {
          border-color: #10b981;
        }
      `}</style>
    </main>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="ticker mb-1 block">{label}</label>
      {children}
    </div>
  );
}
