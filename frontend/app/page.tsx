import Header from "@/components/Header";
import StatCard from "@/components/StatCard";
import GrowthChart from "@/components/GrowthChart";
import ValueBetsTable from "@/components/ValueBetsTable";
import PredictionCard from "@/components/PredictionCard";
import { api } from "@/lib/api";
import { money, signed } from "@/lib/format";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [stats, predictions, valueBets] = await Promise.all([
    api.dashboardStats(),
    api.predictions(),
    api.valueBets(),
  ]);

  return (
    <main>
      <Header />

      <div className="mx-auto max-w-7xl space-y-6 px-6 py-6">
        {/* KPIs */}
        <section className="grid grid-cols-2 gap-3 md:grid-cols-3 lg:grid-cols-6">
          <StatCard
            label="ROI"
            value={`${stats.roi.toFixed(2)}%`}
            delta={signed(stats.roi)}
            positive={stats.roi >= 0}
            hint="retorno sobre capital"
          />
          <StatCard
            label="Yield"
            value={`${stats.yield_pct.toFixed(2)}%`}
            delta={signed(stats.yield_pct)}
            positive={stats.yield_pct >= 0}
            hint="beneficio / apostado"
          />
          <StatCard label="Win Rate" value={`${stats.win_rate.toFixed(1)}%`} hint={`${stats.won}G / ${stats.lost}P`} />
          <StatCard
            label="Beneficio"
            value={money(stats.profit)}
            delta={signed(stats.profit)}
            positive={stats.profit >= 0}
            hint="acumulado"
          />
          <StatCard label="Bankroll" value={money(stats.bankroll)} hint={`inicial ${money(stats.initial_capital)}`} />
          <StatCard
            label="Riesgo abierto"
            value={`${stats.open_exposure_pct.toFixed(1)}%`}
            hint={`${stats.pending} picks activos`}
          />
        </section>

        {/* Curva de crecimiento + resumen */}
        <section className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="panel p-4 lg:col-span-2">
            <div className="mb-2 flex items-center justify-between">
              <h2 className="font-mono text-sm font-bold uppercase tracking-wider text-term-text">
                Curva de crecimiento del bankroll
              </h2>
              <span className="ticker">{stats.total_bets} apuestas</span>
            </div>
            <GrowthChart data={stats.growth_curve} />
          </div>

          <div className="panel p-4">
            <h2 className="mb-3 font-mono text-sm font-bold uppercase tracking-wider text-term-text">
              Resumen de actividad
            </h2>
            <ul className="space-y-2 font-mono text-sm">
              <Row label="Apuestas totales" value={`${stats.total_bets}`} />
              <Row label="Ganadas" value={`${stats.won}`} cls="text-term-green" />
              <Row label="Perdidas" value={`${stats.lost}`} cls="text-term-red" />
              <Row label="Pendientes" value={`${stats.pending}`} cls="text-term-amber" />
              <Row label="Value bets activas" value={`${valueBets.length}`} cls="text-term-green" />
            </ul>
          </div>
        </section>

        {/* Value bets */}
        <section id="value-bets">
          <ValueBetsTable bets={valueBets} />
        </section>

        {/* Pronósticos del día */}
        <section id="predictions">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="font-mono text-sm font-bold uppercase tracking-wider text-term-text">
              Pronósticos del día
            </h2>
            <span className="ticker">{predictions.length} partidos</span>
          </div>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
            {predictions.map((p) => (
              <a key={p.match_id} href={`/match/${p.match_id}`} className="block transition-transform hover:-translate-y-0.5">
                <PredictionCard p={p} />
              </a>
            ))}
          </div>
        </section>

        <footer className="border-t border-term-border pt-4 text-center text-[11px] text-term-muted">
          ProTipster AI · Herramienta analítica. Juega con responsabilidad. +18.
        </footer>
      </div>
    </main>
  );
}

function Row({ label, value, cls = "text-term-text" }: { label: string; value: string; cls?: string }) {
  return (
    <li className="flex items-center justify-between border-b border-term-border/40 pb-1.5">
      <span className="text-term-muted">{label}</span>
      <span className={`font-bold ${cls}`}>{value}</span>
    </li>
  );
}
