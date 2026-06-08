"""
Modelo de Poisson para fútbol.

Estima la probabilidad de cada marcador a partir de las tasas esperadas de
goles (lambda) de local y visitante, derivadas del ataque/defensa de cada
equipo y la ventaja de localía. A partir de la matriz de marcadores se
calculan los mercados 1X2, Over/Under y Ambos Marcan (BTTS).

Implementación en Python puro (sólo `math`) para que el núcleo del motor sea
ejecutable sin dependencias externas.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field


def poisson_pmf(k: int, lam: float) -> float:
    """P(X = k) para una variable Poisson de media lam."""
    if lam <= 0:
        return 1.0 if k == 0 else 0.0
    return math.exp(-lam) * lam**k / math.factorial(k)


@dataclass
class MarketProbabilities:
    """Probabilidades normalizadas (0-1) de los principales mercados."""

    home: float
    draw: float
    away: float
    over_2_5: float
    under_2_5: float
    btts_yes: float
    btts_no: float
    most_likely_score: tuple[int, int]
    expected_home_goals: float
    expected_away_goals: float
    extra: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "home": round(self.home, 4),
            "draw": round(self.draw, 4),
            "away": round(self.away, 4),
            "over_2_5": round(self.over_2_5, 4),
            "under_2_5": round(self.under_2_5, 4),
            "btts_yes": round(self.btts_yes, 4),
            "btts_no": round(self.btts_no, 4),
            "most_likely_score": self.most_likely_score,
            "expected_home_goals": round(self.expected_home_goals, 3),
            "expected_away_goals": round(self.expected_away_goals, 3),
            **self.extra,
        }


def expected_goals(
    home_attack: float,
    home_defense: float,
    away_attack: float,
    away_defense: float,
    league_avg_goals: float = 1.35,
    home_advantage: float = 1.10,
) -> tuple[float, float]:
    """
    Calcula las tasas lambda de goles esperados.

    `*_attack` y `*_defense` son fuerzas relativas (1.0 = media de la liga).
    """
    lam_home = league_avg_goals * home_attack * away_defense * home_advantage
    lam_away = league_avg_goals * away_attack * home_defense
    # Acotar para estabilidad numérica.
    return max(0.05, min(lam_home, 6.0)), max(0.05, min(lam_away, 6.0))


def score_matrix(lam_home: float, lam_away: float, max_goals: int = 10) -> list[list[float]]:
    """Matriz P(home=i, away=j) asumiendo independencia."""
    home_probs = [poisson_pmf(i, lam_home) for i in range(max_goals + 1)]
    away_probs = [poisson_pmf(j, lam_away) for j in range(max_goals + 1)]
    return [[hp * ap for ap in away_probs] for hp in home_probs]


def markets_from_matrix(matrix: list[list[float]], lam_home: float, lam_away: float) -> MarketProbabilities:
    home = draw = away = over = btts_yes = 0.0
    best_p, best_score = -1.0, (0, 0)
    total = 0.0
    for i, row in enumerate(matrix):
        for j, p in enumerate(row):
            total += p
            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p
            if i + j > 2:  # over 2.5
                over += p
            if i > 0 and j > 0:
                btts_yes += p
            if p > best_p:
                best_p, best_score = p, (i, j)

    # Normaliza por si se truncó la cola de la matriz.
    if total > 0:
        home, draw, away, over, btts_yes = (
            home / total,
            draw / total,
            away / total,
            over / total,
            btts_yes / total,
        )
    return MarketProbabilities(
        home=home,
        draw=draw,
        away=away,
        over_2_5=over,
        under_2_5=1 - over,
        btts_yes=btts_yes,
        btts_no=1 - btts_yes,
        most_likely_score=best_score,
        expected_home_goals=lam_home,
        expected_away_goals=lam_away,
    )


def predict_poisson(
    home_attack: float,
    home_defense: float,
    away_attack: float,
    away_defense: float,
    league_avg_goals: float = 1.35,
    home_advantage: float = 1.10,
    max_goals: int = 10,
) -> MarketProbabilities:
    """Pipeline completo del modelo de Poisson."""
    lam_home, lam_away = expected_goals(
        home_attack, home_defense, away_attack, away_defense, league_avg_goals, home_advantage
    )
    matrix = score_matrix(lam_home, lam_away, max_goals)
    return markets_from_matrix(matrix, lam_home, lam_away)
