"""Cliente de The Odds API (the-odds-api.com).

The Odds API devuelve, en una sola llamada, el evento completo: equipos, hora de
inicio y cuotas de varias casas. Por eso aquí construimos directamente
`NormalizedMatch` con las cuotas de consenso (mediana) ya incorporadas.

Plan gratuito: https://the-odds-api.com/  (incluye ~500 peticiones/mes).
"""
from __future__ import annotations

from datetime import datetime
from statistics import median

from .base import BaseProviderClient
from .schemas import NormalizedMatch, NormalizedOdds


# Mapa de "sport_key" de The Odds API → deporte interno.
SPORT_PREFIX = {
    "soccer": "football",
    "basketball": "basketball",
    "tennis": "tennis",
    "baseball": "baseball",
    "americanfootball": "american_football",
    "icehockey": "ice_hockey",
}


def _sport_from_key(sport_key: str) -> str:
    prefix = sport_key.split("_", 1)[0]
    return SPORT_PREFIX.get(prefix, "football")


class OddsApiClient(BaseProviderClient):
    base_url = "https://api.the-odds-api.com/v4"

    def get_matches(self, sport_key: str = "soccer_epl", regions: str = "eu") -> list[NormalizedMatch]:
        """Próximos eventos (equipos + hora + cuotas) de un deporte/liga."""
        if not self.enabled:
            return []
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": "h2h,totals",
            "oddsFormat": "decimal",
        }
        data = self._get(f"/sports/{sport_key}/odds", params)
        if not isinstance(data, list):
            return []
        sport = _sport_from_key(sport_key)
        title = sport_key.replace("_", " ").title()
        return [self._normalize_event(ev, sport, title) for ev in data]

    def _normalize_event(self, ev: dict, sport: str, league_title: str) -> NormalizedMatch:
        home_name = ev.get("home_team", "")
        away_name = ev.get("away_team", "")
        h, d, a, over, under = [], [], [], [], []

        for bk in ev.get("bookmakers", []):
            for market in bk.get("markets", []):
                key = market.get("key")
                for o in market.get("outcomes", []):
                    name, price = o.get("name"), o.get("price")
                    if price is None:
                        continue
                    if key == "h2h":
                        if name == home_name:
                            h.append(price)
                        elif name == away_name:
                            a.append(price)
                        else:
                            d.append(price)
                    elif key == "totals" and o.get("point") == 2.5:
                        if name == "Over":
                            over.append(price)
                        elif name == "Under":
                            under.append(price)

        odds = NormalizedOdds(
            provider="odds_api",
            external_id=str(ev.get("id", "")),
            home=_consensus(h),
            draw=_consensus(d),
            away=_consensus(a),
            over_2_5=_consensus(over),
            under_2_5=_consensus(under),
            bookmaker="consensus",
        )
        return NormalizedMatch(
            provider="odds_api",
            external_id=str(ev.get("id", "")),
            league=ev.get("sport_title", league_title),
            sport=sport,
            home=home_name,
            away=away_name,
            kickoff=_parse_dt(ev.get("commence_time")),
            status="scheduled",
            odds=odds,
        )


def _consensus(prices: list[float]) -> float | None:
    return round(median(prices), 3) if prices else None


def _parse_dt(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow()
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
    except ValueError:
        return datetime.utcnow()
