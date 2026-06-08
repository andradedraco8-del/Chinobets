import type { DashboardStats, Match, Prediction, ValueBet } from "./types";
import { mockPredictions, mockStats, mockValueBets } from "./mock";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Wrapper que intenta llamar al backend FastAPI y, si no está disponible
 * (p. ej. al arrancar sólo el frontend), cae a datos mock para que el
 * dashboard siga siendo navegable.
 */
async function safeFetch<T>(path: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_URL}${path}`, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export const api = {
  dashboardStats: () => safeFetch<DashboardStats>("/api/dashboard/stats", mockStats),
  predictions: () => safeFetch<Prediction[]>("/api/predictions", mockPredictions),
  matches: () => safeFetch<Match[]>("/api/matches", []),
  valueBets: () => safeFetch<ValueBet[]>("/api/value-bets?only_value=true", mockValueBets),
};
