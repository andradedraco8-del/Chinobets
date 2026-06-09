"use client";

import { useState } from "react";
import Header from "@/components/Header";
import { api } from "@/lib/api";
import { money } from "@/lib/format";
import type { StakeResponse } from "@/lib/types";

const METHODS = [
  { key: "kelly", label: "Kelly completo" },
  { key: "kelly_fraction", label: "Kelly fraccional (½)" },
  { key: "conservative", label: "Conservador (¼)" },
  { key: "aggressive", label: "Agresivo (¾)" },
  { key: "fixed", label: "Stake fijo" },
];

export default function BankrollPage() {
  const [bankroll, setBankroll] = useState(1000);
  const [odds, setOdds] = useState(2.1);
  const [prob, setProb] = useState(55);
  const [method, setMethod] = useState("kelly_fraction");
  const [result, setResult] = useState<StakeResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const edge = (prob / 100) * odds - 1;

  async function calculate() {
    setLoading(true);
    const r = await api.stake({ model_prob: prob / 100, odds, bankroll, method });
    setResult(r);
    setLoading(false);
  }

  return (
    <main>
      <Header />
      <div className="mx-auto max-w-4xl space-y-6 px-6 py-6">
        <a href="/" className="ticker hover:text-term-green">← volver al dashboard</a>
        <h1 className="font-mono text-xl font-bold text-term-text">Gestión de Bankroll</h1>

        <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
          {/* Configuración */}
          <section className="panel p-5 space-y-4">
            <h2 className="font-mono text-sm font-bold uppercase tracking-wider text-term-text">
              Calculadora de stake
            </h2>

            <Field label={`Bankroll: ${money(bankroll)}`}>
              <input type="range" min={100} max={10000} step={50} value={bankroll}
                onChange={(e) => setBankroll(Number(e.target.value))} className="w-full accent-term-green" />
            </Field>

            <Field label={`Probabilidad estimada: ${prob}%`}>
              <input type="range" min={1} max={99} value={prob}
                onChange={(e) => setProb(Number(e.target.value))} className="w-full accent-term-green" />
            </Field>

            <Field label="Cuota decimal">
              <input type="number" min={1.01} step={0.01} value={odds}
                onChange={(e) => setOdds(Number(e.target.value))}
                className="w-full rounded border border-term-border bg-term-bg px-3 py-2 font-mono text-term-text outline-none focus:border-term-green" />
            </Field>

            <Field label="Método de staking">
              <select value={method} onChange={(e) => setMethod(e.target.value)}
                className="w-full rounded border border-term-border bg-term-bg px-3 py-2 font-mono text-term-text outline-none focus:border-term-green">
                {METHODS.map((m) => <option key={m.key} value={m.key}>{m.label}</option>)}
              </select>
            </Field>

            <div className="rounded bg-term-bg/60 p-3 font-mono text-sm">
              <div className="flex justify-between">
                <span className="text-term-muted">Edge (ventaja)</span>
                <span className={edge >= 0 ? "text-term-green" : "text-term-red"}>
                  {edge >= 0 ? "+" : ""}{(edge * 100).toFixed(1)}%
                </span>
              </div>
            </div>

            <button onClick={calculate} disabled={loading}
              className="w-full rounded bg-term-green/20 py-2 font-mono text-sm font-bold uppercase tracking-wider text-term-green hover:bg-term-green/30 disabled:opacity-50">
              {loading ? "Calculando…" : "Calcular stake óptimo"}
            </button>
          </section>

          {/* Resultado */}
          <section className="panel p-5">
            <h2 className="mb-4 font-mono text-sm font-bold uppercase tracking-wider text-term-text">
              Recomendación
            </h2>
            {result ? (
              <div className="space-y-3 font-mono">
                <Big label="Stake recomendado" value={money(result.stake)} accent />
                <Row label="Unidades" value={`${result.stake_units.toFixed(2)} u`} />
                <Row label="Fracción Kelly" value={`${(result.kelly_fraction * 100).toFixed(2)}%`} />
                <Row label="Riesgo del bankroll" value={`${result.risk_pct.toFixed(2)}%`} />
                <Row label="Método" value={result.method} />
                {result.capped && (
                  <div className="rounded border border-term-amber/40 bg-term-amber/10 p-2 text-xs text-term-amber">
                    ⚠ Limitado al tope de exposición (5%) para proteger el bankroll.
                  </div>
                )}
              </div>
            ) : (
              <p className="text-sm text-term-muted">
                Ajusta los parámetros y pulsa «Calcular» para obtener el tamaño de apuesta
                óptimo según el criterio de Kelly con tope de exposición del 5%.
              </p>
            )}
          </section>
        </div>
      </div>
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
function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between border-b border-term-border/40 pb-1.5 text-sm">
      <span className="text-term-muted">{label}</span>
      <span className="text-term-text">{value}</span>
    </div>
  );
}
function Big({ label, value, accent }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="rounded bg-term-bg/60 p-3">
      <div className="ticker">{label}</div>
      <div className={`text-2xl font-bold ${accent ? "text-term-green" : "text-term-text"}`}>{value}</div>
    </div>
  );
}
