"""Entrenamiento del modelo ML 1X2.

Permite entrenar:
  - desde el histórico de la BD (partidos finalizados con marcador), o
  - desde datos sintéticos generados con el propio modelo de Poisson como
    "verdad" subyacente (útil para arrancar sin histórico real).

Ejecutable:  python -m app.ml.training
"""
from __future__ import annotations

import random

from .dixon_coles import predict_dixon_coles
from .engine import TeamForm
from .features import build_features
from .ml_models import MODEL_PATH, MLPredictor


def _random_team() -> TeamForm:
    elo = random.gauss(1500, 70)
    attack = max(0.6, random.gauss(1.0, 0.25))
    defense = max(0.6, random.gauss(1.0, 0.25))
    return TeamForm(
        name="synthetic",
        attack=attack,
        defense=defense,
        elo=elo,
        xg_for=max(0.4, random.gauss(1.4, 0.4)),
        xg_against=max(0.4, random.gauss(1.4, 0.4)),
        recent_points=max(0.0, min(3.0, random.gauss(1.5, 0.6))),
    )


def _sample_outcome(home: TeamForm, away: TeamForm) -> int:
    """Genera un resultado (0=home,1=draw,2=away) según Dixon-Coles."""
    dc = predict_dixon_coles(
        home.attack * (home.xg_for / 1.4),
        home.defense * (home.xg_against / 1.4),
        away.attack * (away.xg_for / 1.4),
        away.defense * (away.xg_against / 1.4),
    )
    r = random.random()
    if r < dc.home:
        return 0
    if r < dc.home + dc.draw:
        return 1
    return 2


def generate_synthetic_dataset(n: int = 4000, seed: int = 42) -> tuple[list[list[float]], list[int]]:
    random.seed(seed)
    X: list[list[float]] = []
    y: list[int] = []
    for _ in range(n):
        home, away = _random_team(), _random_team()
        X.append(build_features(home, away))
        y.append(_sample_outcome(home, away))
    return X, y


def train_synthetic(n: int = 4000, save: bool = True) -> dict:
    X, y = generate_synthetic_dataset(n)
    predictor = MLPredictor.create()
    result = predictor.train(X, y)
    if result.get("trained") and save:
        result["saved"] = predictor.save(MODEL_PATH)
        result["path"] = MODEL_PATH
    return result


def train_from_history(matches: list, save: bool = True) -> dict:
    """Entrena con partidos finalizados de la BD (objetos Match con marcador)."""
    X: list[list[float]] = []
    y: list[int] = []
    for m in matches:
        if m.home_score is None or m.away_score is None:
            continue
        home = TeamForm(m.home_team.name, m.home_team.attack, m.home_team.defense,
                        m.home_team.elo, m.home_team.xg_for, m.home_team.xg_against,
                        m.home_team.recent_points)
        away = TeamForm(m.away_team.name, m.away_team.attack, m.away_team.defense,
                        m.away_team.elo, m.away_team.xg_for, m.away_team.xg_against,
                        m.away_team.recent_points)
        X.append(build_features(home, away))
        if m.home_score > m.away_score:
            y.append(0)
        elif m.home_score == m.away_score:
            y.append(1)
        else:
            y.append(2)

    if len(X) < 50:
        # Demasiado poco histórico: completa con sintéticos.
        sx, sy = generate_synthetic_dataset(2000)
        X += sx
        y += sy

    predictor = MLPredictor.create()
    result = predictor.train(X, y)
    if result.get("trained") and save:
        result["saved"] = predictor.save(MODEL_PATH)
    return result


if __name__ == "__main__":
    print(train_synthetic())
