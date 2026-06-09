"""Ingeniería de características para los modelos de ML.

Convierte el estado de dos equipos (forma, xG, ELO, fatiga, etc.) en un vector
numérico de features que consumen Random Forest / XGBoost / LightGBM / redes.
Mantener el orden de `FEATURE_NAMES` estable: define el esquema del modelo.
"""
from __future__ import annotations

from .engine import TeamForm

FEATURE_NAMES = [
    "elo_diff",          # ventaja ELO local - visitante
    "home_attack",
    "home_defense",
    "away_attack",
    "away_defense",
    "home_xg_for",
    "home_xg_against",
    "away_xg_for",
    "away_xg_against",
    "xg_supremacy",      # (xg_for_local - xg_against_visitante) - simétrico
    "form_diff",         # puntos recientes local - visitante
    "home_advantage",    # constante de localía
]


def build_features(
    home: TeamForm,
    away: TeamForm,
    home_advantage: float = 1.0,
) -> list[float]:
    """Devuelve el vector de features en el orden de FEATURE_NAMES."""
    xg_supremacy = (home.xg_for - away.xg_against) - (away.xg_for - home.xg_against)
    return [
        (home.elo - away.elo) / 100.0,
        home.attack,
        home.defense,
        away.attack,
        away.defense,
        home.xg_for,
        home.xg_against,
        away.xg_for,
        away.xg_against,
        xg_supremacy,
        home.recent_points - away.recent_points,
        home_advantage,
    ]


def feature_dict(home: TeamForm, away: TeamForm) -> dict[str, float]:
    """Versión etiquetada (útil para depurar o explicabilidad)."""
    return dict(zip(FEATURE_NAMES, build_features(home, away)))
