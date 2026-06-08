"""
Modelo Dixon-Coles (1997).

Mejora el Poisson independiente con un factor de corrección `tau` que ajusta la
dependencia entre marcadores bajos (0-0, 1-0, 0-1, 1-1), donde el Poisson puro
tiende a equivocarse. Es uno de los modelos de referencia para fútbol.

Núcleo en Python puro reutilizando `poisson.py`.
"""
from __future__ import annotations

from .poisson import MarketProbabilities, expected_goals, poisson_pmf


def tau(i: int, j: int, lam_home: float, lam_away: float, rho: float) -> float:
    """Factor de corrección de Dixon-Coles para los marcadores bajos."""
    if i == 0 and j == 0:
        return 1.0 - lam_home * lam_away * rho
    if i == 0 and j == 1:
        return 1.0 + lam_home * rho
    if i == 1 and j == 0:
        return 1.0 + lam_away * rho
    if i == 1 and j == 1:
        return 1.0 - rho
    return 1.0


def predict_dixon_coles(
    home_attack: float,
    home_defense: float,
    away_attack: float,
    away_defense: float,
    league_avg_goals: float = 1.35,
    home_advantage: float = 1.10,
    rho: float = -0.13,
    max_goals: int = 10,
) -> MarketProbabilities:
    """
    Pipeline Dixon-Coles. `rho` controla la corrección de empates/marcadores
    bajos (valores típicos entre -0.18 y -0.05).
    """
    lam_home, lam_away = expected_goals(
        home_attack, home_defense, away_attack, away_defense, league_avg_goals, home_advantage
    )

    home = draw = away = over = btts_yes = total = 0.0
    best_p, best_score = -1.0, (0, 0)

    for i in range(max_goals + 1):
        ph = poisson_pmf(i, lam_home)
        for j in range(max_goals + 1):
            pa = poisson_pmf(j, lam_away)
            p = ph * pa * tau(i, j, lam_home, lam_away, rho)
            p = max(p, 0.0)
            total += p
            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p
            if i + j > 2:
                over += p
            if i > 0 and j > 0:
                btts_yes += p
            if p > best_p:
                best_p, best_score = p, (i, j)

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
        extra={"model": "dixon_coles", "rho": rho},
    )
