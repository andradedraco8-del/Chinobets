"""KPIs del dashboard profesional: ROI, Yield, Win Rate, curva de crecimiento."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import BankrollSettings, Bet, User
from ...schemas import DashboardStats

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _compute_stats(bets: list[Bet], initial_capital: float) -> DashboardStats:
    settled = [b for b in bets if b.status in ("won", "lost")]
    won = sum(1 for b in settled if b.status == "won")
    lost = sum(1 for b in settled if b.status == "lost")
    pending = sum(1 for b in bets if b.status == "pending")

    staked = sum(b.stake for b in settled) or 0.0
    profit = sum(b.pnl for b in bets)
    open_exposure = sum(b.stake for b in bets if b.status == "pending")

    roi = (profit / initial_capital * 100) if initial_capital else 0.0
    yield_pct = (profit / staked * 100) if staked else 0.0
    win_rate = (won / len(settled) * 100) if settled else 0.0

    # Curva de crecimiento del bankroll (orden cronológico).
    curve = [{"x": 0, "bankroll": round(initial_capital, 2)}]
    running = initial_capital
    for i, b in enumerate(sorted(bets, key=lambda x: x.placed_at), start=1):
        running += b.pnl
        curve.append({"x": i, "bankroll": round(running, 2)})

    return DashboardStats(
        bankroll=round(initial_capital + profit, 2),
        initial_capital=round(initial_capital, 2),
        profit=round(profit, 2),
        roi=round(roi, 2),
        yield_pct=round(yield_pct, 2),
        win_rate=round(win_rate, 2),
        total_bets=len(bets),
        won=won,
        lost=lost,
        pending=pending,
        open_exposure_pct=round((open_exposure / initial_capital * 100) if initial_capital else 0.0, 2),
        growth_curve=curve,
    )


@router.get("/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)):
    """
    Estadísticas agregadas. En el MVP usa el primer usuario sembrado; en
    producción se filtra por el usuario autenticado (Depends(get_current_user)).
    """
    user = db.query(User).first()
    initial = 1000.0
    bets: list[Bet] = []
    if user:
        bk = db.query(BankrollSettings).filter(BankrollSettings.user_id == user.id).first()
        initial = bk.initial_capital if bk else 1000.0
        bets = db.query(Bet).filter(Bet.user_id == user.id).all()
    return _compute_stats(bets, initial)
