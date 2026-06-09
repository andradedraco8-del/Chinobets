"""Construcción del histórico de apuestas para el backtesting.

Genera un conjunto realista de apuestas resueltas simulando temporadas con el
propio motor (Dixon-Coles como "verdad" subyacente) y cuotas de mercado con
margen. Es determinista (semilla fija) para que el backtest sea reproducible.
También puede derivar el histórico de las apuestas reales del usuario.
"""
from __future__ import annotations

import random

from ..ml.backtest import HistoricalBet
from ..ml.dixon_coles import predict_dixon_coles
from ..ml.engine import TeamForm

MARKETS = ["1X2", "O/U 2.5", "BTTS"]
SPORTS = ["football", "basketball", "tennis"]


def _random_team() -> TeamForm:
    return TeamForm(
        name="t",
        attack=max(0.6, random.gauss(1.0, 0.25)),
        defense=max(0.6, random.gauss(1.0, 0.25)),
        elo=random.gauss(1500, 70),
        xg_for=max(0.4, random.gauss(1.4, 0.4)),
        xg_against=max(0.4, random.gauss(1.4, 0.4)),
    )


def generate_history(n: int = 600, seed: int = 7, bookmaker_margin: float = 0.06) -> list[HistoricalBet]:
    """
    Genera `n` apuestas resueltas. La casa añade un margen a las cuotas; el
    modelo encuentra valor cuando su probabilidad supera la implícita.
    """
    random.seed(seed)
    bets: list[HistoricalBet] = []
    for _ in range(n):
        home, away = _random_team(), _random_team()
        dc = predict_dixon_coles(
            home.attack * (home.xg_for / 1.4),
            home.defense * (home.xg_against / 1.4),
            away.attack * (away.xg_for / 1.4),
            away.defense * (away.xg_against / 1.4),
        )
        market = random.choice(MARKETS)
        sport = random.choices(SPORTS, weights=[0.6, 0.25, 0.15])[0]

        if market == "1X2":
            sel, true_p = random.choice([("Local", dc.home), ("Empate", dc.draw), ("Visitante", dc.away)])
        elif market == "O/U 2.5":
            sel, true_p = random.choice([("Over 2.5", dc.over_2_5), ("Under 2.5", dc.under_2_5)])
        else:
            sel, true_p = random.choice([("BTTS Sí", dc.btts_yes), ("BTTS No", dc.btts_no)])

        true_p = min(max(true_p, 0.02), 0.98)
        # Cuota de mercado: inversa de la prob real, peor por el margen, con ruido.
        fair_odds = 1.0 / true_p
        market_odds = fair_odds * (1 - bookmaker_margin) * random.uniform(0.92, 1.12)
        market_odds = max(1.05, round(market_odds, 2))

        # El "modelo" estima la prob con un pequeño error (no es perfecto).
        model_prob = min(0.98, max(0.02, true_p * random.uniform(0.92, 1.08)))
        # Resultado real muestreado de la probabilidad verdadera.
        won = random.random() < true_p

        bets.append(HistoricalBet(
            selection=sel, market=market, sport=sport,
            odds=market_odds, model_prob=model_prob, won=won,
        ))
    return bets
