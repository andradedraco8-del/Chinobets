import Header from "@/components/Header";
import ProbBar from "@/components/ProbBar";
import ValueBetsTable from "@/components/ValueBetsTable";
import { api } from "@/lib/api";
import { confidenceColor } from "@/lib/format";

export const dynamic = "force-dynamic";

export default async function MatchDetailPage({ params }: { params: { id: string } }) {
  const id = Number(params.id);
  const p = await api.prediction(id);
  const ou = p.probabilities.over_under_2_5;
  const btts = p.probabilities.btts;
  const eg = p.probabilities.expected_goals;
  const score = p.probabilities.most_likely_score;
  const models = (p.probabilities as { models?: string[] }).models ?? [
    "poisson",
    "dixon_coles",
    "elo",
  ];

  return (
    <main>
      <Header />
      <div className="mx-auto max-w-5xl space-y-6 px-6 py-6">
        <a href="/" className="ticker hover:text-term-green">
          ← volver al dashboard
        </a>

        {/* Cabecera del partido */}
        <section className="panel p-5">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="font-mono text-xl font-bold text-term-text">
                {p.home} <span className="text-term-muted">vs</span> {p.away}
              </h1>
              <div className="ticker mt-1">
                xG {eg.home}-{eg.away} · marcador más probable {score[0]}-{score[1]}
              </div>
            </div>
            <div className="text-right">
              <div className={`font-mono text-lg font-bold ${confidenceColor(p.confidence_text)}`}>
                {p.confidence_text}
              </div>
              <div className="ticker">confianza {p.confidence_score.toFixed(0)}/100</div>
            </div>
          </div>

          <div className="mt-4">
            <ProbBar
              home={p.probabilities["1x2"].home}
              draw={p.probabilities["1x2"].draw}
              away={p.probabilities["1x2"].away}
            />
          </div>

          <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-3">
            <MarketBox title="Over/Under 2.5">
              <Line label="Over 2.5" value={ou.over} />
              <Line label="Under 2.5" value={ou.under} />
            </MarketBox>
            <MarketBox title="Ambos Marcan">
              <Line label="Sí" value={btts.yes} />
              <Line label="No" value={btts.no} />
            </MarketBox>
            <MarketBox title="Pick principal">
              <div className="font-mono text-sm text-term-green">{p.main_pick.label}</div>
              <div className="ticker mt-1">
                prob {(p.main_pick.model_prob * 100).toFixed(0)}%
              </div>
            </MarketBox>
          </div>
        </section>

        {/* Explicación IA */}
        <section className="panel p-5">
          <h2 className="mb-2 font-mono text-sm font-bold uppercase tracking-wider text-term-text">
            🧠 Explicación del modelo
          </h2>
          <p className="text-sm leading-relaxed text-term-muted">{p.explanation}</p>
          <div className="mt-3 flex flex-wrap gap-2">
            {models.map((m) => (
              <span key={m} className="pill bg-term-border text-term-muted">
                {m}
              </span>
            ))}
          </div>
        </section>

        {/* Value bets del partido */}
        {p.value_bets.length > 0 && <ValueBetsTable bets={p.value_bets} />}
      </div>
    </main>
  );
}

function MarketBox({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded border border-term-border bg-term-bg/60 p-3">
      <div className="ticker mb-2">{title}</div>
      {children}
    </div>
  );
}

function Line({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center justify-between font-mono text-sm">
      <span className="text-term-muted">{label}</span>
      <span className="text-term-text">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}
