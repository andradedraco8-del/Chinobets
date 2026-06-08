"""Siembra de datos de demostración: ligas, equipos, partidos, cuotas y apuestas."""
from __future__ import annotations

from datetime import datetime, timedelta

from .core.security import hash_password
from .database import SessionLocal, init_db
from .models import BankrollSettings, Bet, League, Match, Subscription, Team, User
from .models.user import PlanType, UserRole


def seed_if_empty() -> None:
    db = SessionLocal()
    try:
        if db.query(League).first():
            return
        _seed(db)
    finally:
        db.close()


def _seed(db) -> None:
    now = datetime.utcnow()

    # --- Ligas ---
    epl = League(name="Premier League", sport="football", country="Inglaterra", avg_goals=1.45)
    laliga = League(name="LaLiga", sport="football", country="España", avg_goals=1.30)
    nba = League(name="NBA", sport="basketball", country="EE.UU.", avg_goals=1.0)
    db.add_all([epl, laliga, nba])
    db.flush()

    # --- Equipos (fuerza relativa, ELO y xG recientes) ---
    teams = {
        "city": Team(league_id=epl.id, name="Manchester City", elo=1685, attack=1.45, defense=0.80, xg_for=2.10, xg_against=0.95, recent_points=2.4),
        "brighton": Team(league_id=epl.id, name="Brighton", elo=1545, attack=1.05, defense=1.10, xg_for=1.45, xg_against=1.40, recent_points=1.4),
        "arsenal": Team(league_id=epl.id, name="Arsenal", elo=1660, attack=1.35, defense=0.85, xg_for=1.95, xg_against=1.00, recent_points=2.2),
        "wolves": Team(league_id=epl.id, name="Wolves", elo=1500, attack=0.95, defense=1.05, xg_for=1.20, xg_against=1.45, recent_points=1.2),
        "betis": Team(league_id=laliga.id, name="Real Betis", elo=1560, attack=1.10, defense=1.05, xg_for=1.55, xg_against=1.30, recent_points=1.5),
        "atletico": Team(league_id=laliga.id, name="Atletico Madrid", elo=1640, attack=1.30, defense=0.78, xg_for=1.80, xg_against=0.90, recent_points=2.1),
    }
    db.add_all(list(teams.values()))
    db.flush()

    # --- Partidos con cuotas de mercado ---
    db.add_all([
        Match(
            league_id=epl.id, home_team_id=teams["city"].id, away_team_id=teams["brighton"].id,
            kickoff=now + timedelta(hours=4), status="scheduled",
            odds_home=1.62, odds_draw=4.10, odds_away=5.20,
            odds_over_2_5=1.70, odds_under_2_5=2.15, odds_btts_yes=1.80, odds_btts_no=2.00,
        ),
        Match(
            league_id=epl.id, home_team_id=teams["arsenal"].id, away_team_id=teams["wolves"].id,
            kickoff=now + timedelta(hours=6), status="scheduled",
            odds_home=1.45, odds_draw=4.60, odds_away=6.50,
            odds_over_2_5=1.65, odds_under_2_5=2.25, odds_btts_yes=1.95, odds_btts_no=1.85,
        ),
        Match(
            league_id=laliga.id, home_team_id=teams["betis"].id, away_team_id=teams["atletico"].id,
            kickoff=now + timedelta(hours=8), status="scheduled",
            odds_home=3.40, odds_draw=3.20, odds_away=2.20,
            odds_over_2_5=2.05, odds_under_2_5=1.78, odds_btts_yes=1.95, odds_btts_no=1.85,
        ),
    ])

    # --- Usuario demo + suscripción PRO + bankroll + historial de apuestas ---
    user = User(
        email="demo@protipster.ai",
        hashed_password=hash_password("demo1234"),
        full_name="Tipster Demo",
        role=UserRole.PRO.value,
    )
    db.add(user)
    db.flush()
    db.add(Subscription(user_id=user.id, plan=PlanType.PROFESSIONAL.value))
    db.add(BankrollSettings(user_id=user.id, initial_capital=1000.0, current_capital=1086.5))

    # Historial para poblar KPIs (ROI, yield, win rate, curva).
    history = [
        ("Gana Man City", 1.62, 50, "won", 31.0),
        ("Over 2.5 Arsenal-Wolves", 1.65, 40, "won", 26.0),
        ("Gana Atletico", 2.20, 45, "lost", -45.0),
        ("BTTS Sí Betis-Atletico", 1.95, 30, "won", 28.5),
        ("Doble oport. 1X", 1.40, 60, "won", 24.0),
        ("Under 2.5", 1.85, 35, "lost", -35.0),
        ("Hándicap -1 City", 1.90, 40, "won", 36.0),
        ("Gana Arsenal", 1.45, 55, "pending", 0.0),
    ]
    for i, (sel, odds, stake, status, pnl) in enumerate(history):
        db.add(Bet(
            user_id=user.id, selection=sel, odds=odds, stake=stake,
            status=status, pnl=pnl, placed_at=now - timedelta(days=len(history) - i),
        ))

    db.commit()
    print("[seed] datos de demostración insertados.")


if __name__ == "__main__":
    init_db()
    seed_if_empty()
