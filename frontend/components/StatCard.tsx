interface StatCardProps {
  label: string;
  value: string;
  delta?: string;
  positive?: boolean;
  hint?: string;
}

export default function StatCard({ label, value, delta, positive, hint }: StatCardProps) {
  return (
    <div className="panel p-4 hover:shadow-glow transition-shadow">
      <div className="ticker">{label}</div>
      <div className="mt-1 flex items-baseline gap-2">
        <span className="font-mono text-2xl font-bold text-term-text">{value}</span>
        {delta && (
          <span
            className={`font-mono text-xs font-semibold ${
              positive ? "text-term-green" : "text-term-red"
            }`}
          >
            {delta}
          </span>
        )}
      </div>
      {hint && <div className="mt-1 text-[11px] text-term-muted">{hint}</div>}
    </div>
  );
}
