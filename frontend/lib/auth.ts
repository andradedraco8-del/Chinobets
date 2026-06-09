"use client";

// Cliente de autenticación (lado navegador). Guarda el token JWT en
// localStorage y ofrece login, registro, logout y consulta del usuario.

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const TOKEN_KEY = "protipster_token";
const EMAIL_KEY = "protipster_email";
const ROLE_KEY = "protipster_role";

export interface AuthState {
  email: string | null;
  role: string | null;
  token: string | null;
}

export function getAuth(): AuthState {
  if (typeof window === "undefined") return { email: null, role: null, token: null };
  return {
    token: localStorage.getItem(TOKEN_KEY),
    email: localStorage.getItem(EMAIL_KEY),
    role: localStorage.getItem(ROLE_KEY),
  };
}

export function logout(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(EMAIL_KEY);
  localStorage.removeItem(ROLE_KEY);
  // Avisa a otros componentes (Header) del cambio de sesión.
  window.dispatchEvent(new Event("auth-changed"));
}

export async function login(email: string, password: string): Promise<{ ok: boolean; error?: string }> {
  try {
    // El backend usa OAuth2PasswordRequestForm → datos de formulario, no JSON.
    const body = new URLSearchParams();
    body.set("username", email);
    body.set("password", password);

    const res = await fetch(`${API_URL}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      return { ok: false, error: data.detail || "Email o contraseña incorrectos" };
    }
    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem(EMAIL_KEY, email);
    localStorage.setItem(ROLE_KEY, data.role || "free");
    window.dispatchEvent(new Event("auth-changed"));
    return { ok: true };
  } catch {
    return { ok: false, error: "No se pudo conectar con el servidor. ¿Está el backend encendido?" };
  }
}

export async function register(
  email: string,
  password: string,
  fullName: string,
): Promise<{ ok: boolean; error?: string }> {
  try {
    const res = await fetch(`${API_URL}/api/auth/register`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      return { ok: false, error: data.detail || "No se pudo crear la cuenta" };
    }
    // Tras registrarse, inicia sesión automáticamente.
    return await login(email, password);
  } catch {
    return { ok: false, error: "No se pudo conectar con el servidor. ¿Está el backend encendido?" };
  }
}
