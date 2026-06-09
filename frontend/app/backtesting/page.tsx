"use client";

import { useEffect, useState } from "react";
import Header from "@/components/Header";
import GrowthChart from "@/components/GrowthChart";
import StatCard from "@/components/StatCard";
import { api } from "@/lib/api";
import { money, signed } from "@/lib/format";
import type { BacktestResult, MarketBreakdown } from "@/lib/types";

const METHODS = ["kelly", "kelly_fraction", "conservative", "aggressive", "fixed"];

export default function BacktestingPage() {
  const [initial, setInitial] = useState(1000);
  const [method, setMethod] = useState("kelly_fraction");
  const [edge, setEdge] = useState(2);
  const [n, setN] = useState(600);
  const [result, setResult] = useState<BacktestResult | null>(null);
  const [loading, setLoading] = useState(false);

  async function run() {
    setLoading(true);
    const r = await api.backtest({
      initial_bankroll: initial,
      method,
      edge_threshold: edge / 100,
      n,
      compounding: true,
    });
    setResult(r);
    setLoading(false);
  }

  useEffect(() => {
    run();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <main>
      <Header />
      <div className="mx-auto max-w-7xl space-y-6 px-6 py-6">
        <a href="/" className="ticker hover:text-term-green">← volver al dashboard</a>
        <h1 className="font-mono text-xl font-bold text-term-text">Backtesting de estrategias</h1>

        {/* Controles */}
        <section className="panel grid grid-cols-1 gap-4 p-5 md:grid-cols-4">
          <div>
            <label className="ticker mb-1 block">Bankroll inicial: {money(initial)}</label>
            <input type="range" min={500} max={10000} step={100} value={initial}
              onChange={(e) => setInitial(Number(e.target.value))} className="w-full accent-term-green" />
          </div>
          <div>
            <label className="ticker mb-1 block">Edge mínimo: {edge}%</label>
            <input type="range" min={0} max={15} value={edge}
              onChange={(e) => setEdge(Number(e.target.value))} className="w-full accent-term-green" />
          </div>
          <div>
            <label className="ticker mb-1 block">Muestra: {n} apuestas</label>
            <input type="range" min={100} max={3000} step={100} value={n}
              onChange={(e) => setN(Number(e.target.value))} className="w-full accent-term-green" />
          </div>
          <div className="flex items-end gap-2">
            <select value={method} onChange={(e) => setMethod(e.target.value)}
              className="flex-1 rounded border border-term-border bg-term-bg px-2 py-2 font-mono text-xs text-term-text outline-none focus:border-term-green">
              {METHODS.map((m) => <option key={m} value={m}>{m}</option>)}
            </select>
            <button onClick={run} disabled={loading}
              className="rounded bg-term-green/20 px-4 py-2 font-mono text-xs font-bold uppercase text-term-green hover:bg-term-green/30 disabled:opacity-50">
              {loading ? "…" : "Run"}
            </button>
          </div>
        </section>

        {result && (
          <>
            <section className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
              <StatCard label="ROI" value={`${result.roi.toFixed(2)}%`} delta={signed(result.roi)} positive={result.roi >= 0} />
              <StatCard label="Yield" value={`${result.yield_pct.toFixed(2)}%`} delta={signed(result.yield_pct)} positive={result.yield_pct >= 0} />
              <StatCard label="Win Rate" value={`${result.win_rate.toFixed(1)}%`} hint={`${result.wins}G/${result.losses}P`} />
              <StatCard label="Max Drawdown" value={`${result.max_drawdown_pct.toFixed(1)}%`} hint={money(result.max_drawdown)} />
              <StatCard label="Bankroll final" value={money(result.final_bankroll)} delta={signed(result.profit)} positive={result.profit >= 0} />
              <StatCard label="Racha perd." value={`${result.longest_losing_streak}`} hint={`${result.total_bets} apuestas`} />
            </section>

            <section className="panel p-4">
              <h2 className="mb-2 font-mono text-sm font-bold uppercase tracking-wider text-term-text">
                Equity curve
              </h2>
              <GrowthChart data={result.equity_curve} />
            </section>

            <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <BreakdownTable title="Rentabilidad por mercado" data={result.by_market} />
              <BreakdownTable title="Rentabilidad por deporte" data={result.by_sport} />
            </section>
          </>
        )}
      </div>
    </main>
  );
}

function BreakdownTable({ title, data }: { title: string; data: Record<string, MarketBreakdown> }) {
  return (
    <div className="panel overflow-hidden">
      <div className="border-b border-term-border px-4 py-3">
        <h2 className="font-mono text-sm font-bold uppercase tracking-wider text-term-text">{title}</h2>
      </div>
      <table className="w-full text-sm">
        <thead>
          <tr className="ticker border-b border-term-border text-left">
            <th className="px-4 py-2 font-medium">Categoría</th>
            <th className="px-4 py-2 text-right font-medium">Apuestas</th>
            <th className="px-4 py-2 text-right font-medium">Win%</th>
            <th className="px-4 py-2 text-right font-medium">Beneficio</th>
            <th className="px-4 py-2 text-right font-medium">ROI</th>
          </tr>
        </thead>
        <tbody className="font-mono">
          {Object.entries(data).map(([k, v]) => (
            <tr key={k} className="border-b border-term-border/50">
              <td className="px-4 py-2 capitalize text-term-text">{k}</td>
              <td className="px-4 py-2 text-right text-term-muted">{v.bets}</td>
              <td className="px-4 py-2 text-right text-term-muted">{v.win_rate}%</td>
              <td className={`px-4 py-2 text-right ${v.profit >= 0 ? "text-term-green" : "text-term-red"}`}>
                {v.profit >= 0 ? "+" : ""}{v.profit.toFixed(2)}
              </td>
              <td className={`px-4 py-2 text-right font-bold ${v.roi >= 0 ? "text-term-green" : "text-term-red"}`}>
                {v.roi >= 0 ? "+" : ""}{v.roi}%
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
