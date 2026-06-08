"""Puente entre la capa de datos (ORM) y el motor de predicción (ml)."""
from __future__ import annotations

from ..ml.engine import TeamForm, predict_match
from ..models import Match


def _odds_dict(match: Match) -> dict:
    raw = {
        "home": match.odds_home,
        "draw": match.odds_draw,
        "away": match.odds_away,
        "over_2_5": match.odds_over_2_5,
        "under_2_5": match.odds_under_2_5,
        "btts_yes": match.odds_btts_yes,
        "btts_no": match.odds_btts_no,
    }
    return {k: v for k, v in raw.items() if v}


def match_odds(match: Match) -> dict:
    """Cuotas en formato API-friendly."""
    return _odds_dict(match)


def predict_for_match(match: Match, edge_threshold: float = 0.03) -> dict:
    """Ejecuta el motor sobre un partido de la BD y devuelve el dict de predicción."""
    home = TeamForm(
        name=match.home_team.name,
        attack=match.home_team.attack,
        defense=match.home_team.defense,
        elo=match.home_team.elo,
        xg_for=match.home_team.xg_for,
        xg_against=match.home_team.xg_against,
        recent_points=match.home_team.recent_points,
    )
    away = TeamForm(
        name=match.away_team.name,
        attack=match.away_team.attack,
        defense=match.away_team.defense,
        elo=match.away_team.elo,
        xg_for=match.away_team.xg_for,
        xg_against=match.away_team.xg_against,
        recent_points=match.away_team.recent_points,
    )
    prediction = predict_match(
        home,
        away,
        odds=_odds_dict(match) or None,
        league_avg_goals=match.league.avg_goals,
        edge_threshold=edge_threshold,
    )
    out = prediction.as_dict()
    out["match_id"] = match.id
    return out
