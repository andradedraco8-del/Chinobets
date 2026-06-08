import type { ValueBet } from "@/lib/types";
import { categoryStyle, riskColor } from "@/lib/format";

export default function ValueBetsTable({ bets }: { bets: ValueBet[] }) {
  return (
    <div className="panel overflow-hidden">
      <div className="flex items-center justify-between border-b border-term-border px-4 py-3">
        <h2 className="font-mono text-sm font-bold uppercase tracking-wider text-term-text">
          ★ Value Bets · Ranking
        </h2>
        <span className="ticker">{bets.length} oportunidades</span>
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="ticker border-b border-term-border text-left">
              <th className="px-4 py-2 font-medium">Selección</th>
              <th className="px-4 py-2 font-medium">Mercado</th>
              <th className="px-4 py-2 text-right font-medium">Cuota</th>
              <th className="px-4 py-2 text-right font-medium">Impl.</th>
              <th className="px-4 py-2 text-right font-medium">IA</th>
              <th className="px-4 py-2 text-right font-medium">Edge</th>
              <th className="px-4 py-2 text-right font-medium">EV</th>
              <th className="px-4 py-2 text-center font-medium">Riesgo</th>
              <th className="px-4 py-2 font-medium">Categoría</th>
              <th className="px-4 py-2 text-right font-medium">Score</th>
            </tr>
          </thead>
          <tbody className="font-mono">
            {bets.map((b, i) => (
              <tr key={i} className="border-b border-term-border/50 hover:bg-term-green/5">
                <td className="px-4 py-2">
                  <div className="text-term-text">{b.selection}</div>
                  {b.match && <div className="text-[11px] text-term-muted">{b.match}</div>}
                </td>
                <td className="px-4 py-2 text-term-muted">{b.market}</td>
                <td className="px-4 py-2 text-right text-term-text">{b.odds.toFixed(2)}</td>
                <td className="px-4 py-2 text-right text-term-muted">{(b.implied_prob * 100).toFixed(0)}%</td>
                <td className="px-4 py-2 text-right text-term-text">{(b.model_prob * 100).toFixed(0)}%</td>
                <td className="px-4 py-2 text-right font-bold text-term-green">+{b.edge_pct.toFixed(1)}%</td>
                <td className="px-4 py-2 text-right text-term-green">+{b.ev.toFixed(3)}</td>
                <td className={`px-4 py-2 text-center ${riskColor(b.risk_level)}`}>{b.risk_level}</td>
                <td className="px-4 py-2">
                  <span className={`pill ${categoryStyle(b.category)}`}>{b.category}</span>
                </td>
                <td className="px-4 py-2 text-right font-bold text-term-text">{b.quality_score.toFixed(0)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
