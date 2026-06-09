"""Cliente de TheSportsDB (thesportsdb.com).

Fuente gratuita para catálogos de ligas, equipos y próximos eventos. Útil como
respaldo y para metadatos. Clave pública de pruebas: "3".
"""
from __future__ import annotations

from datetime import datetime

from .base import BaseProviderClient
from .schemas import NormalizedMatch


class TheSportsDbClient(BaseProviderClient):
    base_url = "https://www.thesportsdb.com/api/v1/json"

    def __init__(self, api_key: str = "3", timeout: float = 10.0) -> None:
        super().__init__(api_key or "3", timeout)

    @property
    def enabled(self) -> bool:
        # TheSportsDB siempre tiene una clave pública ("3").
        from .base import httpx

        return httpx is not None

    def next_events(self, league_id: int) -> list[NormalizedMatch]:
        """Próximos 15 eventos de una liga."""
        if not self.enabled:
            return []
        data = self._get(f"/{self.api_key}/eventsnextleague.php", {"id": league_id})
        if not data:
            return []
        out: list[NormalizedMatch] = []
        for ev in data.get("events") or []:
            out.append(
                NormalizedMatch(
                    provider="thesportsdb",
                    external_id=str(ev.get("idEvent", "")),
                    league=ev.get("strLeague", ""),
                    sport=(ev.get("strSport", "Soccer") or "Soccer").lower().replace("soccer", "football"),
                    home=ev.get("strHomeTeam", ""),
                    away=ev.get("strAwayTeam", ""),
                    kickoff=_parse_dt(ev.get("dateEvent"), ev.get("strTime")),
                    status="scheduled",
                )
            )
        return out


def _parse_dt(date: str | None, time: str | None) -> datetime:
    if not date:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(f"{date}T{(time or '00:00:00')[:8]}")
    except ValueError:
        return datetime.utcnow()
