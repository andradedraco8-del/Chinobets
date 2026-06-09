"""Cliente de The Odds API (the-odds-api.com).

Recupera cuotas decimales de múltiples casas y calcula un consenso por mercado
(1X2, totales 2.5, BTTS), normalizado a `NormalizedOdds`.
"""
from __future__ import annotations

from statistics import median

from .base import BaseProviderClient
from .schemas import NormalizedOdds


class OddsApiClient(BaseProviderClient):
    base_url = "https://api.the-odds-api.com/v4"

    def get_odds(self, sport_key: str = "soccer_epl", regions: str = "eu") -> list[NormalizedOdds]:
        """Cuotas de los próximos eventos de un deporte/liga."""
        if not self.enabled:
            return []
        params = {
            "apiKey": self.api_key,
            "regions": regions,
            "markets": "h2h,totals",
            "oddsFormat": "decimal",
        }
        data = self._get(f"/sports/{sport_key}/odds", params)
        if not data:
            return []
        return [self._normalize_event(ev) for ev in data]

    def _normalize_event(self, ev: dict) -> NormalizedOdds:
        home_name = ev.get("home_team", "")
        away_name = ev.get("away_team", "")
        h_prices: list[float] = []
        d_prices: list[float] = []
        a_prices: list[float] = []
        over_prices: list[float] = []
        under_prices: list[float] = []

        for bk in ev.get("bookmakers", []):
            for market in bk.get("markets", []):
                key = market.get("key")
                outcomes = market.get("outcomes", [])
                if key == "h2h":
                    for o in outcomes:
                        name, price = o.get("name"), o.get("price")
                        if price is None:
                            continue
                        if name == home_name:
                            h_prices.append(price)
                        elif name == away_name:
                            a_prices.append(price)
                        else:  # "Draw"
                            d_prices.append(price)
                elif key == "totals":
                    for o in outcomes:
                        point = o.get("point")
                        price = o.get("price")
                        if point == 2.5 and price is not None:
                            if o.get("name") == "Over":
                                over_prices.append(price)
                            elif o.get("name") == "Under":
                                under_prices.append(price)

        return NormalizedOdds(
            provider="odds_api",
            external_id=str(ev.get("id", "")),
            home=_consensus(h_prices),
            draw=_consensus(d_prices),
            away=_consensus(a_prices),
            over_2_5=_consensus(over_prices),
            under_2_5=_consensus(under_prices),
            bookmaker="consensus",
        )


def _consensus(prices: list[float]) -> float | None:
    """Cuota de consenso = mediana de las casas (robusta frente a outliers)."""
    return round(median(prices), 3) if prices else None
