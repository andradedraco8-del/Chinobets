interface Props {
  home: number;
  draw: number;
  away: number;
  homeLabel?: string;
  awayLabel?: string;
}

/** Barra apilada de probabilidad 1X2 estilo terminal. */
export default function ProbBar({ home, draw, away, homeLabel = "L", awayLabel = "V" }: Props) {
  const f = (n: number) => `${(n * 100).toFixed(0)}%`;
  return (
    <div>
      <div className="flex h-3 w-full overflow-hidden rounded">
        <div className="bg-term-green" style={{ width: `${home * 100}%` }} title={`Local ${f(home)}`} />
        <div className="bg-term-muted/60" style={{ width: `${draw * 100}%` }} title={`Empate ${f(draw)}`} />
        <div className="bg-term-red/80" style={{ width: `${away * 100}%` }} title={`Visitante ${f(away)}`} />
      </div>
      <div className="mt-1 flex justify-between font-mono text-[11px] text-term-muted">
        <span className="text-term-green">{homeLabel} {f(home)}</span>
        <span>X {f(draw)}</span>
        <span className="text-term-red">{awayLabel} {f(away)}</span>
      </div>
    </div>
  );
}
