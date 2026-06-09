"""Motor de backtesting de estrategias de apuestas (Python puro).

Simula la aplicación de una estrategia de staking sobre un histórico de
apuestas resueltas y calcula las métricas clave que usa un tipster profesional:

  - ROI (retorno sobre el capital inicial)
  - Yield (beneficio / total apostado)
  - Win rate
  - Máximo drawdown (caída pico-valle del bankroll)
  - Rentabilidad por mercado y por deporte
  - Equity curve (evolución del bankroll)

No requiere dependencias externas, por lo que es totalmente ejecutable.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .kelly import StakingMethod, recommend_stake


@dataclass
class HistoricalBet:
    """Una apuesta resuelta del histórico."""

    selection: str
    market: str
    sport: str
    odds: float
    model_prob: float
    won: bool


@dataclass
class BacktestResult:
    initial_bankroll: float
    final_bankroll: float
    profit: float
    roi: float
    yield_pct: float
    win_rate: float
    total_bets: int
    wins: int
    losses: int
    total_staked: float
    max_drawdown: float          # en valor monetario
    max_drawdown_pct: float      # en % sobre el pico
    longest_losing_streak: int
    by_market: dict
    by_sport: dict
    equity_curve: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "initial_bankroll": round(self.initial_bankroll, 2),
            "final_bankroll": round(self.final_bankroll, 2),
            "profit": round(self.profit, 2),
            "roi": round(self.roi, 2),
            "yield_pct": round(self.yield_pct, 2),
            "win_rate": round(self.win_rate, 2),
            "total_bets": self.total_bets,
            "wins": self.wins,
            "losses": self.losses,
            "total_staked": round(self.total_staked, 2),
            "max_drawdown": round(self.max_drawdown, 2),
            "max_drawdown_pct": round(self.max_drawdown_pct, 2),
            "longest_losing_streak": self.longest_losing_streak,
            "by_market": self.by_market,
            "by_sport": self.by_sport,
            "equity_curve": self.equity_curve,
        }


def run_backtest(
    bets: list[HistoricalBet],
    initial_bankroll: float = 1000.0,
    method: StakingMethod = StakingMethod.KELLY_FRACTION,
    fixed_units: float = 1.0,
    edge_threshold: float = 0.0,
    compounding: bool = True,
) -> BacktestResult:
    """
    Ejecuta el backtest.

    - `compounding`: si True, el stake se recalcula sobre el bankroll vivo
      (interés compuesto); si False, sobre el bankroll inicial (flat).
    - `edge_threshold`: omite apuestas cuyo edge sea inferior al umbral.
    """
    bankroll = initial_bankroll
    peak = initial_bankroll
    max_dd = 0.0
    max_dd_pct = 0.0
    total_staked = 0.0
    wins = losses = 0
    losing_streak = longest_losing_streak = 0

    by_market: dict[str, dict] = {}
    by_sport: dict[str, dict] = {}
    equity_curve = [{"x": 0, "bankroll": round(bankroll, 2)}]

    for i, bet in enumerate(bets, start=1):
        edge = bet.model_prob * bet.odds - 1.0
        if edge < edge_threshold:
            continue

        base = bankroll if compounding else initial_bankroll
        rec = recommend_stake(bet.model_prob, bet.odds, base, method=method, fixed_units=fixed_units)
        stake = min(rec.stake, bankroll)  # no apostar más de lo disponible
        if stake <= 0:
            continue

        total_staked += stake
        pnl = stake * (bet.odds - 1.0) if bet.won else -stake
        bankroll += pnl

        if bet.won:
            wins += 1
            losing_streak = 0
        else:
            losses += 1
            losing_streak += 1
            longest_losing_streak = max(longest_losing_streak, losing_streak)

        # Drawdown.
        peak = max(peak, bankroll)
        drawdown = peak - bankroll
        if drawdown > max_dd:
            max_dd = drawdown
            max_dd_pct = (drawdown / peak * 100) if peak else 0.0

        _accumulate(by_market, bet.market, stake, pnl, bet.won)
        _accumulate(by_sport, bet.sport, stake, pnl, bet.won)
        equity_curve.append({"x": i, "bankroll": round(bankroll, 2)})

    settled = wins + losses
    profit = bankroll - initial_bankroll
    return BacktestResult(
        initial_bankroll=initial_bankroll,
        final_bankroll=bankroll,
        profit=profit,
        roi=(profit / initial_bankroll * 100) if initial_bankroll else 0.0,
        yield_pct=(profit / total_staked * 100) if total_staked else 0.0,
        win_rate=(wins / settled * 100) if settled else 0.0,
        total_bets=settled,
        wins=wins,
        losses=losses,
        total_staked=total_staked,
        max_drawdown=max_dd,
        max_drawdown_pct=max_dd_pct,
        longest_losing_streak=longest_losing_streak,
        by_market={k: _finalize(v) for k, v in by_market.items()},
        by_sport={k: _finalize(v) for k, v in by_sport.items()},
        equity_curve=equity_curve,
    )


def _accumulate(bucket: dict, key: str, stake: float, pnl: float, won: bool) -> None:
    b = bucket.setdefault(key, {"bets": 0, "wins": 0, "staked": 0.0, "profit": 0.0})
    b["bets"] += 1
    b["wins"] += 1 if won else 0
    b["staked"] += stake
    b["profit"] += pnl


def _finalize(b: dict) -> dict:
    return {
        "bets": b["bets"],
        "wins": b["wins"],
        "win_rate": round((b["wins"] / b["bets"] * 100) if b["bets"] else 0.0, 1),
        "staked": round(b["staked"], 2),
        "profit": round(b["profit"], 2),
        "roi": round((b["profit"] / b["staked"] * 100) if b["staked"] else 0.0, 2),
    }
