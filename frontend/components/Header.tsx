import AuthStatus from "./AuthStatus";

export default function Header() {
  return (
    <header className="sticky top-0 z-10 border-b border-term-border bg-term-bg/95 backdrop-blur">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded bg-term-green/15 font-mono text-term-green shadow-glow">
            ▲
          </div>
          <div>
            <div className="font-mono text-sm font-bold tracking-wider text-term-text">
              ProTipster<span className="text-term-green"> AI</span>
            </div>
            <div className="ticker">terminal de análisis deportivo</div>
          </div>
        </div>

        <nav className="hidden gap-6 font-mono text-xs uppercase tracking-wider text-term-muted md:flex">
          <a className="hover:text-term-green" href="/">Dashboard</a>
          <a className="hover:text-term-text" href="/#value-bets">Value Bets</a>
          <a className="hover:text-term-text" href="/#predictions">Pronósticos</a>
          <a className="hover:text-term-text" href="/bankroll">Bankroll</a>
          <a className="hover:text-term-text" href="/backtesting">Backtesting</a>
          <a className="hover:text-term-text" href="/alerts">Alertas</a>
        </nav>

        <div className="flex items-center gap-2">
          <span className="pill bg-term-green/15 text-term-green">● LIVE</span>
          <AuthStatus />
        </div>
      </div>
    </header>
  );
}
