"""
Sistema de ranking ELO adaptado a deportes.

ELO modela la fuerza relativa de cada equipo. La diferencia de rating (más la
ventaja de localía) se traduce en una probabilidad de victoria mediante la
curva logística. Sirve como modelo independiente y como feature para el
ensemble. Funciona para fútbol, baloncesto, tenis, etc.
"""
from __future__ import annotations


def expected_score(rating_a: float, rating_b: float, home_advantage: float = 65.0) -> float:
    """Probabilidad esperada (incluye empates parciales) de que A venza a B."""
    diff = (rating_a + home_advantage) - rating_b
    return 1.0 / (1.0 + 10 ** (-diff / 400.0))


def update_ratings(
    rating_home: float,
    rating_away: float,
    result: float,
    k: float = 20.0,
    home_advantage: float = 65.0,
) -> tuple[float, float]:
    """
    Actualiza ratings tras un partido.
    `result`: 1.0 gana local, 0.5 empate, 0.0 gana visitante.
    """
    exp_home = expected_score(rating_home, rating_away, home_advantage)
    new_home = rating_home + k * (result - exp_home)
    new_away = rating_away + k * ((1 - result) - (1 - exp_home))
    return new_home, new_away


def elo_match_probabilities(
    rating_home: float,
    rating_away: float,
    home_advantage: float = 65.0,
    draw_factor: float = 0.28,
) -> dict[str, float]:
    """
    Convierte ratings ELO en probabilidades 1X2.

    `draw_factor` reparte parte de la probabilidad hacia el empate; es mayor
    cuanto más parejos están los equipos.
    """
    p_home_raw = expected_score(rating_home, rating_away, home_advantage)
    p_away_raw = 1.0 - p_home_raw

    # La probabilidad de empate crece cuando el partido está igualado.
    balance = 1.0 - abs(p_home_raw - p_away_raw)  # 0..1
    p_draw = draw_factor * balance

    scale = 1.0 - p_draw
    p_home = p_home_raw * scale
    p_away = p_away_raw * scale
    return {"home": p_home, "draw": p_draw, "away": p_away}


def rating_to_strength(rating: float, league_avg: float = 1500.0) -> float:
    """
    Traduce un rating ELO a un factor de fuerza relativo (~1.0 = media liga)
    utilizable como ataque/defensa en los modelos de Poisson.
    """
    return 10 ** ((rating - league_avg) / 400.0)
