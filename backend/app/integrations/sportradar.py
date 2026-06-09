"""Cliente de Sportradar (acceso premium con licencia).

Implementa el patrón de acceso a sus "sport event schedules". Requiere clave
con licencia; degrada con elegancia si no está configurada.
"""
from __future__ import annotations

from datetime import datetime

from .base import BaseProviderClient
from .schemas import NormalizedMatch


class SportradarClient(BaseProviderClient):
    # Endpoint de ejemplo (soccer, trial v4). Ajustar según licencia.
    base_url = "https://api.sportradar.com/soccer/trial/v4/en"

    def daily_schedule(self, date: str) -> list[NormalizedMatch]:
        """Calendario de un día (YYYY-MM-DD)."""
        if not self.enabled:
            return []
        data = self._get(f"/schedules/{date}/schedule.json", {"api_key": self.api_key})
        if not data:
            return []
        out: list[NormalizedMatch] = []
        for ev in data.get("sport_events", []):
            competitors = ev.get("competitors", [])
            home = next((c["name"] for c in competitors if c.get("qualifier") == "home"), "")
            away = next((c["name"] for c in competitors if c.get("qualifier") == "away"), "")
            out.append(
                NormalizedMatch(
                    provider="sportradar",
                    external_id=str(ev.get("id", "")),
                    league=ev.get("sport_event_context", {}).get("competition", {}).get("name", ""),
                    sport="football",
                    home=home,
                    away=away,
                    kickoff=_parse_dt(ev.get("start_time")),
                    status="scheduled",
                )
            )
        return out


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.utcnow()
