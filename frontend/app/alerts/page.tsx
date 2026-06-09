import Header from "@/components/Header";
import { api } from "@/lib/api";
import type { Alert } from "@/lib/types";

export const dynamic = "force-dynamic";

const SEVERITY: Record<Alert["severity"], { dot: string; border: string; label: string }> = {
  success: { dot: "bg-term-green", border: "border-term-green/40", label: "VALOR" },
  warning: { dot: "bg-term-amber", border: "border-term-amber/40", label: "ARBITRAJE" },
  info: { dot: "bg-term-muted", border: "border-term-border", label: "INFO" },
};

const ICON: Record<Alert["type"], string> = {
  value_bet: "★",
  high_confidence: "◎",
  odds_movement: "↕",
  arbitrage: "⇄",
};

export default async function AlertsPage() {
  const alerts = await api.alerts();

  return (
    <main>
      <Header />
      <div className="mx-auto max-w-4xl space-y-6 px-6 py-6">
        <a href="/" className="ticker hover:text-term-green">← volver al dashboard</a>
        <div className="flex items-center justify-between">
          <h1 className="font-mono text-xl font-bold text-term-text">Centro de alertas</h1>
          <span className="pill bg-term-green/15 text-term-green">● {alerts.length} activas</span>
        </div>

        <div className="space-y-3">
          {alerts.length === 0 && (
            <div className="panel p-6 text-center text-sm text-term-muted">
              No hay alertas activas en este momento.
            </div>
          )}
          {alerts.map((a, i) => {
            const s = SEVERITY[a.severity];
            return (
              <a
                key={i}
                href={`/match/${a.match_id}`}
                className={`panel flex items-start gap-3 border-l-2 p-4 transition-colors hover:bg-term-green/5 ${s.border}`}
              >
                <span className="mt-1 font-mono text-lg text-term-green">{ICON[a.type]}</span>
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-sm font-bold text-term-text">{a.title}</span>
                    <span className={`h-2 w-2 rounded-full ${s.dot}`} />
                    <span className="ticker">{s.label}</span>
                  </div>
                  <div className="mt-0.5 font-mono text-sm text-term-green">{a.message}</div>
                  <div className="ticker mt-1">{a.match}</div>
                </div>
                <span className="ticker">{new Date(a.created_at).toLocaleTimeString("es-ES")}</span>
              </a>
            );
          })}
        </div>
      </div>
    </main>
  );
}
