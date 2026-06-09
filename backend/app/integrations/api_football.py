"""Cliente de API-Football (api-sports.io).

Devuelve fixtures y estadísticas de equipos normalizados al modelo interno
(`NormalizedMatch`, `NormalizedTeam`).
"""
from __future__ import annotations

from datetime import datetime

from .base import BaseProviderClient
from .schemas import NormalizedMatch, NormalizedTeam


class ApiFootballClient(BaseProviderClient):
    base_url = "https://v3.football.api-sports.io"

    def _headers(self) -> dict[str, str]:
        return {"x-apisports-key": self.api_key}

    def get_fixtures(self, league_id: int, season: int, date: str | None = None) -> list[NormalizedMatch]:
        """Partidos de una liga/temporada (opcionalmente de una fecha YYYY-MM-DD)."""
        if not self.enabled:
            return []
        params = {"league": league_id, "season": season}
        if date:
            params["date"] = date
        data = self._get("/fixtures", params)
        if not data:
            return []
        out: list[NormalizedMatch] = []
        for item in data.get("response", []):
            fx = item.get("fixture", {})
            teams = item.get("teams", {})
            league = item.get("league", {})
            goals = item.get("goals", {})
            out.append(
                NormalizedMatch(
                    provider="api_football",
                    external_id=str(fx.get("id", "")),
                    league=league.get("name", ""),
                    sport="football",
                    home=teams.get("home", {}).get("name", ""),
                    away=teams.get("away", {}).get("name", ""),
                    kickoff=_parse_dt(fx.get("date")),
                    status=_map_status(fx.get("status", {}).get("short", "NS")),
                    home_score=goals.get("home"),
                    away_score=goals.get("away"),
                )
            )
        return out

    def get_team_statistics(self, league_id: int, season: int, team_id: int) -> NormalizedTeam | None:
        """Estadísticas agregadas de un equipo (para derivar ataque/defensa/xG)."""
        if not self.enabled:
            return None
        data = self._get("/teams/statistics", {"league": league_id, "season": season, "team": team_id})
        if not data:
            return None
        resp = data.get("response", {})
        goals = resp.get("goals", {})
        gf = _safe_float(goals.get("for", {}).get("average", {}).get("total"))
        ga = _safe_float(goals.get("against", {}).get("average", {}).get("total"))
        return NormalizedTeam(
            provider="api_football",
            external_id=str(team_id),
            name=resp.get("team", {}).get("name", ""),
            xg_for=gf or 1.4,
            xg_against=ga or 1.4,
            # ataque/defensa relativos respecto a media de liga (~1.35 goles)
            attack=(gf / 1.35) if gf else 1.0,
            defense=(ga / 1.35) if ga else 1.0,
        )


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.utcnow()


def _map_status(short: str) -> str:
    finished = {"FT", "AET", "PEN"}
    live = {"1H", "2H", "HT", "ET", "LIVE"}
    if short in finished:
        return "finished"
    if short in live:
        return "live"
    return "scheduled"


def _safe_float(value) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
