import type {
  Alert,
  BacktestResult,
  DashboardStats,
  Match,
  Prediction,
  StakeResponse,
  ValueBet,
} from "./types";
import {
  mockAlerts,
  mockBacktest,
  mockPredictions,
  mockStats,
  mockValueBets,
} from "./mock";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

/**
 * Wrapper que intenta llamar al backend FastAPI y, si no está disponible
 * (p. ej. al arrancar sólo el frontend), cae a datos mock para que la
 * aplicación siga siendo navegable.
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

async function safePost<T>(path: string, body: unknown, fallback: T): Promise<T> {
  try {
    const res = await fetch(`${API_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  } catch {
    return fallback;
  }
}

export const api = {
  dashboardStats: () => safeFetch<DashboardStats>("/api/dashboard/stats", mockStats),
  predictions: () => safeFetch<Prediction[]>("/api/predictions", mockPredictions),
  prediction: (id: number) =>
    safeFetch<Prediction>(
      `/api/predictions/${id}`,
      mockPredictions.find((p) => p.match_id === id) ?? mockPredictions[0],
    ),
  matches: () => safeFetch<Match[]>("/api/matches", []),
  valueBets: () => safeFetch<ValueBet[]>("/api/value-bets?only_value=true", mockValueBets),
  alerts: () => safeFetch<Alert[]>("/api/alerts", mockAlerts),
  backtest: (params: Record<string, string | number | boolean>) => {
    const qs = new URLSearchParams(
      Object.entries(params).map(([k, v]) => [k, String(v)]),
    ).toString();
    return safeFetch<BacktestResult>(`/api/backtest/run?${qs}`, mockBacktest);
  },
  stake: (body: { model_prob: number; odds: number; bankroll: number; method: string }) =>
    safePost<StakeResponse>("/api/bankroll/stake", body, computeStakeFallback(body)),
};

/** Cálculo de Kelly en cliente como respaldo si el backend no responde. */
function computeStakeFallback(body: {
  model_prob: number;
  odds: number;
  bankroll: number;
  method: string;
}): StakeResponse {
  const b = body.odds - 1;
  const full = b > 0 ? Math.max(0, (b * body.model_prob - (1 - body.model_prob)) / b) : 0;
  const mult =
    body.method === "kelly" ? 1 : body.method === "aggressive" ? 0.75 : body.method === "conservative" ? 0.25 : 0.5;
  let frac = body.method === "fixed" ? 0.01 : full * mult;
  const capped = frac > 0.05;
  if (capped) frac = 0.05;
  return {
    method: body.method,
    kelly_fraction: Number(frac.toFixed(4)),
    stake: Number((body.bankroll * frac).toFixed(2)),
    stake_units: Number(((body.bankroll * frac) / (body.bankroll * 0.01)).toFixed(2)),
    risk_pct: Number((frac * 100).toFixed(2)),
    capped,
  };
}
