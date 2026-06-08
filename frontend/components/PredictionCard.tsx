import type { Prediction } from "@/lib/types";
import { confidenceColor } from "@/lib/format";
import ProbBar from "./ProbBar";

export default function PredictionCard({ p }: { p: Prediction }) {
  const eg = p.probabilities.expected_goals;
  const score = p.probabilities.most_likely_score;
  const topValue = p.value_bets.find((v) => v.is_value);

  return (
    <div className="panel p-4">
      <div className="flex items-start justify-between">
        <div>
          <div className="font-mono text-sm font-bold text-term-text">
            {p.home} <span className="text-term-muted">vs</span> {p.away}
          </div>
          <div className="ticker mt-0.5">
            xG {eg.home}-{eg.away} · marcador prob. {score[0]}-{score[1]}
          </div>
        </div>
        <div className="text-right">
          <div className={`font-mono text-sm font-bold ${confidenceColor(p.confidence_text)}`}>
            {p.confidence_text}
          </div>
          <div className="ticker">conf {p.confidence_score.toFixed(0)}/100</div>
        </div>
      </div>

      <div className="mt-3">
        <ProbBar
          home={p.probabilities["1x2"].home}
          draw={p.probabilities["1x2"].draw}
          away={p.probabilities["1x2"].away}
        />
      </div>

      <div className="mt-3 rounded bg-term-bg/60 p-2">
        <div className="ticker">Pick principal</div>
        <div className="font-mono text-sm text-term-green">{p.main_pick.label}</div>
      </div>

      <p className="mt-3 text-xs leading-relaxed text-term-muted">{p.explanation}</p>

      {topValue && (
        <div className="mt-3 flex items-center justify-between rounded border border-term-green/30 bg-term-green/10 px-3 py-2">
          <span className="font-mono text-xs text-term-green">★ {topValue.selection}</span>
          <span className="font-mono text-xs font-bold text-term-green">
            @{topValue.odds.toFixed(2)} · edge +{topValue.edge_pct.toFixed(1)}%
          </span>
        </div>
      )}
    </div>
  );
}
